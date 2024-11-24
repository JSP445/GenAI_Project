from bs4 import BeautifulSoup
import requests
import json
import re
import argparse
import time
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from random import uniform
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from ratelimit import limits, sleep_and_retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

@dataclass
class Question:
    """Data class to store question information"""
    tags: List[str]
    question: str
    question_link: str

class StackExchangeSites:
    """Class to represent Stack Exchange sites"""
    def __init__(self, base_url: str, host: str):
        self.base_url = base_url
        self.host = host

    @classmethod
    def stackoverflow(cls) -> 'StackExchangeSites':
        return cls(
            "https://stackoverflow.com/questions/tagged/",
            "https://stackoverflow.com"
        )
    
    @classmethod
    def devops(cls) -> 'StackExchangeSites':
        return cls(
            "https://devops.stackexchange.com/questions/tagged/",
            "https://devops.stackexchange.com"
        )
    
class StackExchangeScraper:
    """Main class to scrape Stack Exchange sites"""
    def __init__(self, site: StackExchangeSites, requests_per_minute: int=20):
        self.site = site
        self.requests_per_minute = requests_per_minute
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        })
    
    def build_url(self, tag: str, page: int, tab: str = "votes", pagesize: int = 50) -> str:
        """Build the URL for the given tag and page."""
        return f"{self.site.base_url}{tag}?tab={tab}&page={page}&pagesize={pagesize}"
    
    @sleep_and_retry
    @limits(calls=20, period=60)
    def get_page(self, url: str) -> BeautifulSoup:
        """Get the BeautifulSoup object for the given URL"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            logger.error("Error fetching page %s: %s", url, e)
            raise

    def extract_tags(self, tags_elements) -> List[str]:
        """Extract tags from the given BeautifulSoup object."""
        if not tags_elements:
            return []
        
        tag_pattern = re.compile('t-[a-zA-Z0-9_-]*')
        tags = []
        for tag_str in tags_elements.get('class', []):
            if tag_pattern.match(tag_str):
                tags.append(tag_str[2:])
        return tags
    
    def parse_question(self, summary) -> Optional[Question]:
        """Parse a single question summary"""
        try:
            if not summary.find("div", class_="s-post-summary--stats-item has-answers has-accepted-answer"):
                return None

            summary_content = summary.find("div", class_="s-post-summary--content")
            if not summary_content:
                return None

            tags_element = summary_content.find("div", class_=re.compile("s-post-summary--meta-tags[a-zA-Z ._-]*"))
            tags = self.extract_tags(tags_element)

            link_element = summary.find('a', href=True, string=True)
            if not link_element:
                return None

            return Question(
                tags=tags,
                question=link_element.text.strip(),
                question_link=f"{self.site.host}{link_element['href']}"
            )
        except Exception as e:
            logger.error(f"Error parsing question: {str(e)}")
            return None

    def scrape_page(self, tag: str, page: int) -> List[Question]:
        """Scrape a single page of questions"""
        url = self.build_url(tag=tag, page=page)
        logger.info(f"Scraping page {page} for tag '{tag}'")
        
        soup = self.get_page(url)
        questions = []
        
        questions_container = soup.find("div", id="questions")
        if not questions_container:
            return questions

        for summary in questions_container.find_all("div", id=re.compile("question-summary*")):
            question = self.parse_question(summary)
            if question:
                questions.append(question)

        return questions

    def scrape_tag(self, tag: str, start_page: int, num_pages: int, max_workers: int = 3) -> List[List[Question]]:
        """Scrape multiple pages concurrently with ThreadPoolExecutor"""
        all_questions = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_page = {
                executor.submit(self.scrape_page, tag, page): page
                for page in range(start_page, start_page + num_pages)
            }
            
            for future in as_completed(future_to_page):
                page = future_to_page[future]
                try:
                    questions = future.result()
                    all_questions.append(questions)
                    if not questions:
                        logger.warning(f"No questions found on page {page}")
                        break
                except Exception as e:
                    logger.error(f"Error processing page {page}: {str(e)}")

        return all_questions

def export_data(questions: List[List[Question]], tag: str, start: int, pages: int) -> None:
    """Export scraped data to JSON file"""
    output_dir = Path("output_json")
    output_dir.mkdir(exist_ok=True)
    
    filename = output_dir / f"questions-{tag}_pg{start}-{start+pages-1}.json"
    
    # Convert Questions to dictionaries
    data = [[asdict(q) for q in page] for page in questions]
    q_collection = {tag: data}
    
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(q_collection, f, indent=4, ensure_ascii=False)
    logger.info(f"Data exported to {filename}")

def init_argparse() -> argparse.ArgumentParser:
    """Initialise argument parser with improved help messages"""
    parser = argparse.ArgumentParser(
        description="Scrape Stack Exchange questions with specific tags",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument("-t", "--tagged", 
                       required=True,
                       help="Tag to search questions for")
    parser.add_argument("-s", "--startpage",
                       type=int,
                       default=1,
                       help="Starting page number")
    parser.add_argument("-p", "--pages",
                       type=int,
                       default=1,
                       help="Number of pages to scrape")
    parser.add_argument("--site",
                       choices=["stackoverflow", "devops"],
                       default="stackoverflow",
                       help="Stack Exchange site to scrape")
    
    return parser

def main():
    parser = init_argparse()
    args = parser.parse_args()
    
    # Select site based on argument
    site = (StackExchangeSites.stackoverflow() if args.site == "stackoverflow" 
            else StackExchangeSites.devops())
    
    scraper = StackExchangeScraper(site)
    
    try:
        questions = scraper.scrape_tag(
            tag=args.tagged,
            start_page=args.startpage,
            num_pages=args.pages
        )
        export_data(questions, args.tagged, args.startpage, args.pages)
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
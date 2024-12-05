import streamlit as st
import subprocess
import sys
from parsers import crawler, pdfreader

def main():
    """Page configuration"""
    st.set_page_config(
        page_title="Odyssey",
        page_icon=":rocket:",
    )
    
    st.title("Odyssey 🚀")
    
    col1, col2, col3 = st.columns(3)
    
    # Web Crawler
    with col1:
        st.markdown("### Web Crawler 🌐")
        # Input for tag
        tag = st.text_input("Enter Tag to Crawl", key="crawl_tag")
        
        # Input for pages
        pages = st.number_input("Number of Pages", min_value=1, max_value=10, value=1, key="crawl_pages")
        
        # Site selection
        site = st.selectbox("Select Site", ["stackoverflow", "devops-stackexchange"], key="crawl_site")
        
        # Web Crawl Button
        web_crawl_button = st.button("Start Web Crawl", key="web_crawl", use_container_width=True)

    # PDF Reader
    with col2:
        st.markdown("### PDF Reader 📄")
        pdf_upload_button = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_upload", label_visibility="visible")
        
        # If a PDF is uploaded, run the PDF analysis page
        if pdf_upload_button is not None:
            pdfreader.run(pdf_upload_button)

    # Image uploader
    with col3:
        st.markdown("### Image Uploader 📷")
        image_upload_button = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], key="image_upload", label_visibility="visible")

    # Web Crawl Functionality
    if web_crawl_button:
        if not tag:
            st.error("Please enter a tag to crawl")
        else:
            try:
                # Prepare arguments for crawler
                crawler_args = [
                    "-t", tag,
                    "-p", str(pages),
                    "--site", site
                ]
                
                # Run the crawler
                crawler.main(crawler_args)
                
                st.success(f"Web crawl completed for {tag} on {site}")
                
                # Show output files
                st.markdown("### Output Files")
                import os
                output_dir = "output_json"
                if os.path.exists(output_dir):
                    files = os.listdir(output_dir)
                    for file in files:
                        if file.startswith(f"questions-{tag}_"):
                            st.write(f"✅ {file}")
            
            except Exception as e:
                st.error(f"Error during web crawl: {str(e)}")

    # Display uploaded file details
    if pdf_upload_button is not None:
        st.success(f"PDF Uploaded: {pdf_upload_button.name}")
    
    if image_upload_button is not None:
        st.success(f"Image Uploaded: {image_upload_button.name}")
    
    if web_crawl_button:
        st.info("Web crawl initiated")

if __name__ == "__main__":
    main()
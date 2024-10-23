from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import JsonOutputParser
from langchain import hub
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from typing_extensions import TypedDict
from typing import List
from langchain.schema import Document
from langgraph.graph import END, StateGraph
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader
import streamlit as st
import os

llm = "llama3"
tavily_api_key = os.environ['TAVILY_API_KEY'] = 'API_KEY'
st.title("Multi-PDF ChatBot using LLAMA3 MODELS & Adaptive RAG")
user_input = st.text_input("Question:", placeholder="Ask about your PDF", key='input')

with st.sidebar:
    uploaded_files = st.file_uploader("Upload your file", type=['pdf'], accept_multiple_files=True)
    process = st.button("Process")
if process:
    if not uploaded_files:
        st.warning("Please upload at least one PDF file.")
        st.stop()

# Ensures the temp directory exists
temp_dir = 'C:/temp/'
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

# Process each uploaded file
for uploaded_file in uploaded_files:
    temp_file_path = os.path.join(temp_dir, uploaded_file.name)
    
    # Save the file to disk
    with open(temp_file_path, "wb") as file:
        file.write(uploaded_file.getbuffer()) 
    
    # Load the PDF using PyPDFLoader
    try:
        loader = PyPDFLoader(temp_file_path)
        data = loader.load() 
        st.write(f"Data loaded for {uploaded_file.name}")
    except Exception as e:
        st.error(f"Failed to load {uploaded_file.name}: {str(e)}")

text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=250, chunk_overlap=0
)
text_chunks = text_splitter.split_documents(data)

# Add to vectorDB
vectorstore = Chroma.from_documents(
    documents=text_chunks,
    collection_name="rag-chroma",
    embedding=GPT4AllEmbeddings(),
)
retriever = vectorstore.as_retriever()
llm = ChatOllama(model=local_llm, format="json", temperature=0)

prompt = PromptTemplate(
        template="""You are an expert at routing a user question to a vectorstore or web search. \n
        Use the vectorstore for questions on LLM  agents, prompt engineering, and adversarial attacks. \n
        You do not need to be stringent with the keywords in the question related to these topics. \n
        Otherwise, use web-search. Give a binary choice 'web_search' or 'vectorstore' based on the question. \n
        Return the a JSON with a single key 'datasource' and no premable or explaination. \n
        Question to route: {question}""",
        input_variables=["question"],
)

question_router = prompt | llm | JsonOutputParser()
question = "llm agent memory"
docs = retriever.get_relevant_documents(question)
doc_txt = docs[1].page_content
question_router.invoke({"question": question})
llm = ChatOllama(model=local_llm, format="json", temperature=0)

# Example of using PromptTemplate for grading relevance
grading_prompt = PromptTemplate(
    template="""You are an expert at determining document relevance. \n
    Given the question, evaluate if the document contains relevant keywords. \n
    Return a JSON with a single key 'score' and value 'yes' or 'no'. \n
    Question: {question} \n
    Document: {document}""",
    input_variables=["question", "document"],
)

# Sample question and document for evaluation
question = "What are the capabilities of LLM's agent memory?"
document = doc_txt

# Create a grading pipeline
grader = grading_prompt | llm | JsonOutputParser()
grading_result = grader.invoke({"question": question, "document": document})
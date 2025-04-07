import os
import sys
import sqlite3
from src.exception import CustomException
from src.logger import logger
import fitz
from src.processing_db.vectordb_setup import search_documents

def search_similar_documents(query):
    """
    Returns:
        list: Top k similar documents
    """
    try:
        results = search_documents(query)
        logger.info(f"Response has been retrieved")
        return results
    except Exception as e:
        logger.error(f"Error searching documents in Pinecone database: {str(e)}")
        raise CustomException(e, sys)

def display_results(results):
    """Display search results"""
    print(f"Found {len(results)} relevant documents:")
    for i, doc in enumerate(results):
        print(f"  {i+1}. {doc.page_content}")
        print(f"     Metadata: {doc.metadata}")

def read_pdf_to_string(path,start = 0):
    """
    Returns:
        str: The concatenated text content of all pages in the PDF document.
    """
    doc = fitz.open(path)
    content = ""
    for page_num in range(start,len(doc)):
        page = doc[page_num]
        content += page.get_text()
    return content

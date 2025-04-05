import os
import sys
from src.processing_db.vectordb_setup import initialize_pinecone, search_documents
from src.exception import CustomException
from src.logger import logger 

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "senor-rag"

initialize_pinecone()

def search_similar_documents(query):
    """
    Search for documents similar to the query.
    
    Args:
        query (str): The search query
        initial_k (int): Number of results to search
        final_k (int): Number of results to rerank and return
    
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
    """Display search results in a formatted way."""
    print(f"Found {len(results)} relevant documents:")
    for i, doc in enumerate(results):
        print(f"  {i+1}. {doc.page_content}")
        print(f"     Metadata: {doc.metadata}")



if __name__ == "__main__":
    try:
        query = "consumer protection app"
        results = search_similar_documents(query)
        display_results(results)
        
    except CustomException as e:
        print(f"An error occurred: {e}")
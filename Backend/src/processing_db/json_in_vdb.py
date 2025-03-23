import os
import sys
import json
from langchain.schema import Document
from vectordb_setup import initialize_pinecone, create_vector_store, search_documents
from exception import CustomException
from logger import logger 

def process_json_data(json_data):
    """
    Process JSON data into Document objects for Pinecone.
    
    Args:
        json_data (dict or list): JSON data to process
        
    Returns:
        list: List of Document objects with page_content and metadata
    """
    try:
        documents = []
        json_items = [json_data] if isinstance(json_data, dict) else json_data
        
        for item in json_items:
            if 'description' in item:
                page_content = item['description']
                
                # Skip if page_content is None
                if page_content is None:
                    logger.warning(f"Skipping item with None description: {item.get('title', 'unknown')}")
                    continue
                
                # Ensure page_content is a string
                page_content = str(page_content)
                
                # Create metadata from all other fields
                metadata = {}
                for k, v in item.items():
                    if k != 'description':
                        metadata[k] = str(v) if v is not None else ""
                
                document = Document(page_content=page_content, metadata=metadata)
                documents.append(document)
            else:
                logger.warning(f"No 'description' field found in item: {item.get('title', 'unknown')}")
        
        logger.info(f"Created {len(documents)} documents from JSON data")
        return documents
    
    except Exception as e:
        logger.error(f"Error processing JSON data: {str(e)}")
        raise CustomException(e, sys)

def load_json_from_file(file_path):
    """
    Load JSON data from a file.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        dict or list: The JSON data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        logger.info(f"Loaded JSON data from {file_path}")
        return data
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {str(e)}")
        raise CustomException(e, sys)

def upsert_json_data(json_data=None, json_file=None):
    """
    Upsert JSON data to the vector database.
    
    Args:
        json_data (dict or list, optional): JSON data to upsert directly
        json_file (str, optional): Path to JSON file to load and upsert
        
    Returns:
        PineconeVectorStore: The vector store
    """
    try:
        # Load JSON from file if json_data not provided
        if json_data is None and json_file is not None:
            json_data = load_json_from_file(json_file)
        
        if json_data is None:
            logger.error("No JSON data provided")
            raise ValueError("Either json_data or json_file must be provided")
        
        documents = process_json_data(json_data)
        
        # Ensure we have documents to upsert
        if not documents:
            logger.warning("No valid documents found to upsert")
            return None
            
        initialize_pinecone()
        vector_store = create_vector_store(documents)
        
        logger.info(f"Upserted {len(documents)} documents to vector store.")
        return vector_store
    
    except Exception as e:
        logger.error(f"Error upserting JSON data into Pinecone database: {str(e)}")
        raise CustomException(e, sys)

def search_similar_documents(query):
    """
    Search for documents similar to the query.
    
    Args:
        query (str): The search query
        top_k (int): Number of results to return
    
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
        json_file_path = r"data source\constitution_of_india.json" 
        vector_store = upsert_json_data(json_file=json_file_path)
        
        query = "What is the preamble of the Indian Constitution?"
        results = search_similar_documents(query)
        display_results(results)
        
    except CustomException as e:
        print(f"An error occurred: {e}")
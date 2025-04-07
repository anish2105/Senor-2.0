import sys
import json
from langchain.schema import Document
from src.processing_db.vectordb_setup import initialize_pinecone, create_vector_store, search_documents
from src.exception import CustomException
from src.logger import logger 
from src.utils import search_similar_documents, display_results

def process_json_data(json_data):
    """
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


if __name__ == "__main__":
    try:
        json_file_path = r"data source\constitution_of_india.json" 
        vector_store = upsert_json_data(json_file=json_file_path)
        
        query = "What is the preamble of the Indian Constitution?"
        results = search_similar_documents(query)
        display_results(results)
        
    except CustomException as e:
        print(f"An error occurred: {e}")
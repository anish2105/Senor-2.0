import sys
from langchain.schema import Document
from vectordb_setup import initialize_pinecone, create_vector_store, search_documents
from exception import CustomException
from logger import logger 
from db_reader import db_manager

def extract_documents_from_table(table_name, limit=100):
    """
    Extract documents from a database table where columns with 'desc' in the name become
    the page_content and all other columns become metadata.
    
    Args:
        table_name (str): Name of the table to extract data from
        limit (int): Maximum number of rows to extract
        
    Returns:
        list: List of Document objects with page_content and metadata
    """
    try:
        # Get the data from the table
        table_data = db_manager.fetch_table_data(table_name, limit=limit)
        logger.info(f"Extracted {len(table_data)} rows from table '{table_name}'")
        
        documents = []
        for row in table_data:
            # Find the column with 'desc' in the name
            desc_column = None
            for column in row.keys():
                if 'desc' in column.lower():
                    desc_column = column
                    break
            
            if desc_column is None:
                logger.warning(f"No description column found in table '{table_name}', skipping row")
                continue
            
            page_content = row[desc_column]
            
            if page_content is None:
                logger.warning(f"Skipping row with None description in table '{table_name}'")
                continue
                
            page_content = str(page_content) if page_content is not None else ""
            
            metadata = {}
            for k, v in row.items():
                if k != desc_column:
                    metadata[k] = str(v) if v is not None else ""
            
            metadata['source_table'] = table_name
            
            document = Document(page_content=page_content, metadata=metadata)
            documents.append(document)
        
        logger.info(f"Created {len(documents)} documents from table '{table_name}'")
        return documents
    
    except Exception as e:
        logger.error(f"Error extracting documents from table '{table_name}': {str(e)}")
        raise CustomException(e, sys)

def process_all_tables(tables=None, limit_per_table=100):
    """
    Process all tables or specified tables and create documents.
    
    Args:
        tables (list, optional): List of table names to process. If None, process all tables.
        limit_per_table (int): Maximum number of rows to extract per table
        
    Returns:
        list: Combined list of Document objects from all processed tables
    """
    try:
        if tables is None:
            tables = db_manager.get_all_tables()
        
        all_documents = []
        for table in tables:
            table_docs = extract_documents_from_table(table, limit=limit_per_table)
            all_documents.extend(table_docs)
        
        logger.info(f"Processed {len(tables)} tables, extracted {len(all_documents)} documents total")
        return all_documents
    
    except Exception as e:
        logger.error(f"Error processing tables: {str(e)}")
        raise CustomException(e, sys)

def upsert_data(docs=None, metadata_list=None, tables=None, limit_per_table=100):
    """
    Upsert documents to the vector database.
    If docs is provided, use those directly.
    If docs is None, extract documents from the database tables.
    
    Args:
        docs (list, optional): List of text documents
        metadata_list (list, optional): List of metadata dicts for each document
        tables (list, optional): List of table names to process if docs is None
        limit_per_table (int): Maximum number of rows to extract per table
    """
    try:
        documents = []
        
        if docs is not None:
            if metadata_list is None:
                metadata_list = [{"id": str(i), "source": "manual"} for i in range(len(docs))]
            
            processed_docs = [str(doc) if doc is not None else "" for doc in docs]
            
            processed_metadata = []
            for meta in metadata_list:
                processed_meta = {}
                for k, v in meta.items():
                    processed_meta[k] = str(v) if v is not None else ""
                processed_metadata.append(processed_meta)
            
            documents = [
                Document(page_content=doc, metadata=meta)
                for doc, meta in zip(processed_docs, processed_metadata)
            ]
        else:
            documents = process_all_tables(tables, limit_per_table)
        
        if not documents:
            logger.warning("No valid documents found to upsert")
            return None
            
        initialize_pinecone()
        vector_store = create_vector_store(documents)
        
        logger.info(f"Upserted {len(documents)} documents to vector store.")
        return vector_store
    
    except Exception as e:
        logger.error(f"Error upserting documents into Pinecone database: {str(e)}")
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
        # Process all tables and upsert to vector store
        vector_store = upsert_data(tables=None, limit_per_table=999999)
        
        query = "What is the procedure for filing a civil case?"
        results = search_similar_documents(query)
        display_results(results)
        
    except CustomException as e:
        print(f"An error occurred: {e}")
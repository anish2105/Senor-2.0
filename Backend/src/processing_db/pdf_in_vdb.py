"""
PDF Embedding and Semantic Chunking Pipeline

This script reads a PDF file, applies semantic chunking using LangChain's SemanticChunker
with Gemini embeddings, and upserts the chunks into a Pinecone vector store.

Breakpoints used:
- Type: 'percentile'
- Threshold: 90th percentile
"""

import os
import sys
from dotenv import load_dotenv

from langchain_experimental.text_splitter import SemanticChunker
from src.utils import search_similar_documents, display_results, read_pdf_to_string
from src.logger import logger
from src.exception import CustomException
from src.processing_db.gemini_embed import gemini_embeddings
from src.processing_db.vectordb_setup import (
    initialize_pinecone,
    create_vector_store,
)

load_dotenv()

def process_pdf_to_documents(pdf_path: str):
    """
    Returns:
        list: LangChain Document objects.
    """
    try:
        # Start extracting the content of PDF from 3rd page, default is set to 0 
        content = read_pdf_to_string(pdf_path,3)
        if not content.strip():
            raise ValueError(f"No content extracted from PDF: {pdf_path}")

        chunker = SemanticChunker(
            gemini_embeddings,
            breakpoint_threshold_type='percentile',
            breakpoint_threshold_amount=90,
        )

        documents = chunker.create_documents([content])
        logger.info(f"Created {len(documents)} semantic chunks from PDF.")
        return documents

    except Exception as e:
        logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
        raise CustomException(e, sys)

def upsert_pdf_data(pdf_path: str):
    """ 
    Returns:
        PineconeVectorStore: The vector store instance.
    """
    try:
        documents = process_pdf_to_documents(pdf_path)

        initialize_pinecone()
        vector_store = create_vector_store(documents)

        logger.info(f"Upserted {len(documents)} PDF chunks into Pinecone.")
        return vector_store

    except Exception as e:
        logger.error(f"Failed to upsert PDF data: {str(e)}")
        raise CustomException(e, sys)


if __name__ == "__main__":
    try:
        pdf_file_path = r"data source\consumer_act.pdf"
        vector_store = upsert_pdf_data(pdf_path=pdf_file_path)
        query = "what happens to sellers when the product is defective"
        results = search_similar_documents(query)
        display_results(results)

    except CustomException as e:
        print(f"Error: {e}")
        logger.error(e)
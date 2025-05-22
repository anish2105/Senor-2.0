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
from langchain.schema import Document
from langchain_experimental.text_splitter import SemanticChunker
from src.utils import search_similar_documents, display_results, read_pdf_to_string
from src.logger import logger
from src.exception import CustomException
from src.processing_db.gemini_embed import gemini_embeddings
from src.processing_db.vectordb_setup import (
    initialize_pinecone,
    create_vector_store,
)
from langchain.text_splitter import TokenTextSplitter
from src.utils import get_token_count

MAX_TOKENS = 900
load_dotenv()

def split_longer_chunks(documents, max_tokens=MAX_TOKENS):
    """Splits documents if they exceed max_tokens."""
    token_splitter = TokenTextSplitter(chunk_size=max_tokens, chunk_overlap=50)

    final_docs = []
    for doc in documents:
        text = doc.page_content
        token_count = get_token_count(text)

        if token_count <= max_tokens:
            final_docs.append(doc)
        else:
            smaller_chunks = token_splitter.create_documents([text])
            final_docs.extend(smaller_chunks)

    return final_docs

def process_pdf(pdf_path: str):
    content = read_pdf_to_string(pdf_path, 3)
    if not content.strip():
        raise ValueError(f"No content extracted from PDF: {pdf_path}")

    chunker = SemanticChunker(
        gemini_embeddings,
        breakpoint_threshold_type='percentile',
        breakpoint_threshold_amount=90,
    )
    semantic_chunks = chunker.create_documents([content])
    print(f"Created {len(semantic_chunks)} semantic chunks from PDF.")
    final_documents = split_longer_chunks(semantic_chunks)
    print(f"After token splitting, total chunks: {len(final_documents)}")

    document_objects = [
        Document(
            page_content=chunk.page_content,
            metadata={"source": "consumer_act_pdf"}  
        )
        for chunk in final_documents
    ]

    return document_objects

def upsert_pdf_data(pdf_path: str):
    """ 
    Returns:
        PineconeVectorStore: The vector store instance.
    """
    documents = process_pdf(pdf_path)

    initialize_pinecone()
    vector_store = create_vector_store(documents)

    print(f"Upserted {len(documents)} PDF chunks into Pinecone.")
    return vector_store


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
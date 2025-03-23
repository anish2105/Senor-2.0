import os
import sys
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from processing_db.embeddings import embeddings
from processing_db.vectordb_setup import initialize_pinecone, search_documents
from exception import CustomException
from logger import logger

# FastAPI app
app = FastAPI(title="Pinecone RAG API", version="1.0")

# Pinecone once to optimize performance
try:
    pinecone_client = initialize_pinecone()
    logger.info("Pinecone initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Pinecone: {str(e)}")
    sys.exit(1)  


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


@app.post("/search")
async def search_similar_documents(request: SearchRequest):
    """
    Search for documents similar to the query using Pinecone.
    
    Args:
        request (SearchRequest): Query string and top_k results
    
    Returns:
        List of relevant documents
    """
    try:
        results = search_documents(request.query, initial_k=request.top_k)
        logger.info(f"Retrieved {len(results)} documents for query: {request.query}")

        if not results:
            return {"message": "No relevant documents found"}

        return [
            {
                "rank": i + 1,
                "content": doc.page_content,
                "metadata": doc.metadata,
            }
            for i, doc in enumerate(results)
        ]
    
    except CustomException as e:
        logger.error(f"Error searching documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Error searching documents")


@app.get("/")
async def root():
    """Health Check API"""
    return {"message": "Pinecone RAG API is running!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

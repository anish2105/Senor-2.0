import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.processing_db.vectordb_setup import initialize_pinecone, search_documents
from src.exception import CustomException
from src.logger import logger
from src.utils import *

app = FastAPI(title="Pinecone RAG API", version="1.0")

try:
    pinecone_client = initialize_pinecone()
    logger.info("Pinecone initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize Pinecone: {str(e)}")
    sys.exit(1)


# Request Model for retreiving user's query
class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


@app.post("/search")
async def search_similar_documents(request: SearchRequest):
    """
        list: Top-k matched documents with metadata.
    """
    try:
        results = search_documents(request.query, initial_k=request.top_k)
        logger.info(f"Retrieved {len(results)} documents for query: '{request.query}'")

        if not results:
            return {"message": "No relevant documents found"}

        return [
            {
                "rank": i + 1,
                "content": doc.page_content.strip(),  
                "metadata": doc.metadata,
            }
            for i, doc in enumerate(results)
        ]

    except CustomException as e:
        logger.error(f"For query :'{request.query}', Error during search : {str(e)}")
        raise HTTPException(status_code=500, detail="Error during document search")





@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Pinecone RAG API is running 🚀"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
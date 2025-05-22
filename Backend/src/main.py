import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.processing_db.vectordb_setup import initialize_pinecone, search_documents
from src.exception import CustomException
from src.logger import logger
from src.utils import *
from LLM_setup.LLM_call import generate_chatbot_response, parse_gemini_response
from src.chat_history_manager import chat_history_manager

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
    top_k: int = 6


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


# Chatbot endpoint
class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat_with_legal_bot(request: ChatRequest):
    """
    Accepts a legal query, runs LLM, and returns parsed answer + inner monologue.
    """
    try:
        response = generate_chatbot_response(request.query)
        parsed = parse_gemini_response(response)

        # Return tokens, metadata
        return {
            "query": request.query,
            "inner_monologue": parsed["inner_monologue"],
            "answer": parsed["answer"]
        }

    except CustomException as e:
        logger.error(f"Error while generating response for query: {request.query} | {str(e)}")
        raise HTTPException(status_code=500, detail="Error during chatbot response generation")


@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Pinecone RAG API is running 🚀"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
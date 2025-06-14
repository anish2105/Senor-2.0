import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.processing_db.vectordb_setup import initialize_pinecone, search_documents
from src.exception import CustomException
from src.logger import logger
from src.utils import *
from LLM_setup.llm_call import generate_chatbot_response, parse_gemini_response, extract_token_usage, evaluate_llm_output

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
    Accepts a legal query, runs LLM, and returns parsed answer + inner monologue + token info + evaluation.
    """
    try:
        relevant_chunks, response = generate_chatbot_response(request.query)
        parsed = parse_gemini_response(response)
        token_info = extract_token_usage(response)

        eval_scores = evaluate_llm_output(
            query=request.query,
            context=relevant_chunks,
            llm_answer=parsed["answer"]
        )

        logger.info(f"Evaluation results for query: {request.query} => {eval_scores}")

        return {
            "query": request.query,
            "inner_monologue": parsed["inner_monologue"],
            "answer": parsed["answer"],
            "Input tokens": token_info["input_tokens"],
            "Output tokens": token_info["output_tokens"],
            "Total tokens": token_info["total_tokens"],
            "Relevant chunks": relevant_chunks,
            "Evaluation scores": eval_scores
        }

    except CustomException as e:
        logger.error(f"Error while generating response for query: {request.query} | {str(e)}")
        raise HTTPException(status_code=500, detail="Error during chatbot response generation")

# Evaluation Request Model
class EvaluationRequest(BaseModel):
    query: str
    llm_answer: str
    context: str

@app.post("/evaluate")
async def evaluate_response(request: EvaluationRequest):
    """
    Evaluate the chatbot's answer for a given query and context.
    """
    try:
        scores = evaluate_llm_output(request.query, request.context, request.llm_answer)
        return {
            "query": request.query,
            "evaluation_scores": scores
        }
    except CustomException as e:
        logger.error(f"Evaluation failed for query: {request.query} | {str(e)}")
        raise HTTPException(status_code=500, detail="Evaluation error")


@app.get("/")
async def health_check():
    return {"status": "ok", "message": "RAG API is running"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
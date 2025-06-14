from ragas.metrics import ResponseRelevancy, Faithfulness, LLMContextPrecisionWithoutReference
from ragas import evaluate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings.base import LangchainEmbeddingsWrapper
from datasets import Dataset
import os
import time
from dotenv import load_dotenv
from src.logger import logger

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")


def evaluate_llm_response(user_prompt, context_docs, llm_answer):
    gemini_llm = ChatGoogleGenerativeAI(
        model='gemini-1.5-flash',
        temperature=0.1,
        google_api_key=google_api_key,
        max_retries=3,
        request_timeout=60,
        max_tokens_per_minute=30000,
        max_requests_per_minute=15
    )

    gemini_embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=google_api_key,
        task_type="retrieval_document"
    )

    evaluator_llm = LangchainLLMWrapper(gemini_llm)
    evaluator_embeddings = LangchainEmbeddingsWrapper(gemini_embeddings)

    sample_data = {
        "user_input": user_prompt,
        "retrieved_contexts": context_docs,
        "response": llm_answer
    }

    evaluation_data = Dataset.from_list([sample_data])

    metrics = [
        Faithfulness(llm=evaluator_llm),
        ResponseRelevancy(llm=evaluator_llm, embeddings=evaluator_embeddings),
        LLMContextPrecisionWithoutReference(llm=evaluator_llm)
    ]

    try:
        results = evaluate(
            dataset=evaluation_data,
            metrics=metrics,
            llm=evaluator_llm,
            embeddings=evaluator_embeddings,
            raise_exceptions=False
        )
        return results
    except Exception as retry_error:
        logger.error(f"Evaluation failed: {retry_error}")
        return None


def evaluate_with_backoff( user_prompt, context_docs, llm_answer, max_retries=3):
    for attempt in range(max_retries):
        try:
            logger.info(f"Evaluation attempt {attempt + 1}/{max_retries}")
            results = evaluate_llm_response(user_prompt, context_docs, llm_answer)
            if results is not None:
                return results
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                wait_time = (2 ** attempt) * 10
                logger.warning(f"Rate limited. Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                logger.error(f"Non-rate-limit error during evaluation: {e}")
                break
    return None


def run_llm_evaluation( user_prompt, context_text, llm_answer):
    """
    Wrapper to be called from chatbot: evaluates LLM output using RAGAS metrics.
    """
    # RAGAS expects context as a list of documents
    context_docs = context_text.split("\n\n") if isinstance(context_text, str) else context_text
    scores = evaluate_with_backoff( user_prompt, context_docs, llm_answer)

    if scores is not None:
        try:
            results_dict = scores.to_pandas().iloc[0].to_dict()
            formatted = {
                "Faithfulness": round(results_dict.get("faithfulness", 0.0), 4),
                "Response Relevancy": round(results_dict.get("response_relevancy", 0.0), 4),
                "Context_precision": round(results_dict.get("llm_context_precision_without_reference", 0.0), 4)
            }
            logger.info(f"LLM evaluation scores: {formatted}")
            return formatted
        except Exception as e:
            logger.error(f"Error formatting evaluation results: {e}")
            return None
    else:
        logger.warning("Evaluation failed after retries.")
        return None

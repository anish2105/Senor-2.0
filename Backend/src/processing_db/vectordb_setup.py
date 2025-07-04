import os
import sys
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from src.processing_db.gemini_embed import gemini_embeddings
from src.exception import CustomException
from src.logger import logger

load_dotenv()

# Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "senor-2"

def initialize_pinecone():
    """Initialize Pinecone client and create index if it doesn't exist."""
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Check if index exists, create if it doesn't
        if INDEX_NAME not in [index.name for index in pc.list_indexes()]:
            pc.create_index(
                name=INDEX_NAME,
                dimension=768,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            
        logger.info("Pinecone has been initialized")
        return pc
        
    except Exception as e:
        logger.error(f"Error creating Pinecone database: {str(e)}")
        raise CustomException(e, sys)

def create_vector_store(documents=None):
    """Get or create a vector store."""
    try:
        pc = initialize_pinecone()
        index = pc.Index(INDEX_NAME)
        
        vector_store = PineconeVectorStore(
            index=index,
            embedding=gemini_embeddings,
            text_key="text"
        )
        
        # If documents are provided, add them to the store
        if documents:
            vector_store.add_documents(documents)
            
        logger.info("Pinecone index has been initialized and documents have been inserted")
        return vector_store, pc
        
    except Exception as e:
        logger.error(f"Error inserting documents inside Pinecone index: {str(e)}")
        raise CustomException(e, sys)


# Rerank has been implemented, model = bge-reranker-v2-m3, retrieves 6 inital chunks and then re ranks the top 3
# Facing an error where re ranker doesnt work when token length of the retrieved documents is greater than 1024, hence a fallback mechanism has been implemented where if the error occurs than return first 3 retrieved documents
def search_documents(query, initial_k=6, final_k=3):
    """
    Search for documents similar to the query with re-ranking using Pinecone's native reranker.
    Fallback: If reranking fails (e.g., due to token limits), return top `final_k` from initial retrieval.
    """
    try:
        vector_store, pc = create_vector_store()
        
        retriever = vector_store.as_retriever(search_kwargs={"k": initial_k})
        initial_results = retriever.invoke(query)
        
        documents_for_reranking = [doc.page_content for doc in initial_results]

        try:
            rerank_results = pc.inference.rerank(
                model="bge-reranker-v2-m3",
                query=query,
                documents=documents_for_reranking,
                top_n=final_k,
                return_documents=True,
            )

            reranked_documents = []
            for reranked_item in rerank_results.data:
                reranked_text = reranked_item['document']['text']

                # Find the matching document in initial results
                for original_doc in initial_results:
                    if original_doc.page_content == reranked_text:
                        reranked_documents.append(original_doc)
                        break 

            logger.info(f"Successfully re-ranked {final_k} out of {initial_k} documents.")
            return reranked_documents

        except Exception as rerank_error:
            logger.warning(f"Reranker failed: {str(rerank_error)}. Falling back to initial retrieval.")
            return initial_results[:final_k]  # fallback: first N from initial results

    except Exception as e:
        logger.error(f"Error retrieving and re-ranking documents: {str(e)}")
        raise CustomException(e, sys)

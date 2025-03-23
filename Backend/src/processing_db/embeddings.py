import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_core.embeddings import Embeddings
from exception import CustomException
from logger import logger

load_dotenv()

# Gemini
API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=API_KEY)

class GeminiEmbeddings(Embeddings):
    
    def __init__(self, model_name="models/embedding-001"):
        self.model_name = model_name
        
    def embed_documents(self, texts):
        """Generate embeddings for documents."""
        results = []
        for text in texts:
            embedding_result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="RETRIEVAL_DOCUMENT"
            )
            results.append(embedding_result['embedding'])
        return results
    
    def embed_query(self, text):
        """Generate embedding for a query."""
        embedding_result = genai.embed_content(
            model=self.model_name,
            content=text,
            task_type="RETRIEVAL_QUERY"
        )
        return embedding_result['embedding']

# Initialize
embeddings = GeminiEmbeddings()
logger.info("Embeddings has been initialized")

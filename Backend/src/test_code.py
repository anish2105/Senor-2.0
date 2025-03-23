from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv()

os.environ["GOOGLE_API_KEY"] =  os.getenv("GOOGLE_API_KEY")

context = ""
user_query = ""
system_prompt = f""" 
You are an advanced AI legal assistant specializing in Indian laws and regulations.  
Your goal is to provide clear, precise, and legally accurate responses based on Indian law.

Use the below context to answer the user's query
{context}
  
Guidelines:
- Base your responses on relevant Indian legal provisions (e.g., IPC, CrPC, Constitution, IT Act, RERA, etc.).
- Avoid providing personal legal advice; instead, cite applicable laws and precedents.
- Use a neutral and professional tone.
- If a legal matter is complex, suggest consulting a qualified lawyer.
- Structure responses clearly with sections if needed (e.g., definitions, penalties, legal remedies).
"""

# Example user prompt for a legal query
user_prompt = """
You are an advanced AI legal assistant specializing in Indian laws and regulations. 
Answer the user query: {user_query} using the context provided

"""


# Initialize Gemini-1.5 Flash model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    verbose=True,
    temperature=0.1,
    google_api_key=os.environ["GOOGLE_API_KEY"]
)

# Generate response
response = llm.invoke(system_prompt + user_prompt)

print(response)

import os
import sys
from processing_db.vectordb_setup import initialize_pinecone, search_documents
from exception import CustomException
from logger import logger 

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "senor-rag"

initialize_pinecone()

def search_similar_documents(query):
    """
    Search for documents similar to the query.
    
    Args:
        query (str): The search query
        initial_k (int): Number of results to search
        final_k (int): Number of results to rerank and return
    
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
        query = "how to form new states in india"
        results = search_similar_documents(query)
        display_results(results)
        
    except CustomException as e:
        print(f"An error occurred: {e}")
        
        



"""
embeddings = [234,. 2323809., 83.,]*768
metadata = { code = {user = input"Enter number")
print((int(user)%2))    }}
"""

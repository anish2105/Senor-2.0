from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv()

os.environ["GOOGLE_API_KEY"] =  os.getenv("GOOGLE_API_KEY")

# Define system prompt for Indian law-based AI assistant
system_prompt = """ 
You are an advanced AI legal assistant specializing in Indian laws and regulations.  
Your goal is to provide clear, precise, and legally accurate responses based on Indian law.  
Guidelines:
- Base your responses on relevant Indian legal provisions (e.g., IPC, CrPC, Constitution, IT Act, RERA, etc.).
- Avoid providing personal legal advice; instead, cite applicable laws and precedents.
- Use a neutral and professional tone.
- If a legal matter is complex, suggest consulting a qualified lawyer.
- Structure responses clearly with sections if needed (e.g., definitions, penalties, legal remedies).
"""

# Example user prompt for a legal query
user_prompt = """
What are the legal rights of tenants under Indian law in case of eviction?
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

# Print the response
print(response)
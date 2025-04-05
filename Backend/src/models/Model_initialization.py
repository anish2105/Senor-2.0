import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from src.exception import CustomException
from src.logger import logger
import sys

class ChatbotConfig(BaseModel):
    model_name: str = Field(default="gemini-2.0-flash")
    temperature: float = Field(default=0.1)
    verbose: bool = Field(default=True)
    google_api_key: str

class LegalChatbot:
    def __init__(self):
        try:
            load_dotenv()
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY is missing in the .env file.")
            
            self.config = ChatbotConfig(google_api_key=api_key)
            
            self.llm = ChatGoogleGenerativeAI(
                model=self.config.model_name,
                temperature=self.config.temperature,
                verbose=self.config.verbose,
                google_api_key=self.config.google_api_key
            )
            logger.info("LegalChatbot model initialized successfully.")

        except Exception as e:
            logger.error(f"Error initializing LegalChatbot: {str(e)}")
            raise CustomException(e, sys)

    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        try:
            logger.info("Generating response from LLM.")
            return self.llm.invoke(system_prompt + "\n\n" + user_prompt)
        except Exception as e:
            logger.error(f"Error during response generation: {str(e)}")
            raise CustomException(e, sys)

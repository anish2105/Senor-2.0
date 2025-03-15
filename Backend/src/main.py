from Model_initialization import LegalChatbot
from exception import CustomException
from logger import logger
import sys
from prompts import basic_prompt

def load_prompts():
    try:
        
        system_prompt, user_prompt = basic_prompt()
        return system_prompt, user_prompt
    except Exception as e:
        logger.error(f"Error loading prompts: {str(e)}")
        raise CustomException(e, sys)

if __name__ == "__main__":
    try:
        chatbot = LegalChatbot()
        system_prompt, user_prompt = load_prompts()
        
        response = chatbot.generate_response(system_prompt, user_prompt)
        print("\nLegal Chatbot Response:\n", response)
        logger.info("Response generated successfully.")

    except CustomException as ce:
        logger.error(f"Application Error: {str(ce)}")
        print(f"An error occurred: {str(ce)}")

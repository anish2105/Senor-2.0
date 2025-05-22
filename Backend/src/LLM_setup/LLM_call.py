from src.LLM_setup.LLM_initialization import LegalChatbot
from src.prompts.main_prompt import basic_prompt
from src.exception import CustomException
from src.utils import search_similar_documents, display_results
from src.logger import logger
from langchain_core.messages import AIMessage
from src.chat_history_manager import chat_history_manager
from src.prompts.summarization import summarize
import re

# chat_history = []

# def update_chat_history(user_query, system_response):
#     chat_history.append({"user": user_query, "system": system_response})

def get_chunk_text(results):
    return "\n".join([doc.page_content for doc in results])

def parse_gemini_response(response: AIMessage) -> dict:
    """
    Extracts and returns the content inside <inner_monologue> and <answer> tags from the Gemini output.
    """
    try:
        content = response.content if isinstance(response, AIMessage) else str(response)
        inner_monologue_match = re.search(r"<inner_monologue>\s*(.*?)\s*</inner_monologue>", content, re.DOTALL)
        answer_match = re.search(r"<answer>\s*(.*?)\s*</answer>", content, re.DOTALL)
        logger.info("LLM answer has been parsed for inner monologue and final answer")
        return {
            "inner_monologue": inner_monologue_match.group(1).strip() if inner_monologue_match else "",
            "answer": answer_match.group(1).strip() if answer_match else ""
        }
    except CustomException as e:
        logger.error(f"Error during parsing chatbot response's: {str(e)}")
        raise e


def generate_chatbot_response(user_query: str) -> AIMessage:
    try:
        results = search_similar_documents(user_query)
        relevant_chunks = get_chunk_text(results)

        chat_history = chat_history_manager.get()

        if len(chat_history) >= 2:
            first_two = chat_history[:2]

            summary_system_prompt, summary_user_prompt = summarize(first_two)
            logger.info("Summarizing chat history")
            print("Summarizing chat history")
            
            chatbot = LegalChatbot()
            summary_response: AIMessage = chatbot.generate_response(summary_system_prompt, summary_user_prompt)

            chat_history_manager.clear()  # Clear all temporarily
            chat_history_manager.add("Summary of earlier chat", summary_response.content if isinstance(summary_response, AIMessage) else str(summary_response))

            # Add remaining messages after the first two
            for msg in chat_history[2:]:
                chat_history_manager.add(msg['user'], msg['system'])

        chat_summary = "\n".join(
            [f"User: {msg['user']}\nAssistant: {msg['system']}" for msg in chat_history_manager.get()]
        ) if chat_history_manager.get() else "This is the start of the conversation."

        # Response from LLM for user's query
        system_prompt, user_prompt = basic_prompt(chat_summary, relevant_chunks, user_query)
        chatbot = LegalChatbot()
        response: AIMessage = chatbot.generate_response(system_prompt, user_prompt)

        chat_history_manager.add(user_query, response.content if isinstance(response, AIMessage) else str(response))
        logger.info("Chatbot response generated successfully.")
        return response

    except CustomException as e:
        logger.error(f"Error during chatbot response generation: {str(e)}")
        raise e

    
if __name__ == "__main__":
    print("\n🧑‍⚖️ Legal Chatbot (type 'exit' to quit)\n")
    while True:
        try:
            
            query = input("\nYou: ")
            print("Processing .....")
            if query.lower() in ["exit", "quit"]:
                break
            response = generate_chatbot_response(query)
            parsed = parse_gemini_response(response)
            print("\n🤖 Assistant:", parsed["answer"])
        except CustomException as e:
            print("Error:", str(e))
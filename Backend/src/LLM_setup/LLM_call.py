from src.LLM_setup.llm_initialization import LegalChatbot
from src.prompts.main_prompt import basic_prompt
from src.exception import CustomException
from src.utils import search_similar_documents
from src.logger import logger
from langchain_core.messages import AIMessage
from src.chat_history_manager import chat_history_manager
from src.prompts.summarization import summarize
import re
import sys
from ai_agent_call import get_enhanced_legal_answer

def get_chunk_text(results):
    return "\n".join([doc.page_content for doc in results])

def extract_token_usage(response: AIMessage) -> dict:
    """
    Extracts input, output, and total token 
    """
    try:
        usage = response.usage_metadata if hasattr(response, 'usage_metadata') else {}
        return {
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0)
        }
    except Exception as e:
        logger.error(f"Error extracting token usage: {str(e)}")
        raise CustomException(e, sys)


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

        if len(chat_history) >= 4:
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
        return relevant_chunks, response

    except CustomException as e:
        logger.error(f"Error during chatbot response generation: {str(e)}")
        raise e

    
if __name__ == "__main__":
    print("\n🧑‍⚖️ Legal Chatbot (type 'exit' to quit)\n")
    while True:
        try:
            print("\nEnter your query...\n")
            query = input("\nYou: ")
            print("Processing .....")
            if query.lower() in ["exit", "quit"]:
                break
            relevant_chunks, response = generate_chatbot_response(query)
            # print(response)
            parsed = parse_gemini_response(response)
            token_info = extract_token_usage(response)
            if "<additional>" in parsed["answer"].lower() :
                print("\n Primary LLM could not provide an answer. Trying enhanced AI agent...\n")
                logger.info("Entering Agents call...")
                fallback_answer = get_enhanced_legal_answer(query)
                print("\n🤖 Enhanced Assistant:", fallback_answer)
            else:
                print("\n🤖 Assistant:", parsed["answer"])
                print("\n************************************************\n")
                print("Input tokens:", token_info["input_tokens"])
                print("Output tokens:", token_info["output_tokens"])
                print("Total tokens:", token_info["total_tokens"])
                print("\n************************************************\n")
                user_followup = input("\n💡 Do you want to enhance this answer? (y/n): ").strip().lower()
                if user_followup == "y":
                    # You can pass chat history if desired
                    history_str = "\n".join(
                        [f"User: {msg['user']}\nAssistant: {msg['system']}" for msg in chat_history_manager.get()]
                    )
                    # print(history_str)
                    enhanced_response = get_enhanced_legal_answer(query, chat_history=history_str)
                    print("\n🤖 Enhanced Assistant:", enhanced_response)
        except CustomException as e:
            print("Error:", str(e))
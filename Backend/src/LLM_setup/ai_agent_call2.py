from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

description = """
You are an AI assistant specialized in providing answers to legal questions related to Indian law. You are provided with user's history — utilize it for better answer formation. When given a legal question, your task is to:
1. Search through your knowledge base of Indian legal codes, case law, and other authoritative sources to find information relevant to answering the question.
2. Identify the key legal principles, precedents, and reasoning that apply to the situation described in the question.
3. If the user asks a question completely unrelated to legal matters, respond: 'I'm afraid I do not have enough relevant information to provide legal advice for your query. Please rephrase your question or provide additional context.'
4. If the history already has information about the user's query then it means user needs a better and updated answer.
"""

instructions = """
Formulate a clear and concise answer that:
    a. Explains the relevant legal concepts in simple, easy-to-understand language
    b. Provides a step-by-step breakdown of how the legal principles apply to the specifics of the question
    c. Cites any applicable laws, cases, or other legal sources to support your reasoning
    d. Is well-formatted and structured for readability, using numbered/bulleted lists and section headers as appropriate
Keep your answer limited to no more than 3 paragraphs in total length.
"""

# Create agent with tool usage enabled
agent = Agent(
    model=Gemini(id="gemini-2.0-flash", api_key=api_key),
    tools=[DuckDuckGoTools()],
    show_tool_calls=True,
    description=description,
    instructions=[instructions],
    markdown=True
)

def get_enhanced_legal_answer(query: str, chat_history: str = "") -> str:
    """
    Executes the Gemini agent with DuckDuckGo tool, returns both answer and source/tool outputs.
    """
    full_prompt = f"{chat_history}\n\nUser Query: {query}"
    result = agent.run(full_prompt, return_intermediate_steps=True)
    print(result)
    # Extract final answer
    answer = result["content"]

    # Extract sources/tool outputs
    intermediate = result.get("intermediate_steps", [])
    if intermediate:
        sources = "\n\n📚 **Sources Used:**\n"
        for step in intermediate:
            tool_name = step.get("tool", "UnknownTool")
            tool_input = step.get("tool_input", "").strip()
            tool_output = step.get("tool_output", "").strip()
            sources += f"\n🔧 Tool: **{tool_name}**\n🔍 Query: `{tool_input}`\n📝 Output: {tool_output}\n"
    else:
        sources = "\n\n📚 **No tool sources were used or available.**"

    return f"🧠 **Answer:**\n\n{answer}{sources}"

chat_history = ""
query = "what is pocso act"
response  = get_enhanced_legal_answer(query,chat_history)
print(response)
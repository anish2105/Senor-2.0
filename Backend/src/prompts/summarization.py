def summarize(CHAT_history):
    summary_system_prompt = f"""
    <Instructions>
    Your task is to summarize a given chat history between a user and an AI assistant. The chat history will be provided in the following format: ('user': user_query, 'system': ai_response), where 'user' represents the user's query, and 'system' represents the AI assistant's response.

    Here are the steps you should follow:

    1. Carefully analyze the provided chat history

    2. Identify the key points, main topics, and essential information discussed throughout the conversation.

    3. Generate a concise summary that captures the most relevant and important details from the chat history. Your summary should be a coherent and well-structured text that accurately represents the core content of the conversation.

    4. While summarizing, focus on rephrasing the information in your own words rather than directly copying or quoting from the chat history.

    5. Omit any unnecessary, redundant, or irrelevant information that does not contribute to the overall understanding of the chat history.

    6. Present your summary within the following XML tags:

    <summary>
    [Your summary goes here]
    </summary>

    Remember, the goal is to provide a clear and concise summary that effectively captures the essence of the chat history while maintaining brevity and coherence.
    </Instructions>
    """
    
    summary_user_prompt = f"""
    <Inputs>
    {CHAT_history}
    </Inputs>
    1. Carefully analyze the provided chat history

    2. Identify the key points, main topics, and essential information discussed throughout the conversation.

    3. Generate a concise summary that captures the most relevant and important details from the chat history. Your summary should be a coherent and well-structured text that accurately represents the core content of the conversation.

    4. While summarizing, focus on rephrasing the information in your own words rather than directly copying or quoting from the chat history.

    5. Omit any unnecessary, redundant, or irrelevant information that does not contribute to the overall understanding of the chat history.

    6. Present your summary within the following XML tags:

    <summary>
    [Your summary goes here]
    </summary>

    Remember, the goal is to provide a clear and concise summary that effectively captures the essence of the chat history while maintaining brevity and coherence.
    </Instructions>
    """
    
    return summary_system_prompt , summary_user_prompt
import streamlit as st
import requests

API_URL = "http://localhost:8000/chat"

st.set_page_config(page_title="Legal Chatbot", page_icon="⚖️")
st.title("🧑‍⚖️ Indian Legal Chatbot")
st.caption("Ask legal questions and get responses based on Indian law")

# Initialize session state for chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Clear chat button
with st.sidebar:
    st.header("⚙️ Options")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.experimental_rerun()

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle user input
if user_input := st.chat_input("Type your legal query..."):
    # Store user's message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(API_URL, json={"query": user_input})

                if response.status_code == 200:
                    data = response.json()

                    answer = data.get("answer", "Sorry, I couldn't find an answer.")
                    inner_monologue = data.get("inner_monologue", "")
                    eval_scores = data.get("Evaluation scores", {})

                    st.markdown(f"**Answer:** {answer}")
                    st.session_state.messages.append({"role": "assistant", "content": f"{answer}"})

                    # Expanders for more details
                    with st.expander("🧠 Inner Monologue"):
                        st.markdown(inner_monologue)

                    with st.expander("📊 Evaluation Metrics"):
                        for metric, score in eval_scores.items():
                            st.write(f"{metric}: {score:.4f}")

                else:
                    st.error("❌ Error: Chatbot backend returned an error.")
            except Exception as e:
                st.error(f"❌ Exception occurred: {str(e)}")
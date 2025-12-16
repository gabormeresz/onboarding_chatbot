from dotenv import load_dotenv
import streamlit as st
from onboarding_agent.agent.graph import build_graph
from onboarding_agent.agent.state import build_initial_state

# Load environment variables for LangSmith tracing
load_dotenv(override=False)

st.set_page_config(page_title="Onboarding Chatbot")

st.title("💬 Onboarding Assistant")

st.markdown(
    """
Welcome to the onboarding assistant! Ask me questions about:
- HR policies and procedures
- IT setup and troubleshooting
- Equipment and access requests
- Security guidelines
"""
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if user_input := st.chat_input("Ask me anything about onboarding..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            graph = build_graph()
            initial_state = build_initial_state(user_input)

            result = graph.invoke(initial_state)
            response = result.get(
                "answer", "I'm sorry, I couldn't process that request."
            )

        st.markdown(response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

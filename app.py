import streamlit as st
import uuid
from config import get_bedrock_client
from agent import agent_response
from memory import save_message, get_history, get_recent_history

st.set_page_config(page_title="AI Support Agent", layout="wide")

st.title("🤖 AI Customer Support Agent (AWS Bedrock)")

# ✅ Sidebar
st.sidebar.title("💬 Chat History")

# Clear chat button
if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())

# ✅ Initialize Bedrock client
bedrock = get_bedrock_client()

# ✅ Create session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# ✅ Load chat history
if "messages" not in st.session_state:
    history = get_history(None, st.session_state.session_id)
    st.session_state.messages = [
        (msg["role"], msg["message"]) for msg in history
    ]

user_input = st.text_input("Ask your question:", key="input")

if st.button("Send"):
    if user_input:

        # 🧠 Pull recent turns for this session so the LLM has short-term
        # context (only used when the query falls through to the LLM fallback)
        recent_history = get_recent_history(st.session_state.session_id, limit=5)

        # 🤖 Get response
        response = agent_response(bedrock, user_input, recent_history)

        # 💾 Save in session
        st.session_state.messages.append(("You", user_input))
        st.session_state.messages.append(("Agent", response))

        # 💾 Save in JSON
        save_message(None, st.session_state.session_id, "You", user_input)
        save_message(None, st.session_state.session_id, "Agent", response)

        # 🔁 Rerun to clear input
        st.rerun()



# 📜 Main chat display
for role, msg in st.session_state.messages:
    if role == "You":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 Agent:** {msg}")

# 📂 Sidebar chat history
with st.sidebar:
    for role, msg in st.session_state.messages:
        if role == "You":
            st.markdown(f"🧑 {msg}")
        else:
            st.markdown(f"🤖 {msg}")


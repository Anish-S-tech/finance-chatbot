import streamlit as st
from openai import OpenAI

# Secret values
LLM_API_KEY = st.secrets["LLM_API_KEY"]
API_BASE_URL = st.secrets["API_BASE_URL"]
MODEL_ID = st.secrets["MODEL_ID"]
SYSTEM_PROMPT = st.secrets.get("SYSTEM_PROMPT", "You are a helpful finance assistant.")

client = OpenAI(base_url=API_BASE_URL, api_key=LLM_API_KEY)

st.set_page_config(
    page_title="Finance Chatbot",
    layout="wide"
)

# Inject some CSS for modern look
st.markdown(
    """
    <style>
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 10px;
        background-color: #f9f9f9;
    }
    .user-bubble {
        background-color: #DCF3FF;
        padding: 8px 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        align-self: flex-end;
        max-width: 80%;
    }
    .ai-bubble {
        background-color: #E8E4FF;
        padding: 8px 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        align-self: flex-start;
        max-width: 80%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Interactive Finance Assistant")

# Initialize conversation history
if "history" not in st.session_state:
    st.session_state.history = []

def generate_response(message, history_list):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for u_msg, a_msg in history_list:
        messages.append({"role": "user", "content": u_msg})
        messages.append({"role": "assistant", "content": a_msg})
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=messages
    )
    return response.choices[0].message.content


# Chat UI container
with st.container():
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for u, a in st.session_state.history:
        st.markdown(f"<div class='user-bubble'><strong>You:</strong> {u}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='ai-bubble'><strong>Bot:</strong> {a}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Input section
col1, col2 = st.columns([5,1])
with col1:
    user_input = st.text_input("Type your question:", key="input", label_visibility="collapsed")
with col2:
    send_button = st.button("Send", use_container_width=True)

if send_button and user_input:
    ai_reply = generate_response(user_input, st.session_state.history)
    st.session_state.history.append((user_input, ai_reply))
    st.experimental_rerun()  # works as long as your version supports it, otherwise st.rerun()

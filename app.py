import streamlit as st
from openai import OpenAI

# --- Secrets / config access ---
# st.secrets is expected to have keys: LLM_API_KEY, API_BASE_URL, MODEL_ID
LLM_API_KEY = st.secrets["LLM_API_KEY"]
API_BASE_URL = st.secrets["API_BASE_URL"]
MODEL_ID = st.secrets["MODEL_ID"]

SYSTEM_PROMPT = st.secrets.get("SYSTEM_PROMPT", "You are a helpful finance assistant.")

# --- Initialize client (Fireworks but OpenAI compatible) ---
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=LLM_API_KEY
)

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="Finance Chatbot",
    layout="centered"
)

# --- Custom CSS for Professional Look ---
st.markdown("""
    <style>
    body, .stApp {
        background-color: #ffffff;
        color: #1a1a1a;
        font-family: 'Helvetica', sans-serif;
    }
    .chat-container {
        max-height: 550px;
        overflow-y: auto;
        padding: 12px;
        border: 1px solid #cccccc;
        border-radius: 6px;
        background-color: #fdfdfd;
    }
    .user-bubble {
        background-color: #e7f0f9;
        color: #0a0a0a;
        padding: 10px;
        border-radius: 6px;
        margin-bottom: 6px;
        align-self: flex-end;
        border: 1px solid #c3dff2;
        max-width: 80%;
    }
    .ai-bubble {
        background-color: #f2f2f2;
        color: #0a0a0a;
        padding: 10px;
        border-radius: 6px;
        margin-bottom: 6px;
        align-self: flex-start;
        border: 1px solid #dedede;
        max-width: 80%;
    }
    .stTextInput>div>div>input{
        background-color:#ffffff !important;
        border:1px solid #cccccc !important;
        color:#1a1a1a !important;
    }
    .stButton>button{
        background-color:#004080;
        color:white;
        border:none;
        border-radius:4px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("Intelligent Finance Assistant")

# --- Session state for chat history ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Generate response function ---
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

# --- UI input ---
user_input = st.text_input("Ask a financial question", key="input")
send_button = st.button("Send")

# --- On Send ---
if send_button and user_input:
    assistant_reply = generate_response(user_input, st.session_state.history)
    st.session_state.history.append((user_input, assistant_reply))
    st.rerun()

# --- Display chat with custom bubble classes ---
st.write("")  # small spacer

st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for user_msg, ai_msg in st.session_state.history:
    st.markdown(f'<div class="user-bubble">You: {user_msg}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ai-bubble">Assistant: {ai_msg}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

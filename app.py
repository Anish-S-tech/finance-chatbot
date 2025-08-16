import streamlit as st
from openai import OpenAI

# These will be read from your secrets (via Streamlit Cloud secrets or HuggingFace Secrets)
LLM_API_KEY = st.secrets["LLM_API_KEY"]  # Fireworks API key!
API_BASE_URL = st.secrets["API_BASE_URL"]
MODEL_ID = st.secrets["MODEL_ID"]
SYSTEM_PROMPT = st.secrets.get("SYSTEM_PROMPT", "You are a helpful finance assistant.")

# Initialize Fireworks/OpenAI-compatible client
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=LLM_API_KEY
)

st.set_page_config(
    page_title="Finance Chatbot (Fireworks/Mixtral)",
    page_icon="💰",
    layout="centered"
)

st.title("💸 Finance Chatbot (Fireworks Models)")

# Session state to keep history
if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("Ask me a finance question:", key="input")
send_button = st.button("Send")

def generate_response(message, history_list):
    # Build messages with conversation memory
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

if send_button and user_input:
    assistant_reply = generate_response(user_input, st.session_state.history)
    st.session_state.history.append((user_input, assistant_reply))
    st.rerun()

# Display chat history (simple)
for user_msg, ai_msg in st.session_state.history:
    st.write("**You:**", user_msg)
    st.write("**Assistant:**", ai_msg)
    st.write("---")

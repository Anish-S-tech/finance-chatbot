import os
import streamlit as st
from openai import OpenAI

# Load credentials from Streamlit Cloud secrets (recommended)
LLM_API_KEY = st.secrets["LLM_API_KEY"]
API_BASE_URL = st.secrets["API_BASE_URL"]
MODEL_ID = st.secrets["MODEL_ID"]
SYSTEM_PROMPT = st.secrets.get("SYSTEM_PROMPT", "You are a helpful finance assistant.")

# Initialize OpenAI-compatible client (Fireworks)
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=LLM_API_KEY
)

st.set_page_config(page_title="Finance Chatbot (Mistral)",
                   page_icon="💰",
                   layout="centered")

st.title("💸 Finance Chatbot (Mistral via Fireworks)")

if "history" not in st.session_state:
    st.session_state.history = []

# UI:
user_input = st.text_input("Ask me a financial question:", key="input")
send_button = st.button("Send")

def generate_response(message, history):
    # Build messages for API
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for user_msg, ai_msg in history:
        if user_msg:
            messages.append({"role": "user", "content": user_msg})
        if ai_msg:
            messages.append({"role": "assistant", "content": ai_msg})

    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=messages
    )
    return response.choices[0].message.content

if send_button and user_input:
    output = generate_response(user_input, st.session_state.history)
    st.session_state.history.append((user_input, output))
    st.experimental_rerun()

# Display chat history
for user_msg, ai_msg in st.session_state.history:
    st.write("**You:**", user_msg)
    st.write("**Assistant:**", ai_msg)
    st.write("---")

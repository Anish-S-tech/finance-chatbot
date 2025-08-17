# app.py

import streamlit as st
from openai import OpenAI

# =================== Configuration ===================

LLM_API_KEY = st.secrets["LLM_API_KEY"]
API_BASE_URL = st.secrets["API_BASE_URL"]

SYSTEM_PROMPT = st.secrets.get(
    "SYSTEM_PROMPT",
    "You are a knowledgeable, friendly finance assistant. Always answer clearly and professionally."
)

# Use the Fireworks-style model IDs provided in secrets
MODEL_DEEPSEEK = st.secrets.get("MODEL_DEEPSEEK")
MODEL_MISTRAL = st.secrets.get("MODEL_MISTRAL")
MODEL_GEMMA = st.secrets.get("MODEL_GEMMA")

MODEL_OPTIONS = {
    "DeepSeek V3": MODEL_DEEPSEEK,
    "Mistral 7B": MODEL_MISTRAL,
    "Gemma 7B IT": MODEL_GEMMA
}

# Initialize client
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=LLM_API_KEY
)

# =====================================================

st.set_page_config(
    page_title="Finance Chatbot",
    page_icon="💵",
    layout="centered",
)

st.markdown(
    "<h1 style='text-align:center; color:#0c3c60;'>💸 Finance AI Chatbot</h1>",
    unsafe_allow_html=True
)

# Model Selection
model_label = st.selectbox(
    "Select Model:",
    list(MODEL_OPTIONS.keys())
)

# Initialize history
if "history" not in st.session_state:
    st.session_state.history = []

# User input
user_input = st.text_input(
    "Your finance question:",
    key="user_input"
)

if st.button("Send") and user_input:
    selected_model_id = MODEL_OPTIONS[model_label]

    def generate_response(message, history):
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for u_msg, a_msg in history:
            messages.append({"role": "user", "content": u_msg})
            messages.append({"role": "assistant", "content": a_msg})

        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model=selected_model_id,
            messages=messages
        )
        return response.choices[0].message.content

    reply = generate_response(user_input, st.session_state.history)
    st.session_state.history.append((user_input, reply))
    user_input = ""


# Show chat
for u_msg, a_msg in st.session_state.history:
    st.markdown(f"**You:** {u_msg}")
    st.markdown(f"**Assistant:** {a_msg}")
    st.markdown("---")

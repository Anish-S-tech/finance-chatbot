import streamlit as st
from openai import OpenAI

# Read API keys / endpoints from secrets
LLM_API_KEY = st.secrets["LLM_API_KEY"]
API_BASE_URL = st.secrets["API_BASE_URL"]
SYSTEM_PROMPT = st.secrets.get(
    "SYSTEM_PROMPT",
    "You are a helpful financial assistant. Answer clearly and professionally."
)

# Model IDs from secrets
MODEL_DEEPSEEK = st.secrets["MODEL_DEEPSEEK"] 
MODEL_OSS = st.secrets["MODEL_OSS"]
MODEL_LLAMA = st.secrets["MODEL_LLAMA"]

# Initialize client
client = OpenAI(
    api_key=LLM_API_KEY,
    base_url=API_BASE_URL,
)

st.set_page_config(
    page_title="Finance Chatbot",
    layout="centered",
)

st.markdown("<h1 style='text-align: center;'> Finance Chatbot</h1>", unsafe_allow_html=True)

# Model selector
st.sidebar.title("Model Selector")
model_option = st.sidebar.selectbox(
    "Choose a language model",
    ["DeepSeek-v3", "GPT OSS", "LLaMA 3.1"]
)

model_id_map = {
    "DeepSeek-v3": MODEL_DEEPSEEK,
    "GPT OSS": MODEL_OSS,
    "LLaMA 3.1": MODEL_LLAMA,
}

# Initialize chat history
if "history" not in st.session_state:
    st.session_state.history = []

def chat_model_call(user_message, history, model_id):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for (u, a) in history:
        messages.append({"role": "user", "content": u})
        messages.append({"role": "assistant", "content": a})
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=model_id,
        messages=messages
    )
    return response.choices[0].message.content.strip()


# Display message history
for u, a in st.session_state.history:
    st.markdown(f"**You:** {u}")
    st.markdown(f"**Assistant:** {a}")  # Now plain

st.write("---")

# User input + send button
user_input = st.text_input("Your question:")
if st.button("Send") and user_input:
    selected_model_id = model_id_map[model_option]
    try:
        reply = chat_model_call(user_input, st.session_state.history, selected_model_id)
    except Exception as e:
        reply = f"⚠ Error: {e}"

    st.session_state.history.append((user_input, reply))
    st.rerun()


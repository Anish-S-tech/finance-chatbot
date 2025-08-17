import streamlit as st
from openai import OpenAI

# Load credentials and model IDs from secrets
LLM_API_KEY   = st.secrets["LLM_API_KEY"]
API_BASE_URL  = st.secrets["API_BASE_URL"]
SYSTEM_PROMPT = st.secrets["SYSTEM_PROMPT"]

MODEL_DEEPSEEK = st.secrets["MODEL_DEEPSEEK"]
MODEL_MISTRAL  = st.secrets["MODEL_MISTRAL"]
MODEL_GEMMA    = st.secrets["MODEL_GEMMA"]

# Initialize LLM client (Fireworks)
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=LLM_API_KEY
)

# Custom style (corporate blue/gray)
st.set_page_config(
    page_title="Finance Chatbot - MultiModel",
    layout="centered"
)

st.markdown(
    """
    <style>
    body { background-color: #f4f6f9; }
    .stApp { font-family: Arial, sans-serif; }
    .title { font-size: 32px; color: #083358; font-weight: bold; text-align: center; }
    .credit { font-size: 10px; text-align: center; margin-top: 20px; color: #888; }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="title"> Finance Chatbot (Multi-Model)</div>', unsafe_allow_html=True)

st.markdown("Ask about investments, markets, loans, or general finance. The model will adjust based on your tone or topic.")

# Initialize session
if "history" not in st.session_state:
    st.session_state.history = []

def choose_model(user_message: str) -> str:
    """Simple routing logic by keyword or emotional tone."""
    msg = user_message.lower()

    # Keywords about emotion or sentiment
    if any(w in msg for w in ["sad", "depressed", "happy", "excited", "emotion", "feeling"]):
        return MODEL_GEMMA  # more emotional

    # Keywords about technical finance queries
    if any(w in msg for w in ["stock", "investment", "loan", "mutual fund", "returns", "roi", "nifty", "sensex"]):
        return MODEL_DEEPSEEK

    # Default general finance advice
    return MODEL_MISTRAL

def generate_response(message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for u, a in history:
        messages.append({"role": "user", "content": u})
        messages.append({"role": "assistant", "content": a})

    messages.append({"role": "user", "content": message})

    model_to_use = choose_model(message)

    response = client.chat.completions.create(
        model = model_to_use,
        messages = messages
    )
    return response.choices[0].message.content

# Input field
user_input = st.text_input("Your question:")

if st.button("Send") and user_input:
    reply = generate_response(user_input, st.session_state.history)
    st.session_state.history.append((user_input, reply))
    user_input = ""  # reset

# Display chat history
for u, r in st.session_state.history:
    st.write(f"**You:** {u}")
    st.write(f"**Assistant:** {r}")
    st.write("---")

st.markdown('<div class="credit">Powered by Fireworks AI • Models: Mistral, DeepSeek, Gemma</div>', unsafe_allow_html=True)

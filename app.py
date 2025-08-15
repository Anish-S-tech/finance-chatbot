import os
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

# Load environment variables from .env
load_dotenv()

# Required Environment Variables
API_BASE_URL = os.getenv("API_BASE_URL")  # e.g. https://api.fireworks.ai/inference/v1
LLM_API_KEY = os.getenv("LLM_API_KEY")    # your Fireworks AI token
MODEL_ID = os.getenv("MODEL_ID")          # e.g. mistralai/Mistral-7B-Instruct-v0.2
SYSTEM_PROMPT = os.getenv("XTRNPMT") or "You are a helpful financial assistant."

# Warn if keys are missing
if not API_BASE_URL or not LLM_API_KEY:
    print("⚠️  Missing API_BASE_URL or LLM_API_KEY environment variable. "
          "Please set these in .env or Space secrets.")

# Initialize client for Fireworks AI (works like OpenAI client)
try:
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=LLM_API_KEY
    )
    print(f"✅ OpenAI-compatible client initialized for model: {MODEL_ID}")
except Exception as e:
    raise RuntimeError(f"Failed to initialize client: {e}")


def generate_response(message, history):
    """
    Streams tokens from Fireworks API like OpenAI.
    """
    # Build message list with system prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Append chat history
    for user_msg, ai_msg in history:
        if user_msg:
            messages.append({"role": "user", "content": user_msg})
        if ai_msg:
            messages.append({"role": "assistant", "content": ai_msg})

    # Add the latest user message
    messages.append({"role": "user", "content": message})

    try:
        stream = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages,
            stream=True,
        )
        response_text = ""
        # Return tokens as streaming response
        for chunk in stream:
            token = ""
            # chunk.choices[0].delta for streamed tokens
            if chunk.choices and chunk.choices[0].delta:
                token = chunk.choices[0].delta.get("content", "")
            elif chunk.choices and chunk.choices[0].message:
                token = chunk.choices[0].message.get("content", "")

            response_text += token
            yield response_text

    except Exception as e:
        error_text = f"API Error: {e}"
        print(error_text)
        yield error_text


# Gradio UI
with gr.Blocks(title="Finance Chatbot (Fireworks AI)") as demo:

    gr.Markdown("### 💸 Fireworks Mistral Finance Chatbot\n"
                "Ask anything about savings, investments, budgeting, etc.")

    chatbot_ui = gr.ChatInterface(
        fn=generate_response,
        chatbot=gr.Chatbot(height=700, label="Financial Advisor"),
        theme="dark"
    )

if __name__ == "__main__":
    demo.queue().launch()
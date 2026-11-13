"""Gemini Q&A chatbot built with Streamlit and LangChain."""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

DEFAULT_MODEL = "gemini-2.5-flash"
MODELS = ("gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.5-pro")
DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful assistant. Answer clearly and concisely, and say so "
    "when you are not sure."
)
# Only the most recent turns are sent, so long chats stay inside the context
# window and the cost per message stays bounded.
MAX_HISTORY_MESSAGES = 20

st.set_page_config(page_title="Gemini Q&A Chatbot", page_icon="💬", layout="centered")


def get_api_key() -> str | None:
    """Read the key from Streamlit secrets first, then the environment."""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        # st.secrets raises when no secrets.toml exists, which is the normal
        # case for local runs that use a .env file.
        pass
    return os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


@st.cache_resource(show_spinner=False)
def get_llm(api_key: str, model: str, temperature: float, max_tokens: int):
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=temperature,
        max_output_tokens=max_tokens,
    )


def to_langchain_messages(system_prompt: str, history: list[dict]):
    messages = [SystemMessage(content=system_prompt)] if system_prompt.strip() else []
    for item in history[-MAX_HISTORY_MESSAGES:]:
        cls = HumanMessage if item["role"] == "user" else AIMessage
        messages.append(cls(content=item["content"]))
    return messages


def chunk_text(chunk) -> str:
    """Gemini can return content as a string or as a list of parts."""
    content = chunk.content
    if isinstance(content, str):
        return content
    return "".join(
        part.get("text", "") if isinstance(part, dict) else str(part)
        for part in content
    )


if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Settings")
    model = st.selectbox("Model", MODELS, index=MODELS.index(DEFAULT_MODEL))
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.05)
    max_tokens = st.slider("Max response tokens", 128, 4096, 1024, 128)
    system_prompt = st.text_area("System prompt", DEFAULT_SYSTEM_PROMPT, height=110)
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.title("💬 Gemini Q&A Chatbot")
st.caption("Ask a question. Follow-ups keep the context of the conversation.")

api_key = get_api_key()
if not api_key:
    st.warning(
        "No API key found. Set `GEMINI_API_KEY` in a `.env` file, as an "
        "environment variable, or in Streamlit secrets."
    )
    st.stop()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            llm = get_llm(api_key, model, temperature, max_tokens)
            stream = llm.stream(
                to_langchain_messages(system_prompt, st.session_state.messages)
            )
            reply = st.write_stream(chunk_text(chunk) for chunk in stream)
        except Exception as error:  # surface API failures instead of crashing
            reply = None
            st.error(f"The request failed: {error}")

    if reply:
        st.session_state.messages.append({"role": "assistant", "content": reply})
    else:
        # Drop the unanswered question so a retry does not send it twice.
        st.session_state.messages.pop()

# Q&A ChatBot

A conversational question-answering app built with Streamlit, LangChain and
Google Gemini.

## Features

- Multi-turn chat that remembers the conversation
- Responses stream in as they are generated
- Sidebar controls for model, temperature, response length and system prompt
- API key read from Streamlit secrets or the environment, never from code

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # then add your key
streamlit run streamlit_app.py
```

Get a key from [Google AI Studio](https://aistudio.google.com/apikey).

## Run with Docker

```bash
docker build -t qa-chatbot .
docker run -p 8501:8501 -e GEMINI_API_KEY=your-key qa-chatbot
```

The container listens on `$PORT` when the platform sets it (Render, Cloud Run)
and on 8501 otherwise.

## Deploy on Streamlit Community Cloud

Point the app at `streamlit_app.py` and add the key under
**Settings → Secrets**:

```toml
GEMINI_API_KEY = "your-key"
```

## Project layout

| Path | Purpose |
| --- | --- |
| `streamlit_app.py` | The chat application |
| `Dockerfile` | Container image for Render or any Docker host |
| `generate_bot_stats.py`, `simulate_conversations.py` | Write simulated usage numbers to `data/bot_stats.json` for a scheduled workflow. The numbers are random, not measured from the app. |

# apps/qa-chatbot/Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render exposes via $PORT
EXPOSE 8501

# Streamlit command using Render's PORT environment variable
CMD streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0

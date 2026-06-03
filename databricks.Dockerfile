# Databricks Apps compatible Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements_streamlit.txt .
RUN pip install --no-cache-dir -r requirements_streamlit.txt

# Copy app and content
COPY app_streamlit.py .
COPY content/ ./content/

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app_streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]

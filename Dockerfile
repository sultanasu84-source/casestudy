FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user WITH valid home
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/bin/sh" \
    appuser

# Copy app code
COPY . .

# Fix permissions
RUN chown -R appuser:appuser /app

# Switch user
USER appuser

# Expose Streamlit port
EXPOSE 9002

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=9002", "--server.address=0.0.0.0"]

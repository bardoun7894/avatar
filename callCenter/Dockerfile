# Call Center Backend - FastAPI + LiveKit Agents
FROM python:3.11-slim

# Install system dependencies including supervisor
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    portaudio19-dev \
    ffmpeg \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for logs
RUN mkdir -p /app/logs

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Environment variables setup
# These are sourced from docker-compose.yml or .env files
# No defaults needed - values come from env_file and environment sections
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run supervisor to manage both API server and agent worker
# Supervisor will start:
#   1. FastAPI server (main.py) - port 8000
#   2. LiveKit agent worker (call_center_agent.py) - connects to LiveKit
# All environment variables (LIVEKIT_URL, OPENAI_API_KEY, DATABASE_URL, etc.)
# are loaded from docker-compose.yml env_file and environment sections
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

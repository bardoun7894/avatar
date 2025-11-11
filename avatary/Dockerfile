# Avatar Backend - Python + LiveKit Agents
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    portaudio19-dev \
    ffmpeg \
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

# Environment variables setup
# These are sourced from docker-compose.yml or .env files
# No defaults needed - values come from env_file and environment sections
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import sys; sys.exit(0)" || exit 1

# Run the agent
# All environment variables (LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET, etc.)
# are loaded from docker-compose.yml env_file and environment sections
CMD ["python", "agent.py", "start"]

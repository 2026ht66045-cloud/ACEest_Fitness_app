FROM python:3.10-slim

WORKDIR /app

# Install system dependencies including xvfb and xauth
RUN apt-get update && apt-get install -y \
    xvfb \
    xauth \
    python3-tk \
    tk \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxft2 \
    libxss1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (optional for security)
RUN useradd -m appuser
USER appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Install Python dependencies
COPY requirements.txt .
RUN python -m venv .venv && \
    .venv/bin/pip install --no-cache-dir -r requirements.txt && \
    .venv/bin/pip install pytest

COPY . .

CMD ["python", "aceest_app.py"]

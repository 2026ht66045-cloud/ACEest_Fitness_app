FROM python:3.10-slim

# Install Tkinter + xvfb in one step
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-tk \
    tk \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxft2 \
    libxss1 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m appuser
USER appuser

# Set working directory
WORKDIR /home/appuser/app

# Copy requirements first (better caching)
COPY --chown=appuser:appuser requirements.txt .

# Install dependencies in a venv
RUN python -m venv .venv && \
    .venv/bin/pip install --no-cache-dir -r requirements.txt && \
    .venv/bin/pip install pytest

# Copy application code
COPY --chown=appuser:appuser . .

# Default command (for local run)
CMD ["python", "aceest_app.py"]

# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.12-slim

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Copy installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Create writable directory for pyngrok to download ngrok binary
RUN mkdir -p /home/appuser/.ngrok2 && \
    mkdir -p /home/appuser/.local/lib/python3.12/site-packages/pyngrok/bin && \
    chown -R appuser:appuser /home/appuser/.ngrok2 && \
    chown -R appuser:appuser /home/appuser/.local

# Copy application code
COPY app/ ./app/

# Set ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Add local bin to PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Set pyngrok to use a writable directory
ENV NGROK_PATH=/home/appuser/.local/bin/ngrok

# Environment defaults
ENV PORT=8080
ENV DEBUG=false

EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--access-logfile", "-", "app.main:app"]

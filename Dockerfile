FROM python:3.13-slim

WORKDIR /opt/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache

COPY src/ src/

RUN addgroup --gid 10000 appgroup && \
    adduser --gecos "App User" --disabled-password --uid 10000 --gid 10000 appuser && \
    chown -R appuser:appgroup /opt/app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

ENV HOST=0.0.0.0
ENV PORT=8000

CMD ["python", "-m", "src.main"]

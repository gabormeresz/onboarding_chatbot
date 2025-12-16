FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev

COPY src ./src
COPY streamlit ./streamlit
COPY data ./data
COPY README.md ./

EXPOSE 8501

ENV PYTHONPATH=/app/src
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD curl -fsS http://localhost:8501/_stcore/health || exit 1

CMD ["uv", "run", "streamlit", "run", "streamlit/app.py", "--server.address=0.0.0.0", "--server.port=8501"]

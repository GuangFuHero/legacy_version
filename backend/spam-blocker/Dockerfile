FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:$PATH"

RUN uv --version

COPY pyproject.toml uv.lock ./
COPY src/ ./src/

RUN uv sync --frozen

RUN mkdir -p logs
RUN touch logs/main.log

COPY secret/cred.txt ./
RUN mkdir -p secret && \
    python -c "import base64, json; data = open('cred.txt').read().strip(); decoded = base64.b64decode(data); open('secret/cred.json', 'wb').write(decoded)" && \
    rm cred.txt

ENV PYTHONPATH=/app

CMD ["uv", "run", "python", "src/main.py"]
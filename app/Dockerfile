FROM python:3.13 AS builder

WORKDIR /app/

RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    make \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml pdm.lock ./

RUN pip install pdm \
    && python -m venv /venv \
    && . /venv/bin/activate \
    && pdm install --production

FROM python:3.13-slim

WORKDIR /app/

COPY --from=builder /venv /venv

COPY . .

ENV VIRTUAL_ENV=/venv
ENV PATH="/venv/bin:$PATH"
ENV PYTHONPATH="/app"

EXPOSE 8080

CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8080"]
# CMD ["sh", "-c", "cd app && alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8080"]
# CMD ["sh", "-c", "echo '=== FILES IN /app ===' && ls -la /app && echo '=== FIND MAIN.PY ===' && find /app -name main.py && echo '=== STARTING APP ===' && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8080"]

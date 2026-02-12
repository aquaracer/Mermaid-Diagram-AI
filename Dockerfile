FROM python:3.13-alpine

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv sync --frozen

COPY app ./app

ENTRYPOINT ["uv", "run", "python", "-m", "app.cli"]
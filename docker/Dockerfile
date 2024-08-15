FROM python:3.10 as base

ARG DEV=false
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

FROM base as builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN apt-get update && \
    apt-get install --no-install-recommends --yes git

WORKDIR /app

# Install Poetry
RUN pip install poetry==1.8.3

# Install the app
COPY pyproject.toml poetry.lock ./
RUN if [ $DEV ]; then \
      poetry install --with dev --no-root && rm -rf $POETRY_CACHE_DIR; \
    else \
      poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR; \
    fi

# Copy the app
FROM base as runtime

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Embedding model is around 2.5GB and downloading it every time is not feasible, increases cold start time
COPY models /app/models
ENV SENTENCE_TRANSFORMERS_HOME=/app/models

COPY glov /app/glov

WORKDIR /app/glov

ENTRYPOINT ["fastapi", "run", "app.py", "--port", "8000", "--proxy-headers"]
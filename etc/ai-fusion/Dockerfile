ARG REPOSITORY_URL=""
FROM ${REPOSITORY_URL}/base/python:3.12.11-slim AS python-base

ENV PIP_NO_CACHE_DIR=off \
    PYTHONUNBUFFERED=1 \
    LC_ALL=C \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_PATH=/opt/poetry \
    POETRY_VERSION=1.8.4 \
    VENV_PATH=/app/.venv \
    PYTHONPATH="$PYTHONPATH:/app" \
    LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib"
ENV PATH="$POETRY_PATH/bin:$VENV_PATH/bin:$PATH"

FROM python-base AS poetry
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    openssl \
    # deps for installing poetry
    curl \
    # deps for building python deps
    build-essential \
    libcurl4-openssl-dev libssl-dev && \
    pip install pip==21.2.4 && \
    # Install Poetry
    curl -sSL https://install.python-poetry.org | POETRY_HOME=$POETRY_PATH POETRY_VERSION=$POETRY_VERSION python3 - && \
    poetry --version && \
    poetry config virtualenvs.in-project true && \
    # cleanup
    rm -rf /var/lib/apt/lists/*

FROM poetry AS build

WORKDIR /app/

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./src/pyproject.toml ./src/poetry.lock* /app/

# Allow installing dev dependencies to run tests
COPY ./vendors /vendors

RUN poetry install --no-interaction --no-ansi --no-root --only main

FROM build AS develop

RUN poetry install --no-interaction --no-ansi --no-root

COPY ./src /app

ARG BUILD_HASH=
ARG BUILD_TAG=
ARG BUILD_DATE=

ENV SERVICE_INFO_HASH=$BUILD_HASH
ENV SERVICE_INFO_TAG=$BUILD_TAG
ENV SERVICE_INFO_DATE=$BUILD_DATE

CMD ["python", "-m", "deps_ai_fusion", "serve"]


FROM python-base AS runtime

WORKDIR /app

RUN apt-get update && apt-get install openssl -y

COPY --from=build $VENV_PATH $VENV_PATH
COPY ./vendors /vendors
COPY ./src /app

ARG BUILD_HASH=
ARG BUILD_TAG=
ARG BUILD_DATE=

ENV SERVICE_INFO_HASH=$BUILD_HASH
ENV SERVICE_INFO_TAG=$BUILD_TAG
ENV SERVICE_INFO_DATE=$BUILD_DATE

RUN useradd -Ms /bin/bash deps
USER deps

CMD ["python", "-m", "deps_ai_fusion", "serve"]

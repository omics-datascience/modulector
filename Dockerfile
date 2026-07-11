FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.8.23 /uv /uvx /bin/

RUN apt-get update \
    && apt-get install --no-install-recommends -y curl \
    && rm -rf /var/lib/apt/lists/*

# Default value for deploying with modulector DB image
ENV POSTGRES_USERNAME=modulector
ENV POSTGRES_PASSWORD=modulector
ENV POSTGRES_PORT=5432
ENV POSTGRES_DB=modulector

# App's folder creation
RUN mkdir /src
WORKDIR /src/
ENV BASEDIR=/src
ENV PATH="/src/.venv/bin:$PATH"
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install app Python dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# Copy source code and the data permitted for distribution.
COPY . .

# Gives execution permissions to run.sh
RUN chmod +x tools/run.sh

# Run app
CMD ["/bin/bash","-c","tools/run.sh"]

# Modulector API and MCP port
EXPOSE 8000 8001


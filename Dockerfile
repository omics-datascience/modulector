FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.8.23 /uv /uvx /bin/

# Default value for deploying with modulector DB image
ENV POSTGRES_USERNAME "modulector"
ENV POSTGRES_PASSWORD "modulector"
ENV POSTGRES_PORT 5432
ENV POSTGRES_DB "modulector"

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

# Copy all source data
COPY . .

RUN echo 0 > tools/healthcheck/tries.txt
HEALTHCHECK CMD python tools/healthcheck/check.py

# Gives execution permissions to run.sh
RUN chmod +x tools/run.sh

# Run app
CMD ["/bin/bash","-c","tools/run.sh"]

# Modulector port
EXPOSE 8000


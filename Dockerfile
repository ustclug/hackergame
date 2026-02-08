FROM python:3.11

RUN apt-get update && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PYTHONUNBUFFERED=1
WORKDIR /opt/hackergame
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project
# Bind project inside instead of copying it
# to avoid copying credentials inside container
# COPY ./ /opt/hackergame/

EXPOSE 2018
CMD ["docker/start.sh"]

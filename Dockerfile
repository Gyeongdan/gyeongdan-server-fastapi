FROM --platform=linux/amd64 python:3.11.4-slim-bookworm

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev libatlas-base-dev libomp-dev && \
    pip install --no-cache-dir pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy --ignore-pipfile

RUN apt-get purge -y --auto-remove gcc && \
    rm -rf /var/lib/apt/lists/*

COPY ./entrypoint.sh ./entrypoint.sh
COPY ./app ./app

ENV PORT=8000

ARG DB_HOST
ARG DB_USER
ARG DB_PASSWORD
ARG DB_NAME
ARG DB_PORT
ARG OPENAI_API_KEY
ARG GOOGLE_CSE_ID
ARG GOOGLE_API_KEY
ARG USER_AGENT

ENV DB_HOST=${DB_HOST}
ENV DB_USER=${DB_USER}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_NAME=${DB_NAME}
ENV DB_PORT=${DB_PORT}
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV GOOGLE_CSE_ID=${GOOGLE_CSE_ID}
ENV GOOGLE_API_KEY=${GOOGLE_API_KEY}
ENV USER_AGENT=${USER_AGENT}

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["/bin/sh", "-c", "./entrypoint.sh"]

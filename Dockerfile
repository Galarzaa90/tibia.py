FROM python:3.11-slim
RUN apt-get update \
    && apt-get install gcc curl -y \
    && apt-get clean
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY requirements-server.txt .
RUN pip install -r requirements-server.txt

LABEL maintainer="Allan Galarza <allan.galarza@gmail.com>"
LABEL org.opencontainers.image.licenses="Apache 2.0"
LABEL org.opencontainers.image.authors="Allan Galarza <allan.galarza@gmail.com>"
LABEL org.opencontainers.image.url="https://github.com/Galarzaa90/tibia.py"
LABEL org.opencontainers.image.source="https://github.com/Galarzaa90/tibia.py"
LABEL org.opencontainers.image.vendor="Allan Galarza <allan.galarza@gmail.com>"
LABEL org.opencontainers.image.title="tibia.py"
LABEL org.opencontainers.image.description="API that parses website content into python data."


COPY tibiapy/ tibiapy/
COPY server.py main.py
EXPOSE 8000
HEALTHCHECK --interval=60s --timeout=10s --start-period=5s --retries=5 \
  CMD curl --fail http://localhost:8000/healthcheck || exit 1
ENTRYPOINT ["fastapi", "run", "--port", "8000"]

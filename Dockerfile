FROM python:3.9-slim
RUN apt-get update \
    && apt-get install gcc -y \
    && apt-get clean
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt uvloop

LABEL maintainer="Allan Galarza <allan.galarza@gmail.com>"
LABEL org.opencontainers.image.licenses="Apache 2.0"
LABEL org.opencontainers.image.authors="Allan Galarza <allan.galarza@gmail.com>"
LABEL org.opencontainers.image.url="https://github.com/Galarzaa90/tibia.py"
LABEL org.opencontainers.image.source="https://github.com/Galarzaa90/tibia.py"
LABEL org.opencontainers.image.vendor="Allan Galarza <allan.galarza@gmail.com>"
LABEL org.opencontainers.image.title="tibia.py"
LABEL org.opencontainers.image.description="API that parses website content into python data."


COPY . .
RUN python setup.py install
EXPOSE 8000
CMD ["python", "serve.py"]
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt uvloop

COPY . .
RUN python setup.py install
EXPOSE 8000
CMD ["python", "serve.py"]
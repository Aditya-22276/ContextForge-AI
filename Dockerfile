FROM python:3.11

WORKDIR /app

COPY . .

WORKDIR /app/backend

RUN pip install -r requirements.txt

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
# FastAPI Backend Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn pydantic sqlalchemy requests

COPY . .

EXPOSE 8000

ENV USE_MOCK=true

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

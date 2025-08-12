# Use Python 3.10 to match the numpy wheels in requirements.txt
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "daiku.api:app", "--host", "0.0.0.0", "--port", "8000"]

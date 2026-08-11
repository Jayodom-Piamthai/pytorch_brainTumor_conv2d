FROM python:3.10-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ultralytics/opencv need these system libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

COPY requirement.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirement.txt

COPY . .

EXPOSE 8000
CMD ["sh", "-c", "uvicorn webAPI:app --host 0.0.0.0 --port ${PORT:-8000}"]
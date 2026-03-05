# 1. Use a lightweight Python image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Install system dependencies for OpenCV/Pillow if needed
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements first (optimization for Docker layers)
COPY requirements.txt .

# 5. Install Python dependencies
# Use --no-cache-dir to keep the image size small
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy your model and code into the container
COPY . .

# 7. Expose the port FastAPI runs on
EXPOSE 8000

# 8. Command to run the app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
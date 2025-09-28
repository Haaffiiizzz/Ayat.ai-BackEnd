# Use official Python image
FROM python:3.13-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt update && apt install -y git build-essential curl ffmpeg && rm -rf /var/lib/apt/lists/*


# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Expose port
EXPOSE 8000

# Run Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

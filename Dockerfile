# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY ./app ./app

# Set environment variable to run in production mode
ENV PYTHONUNBUFFERED=1

# Expose port 8000 for the FastAPI application
EXPOSE 8000

WORKDIR /app/app

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
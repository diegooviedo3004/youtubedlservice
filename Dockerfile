# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir flask flask-httpauth yt-dlp

# Copy application files
COPY . /app

# Create a directory for downloads
RUN mkdir -p /app/downloads

# Expose the application port
EXPOSE 5000

# Run the Flask application
CMD ["python", "app.py"]

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the application files
COPY . /app

# Install required packages
RUN pip install --no-cache-dir flask flask-httpauth yt-dlp

# Create a directory for downloads
RUN mkdir -p /app/downloads

# Expose the port the app runs on
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]

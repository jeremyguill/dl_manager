# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Install yt-dlp and other dependencies
# ffmpeg is needed by yt-dlp for video/audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install yt-dlp using pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY download_manager.py .

# Create an empty urls.txt if it doesn't exist, so the container starts without error
RUN touch urls.txt

# Command to run the application
CMD ["python", "download_manager.py"]

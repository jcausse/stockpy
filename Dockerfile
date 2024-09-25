# Base image: Use Python 3.12 slim to keep it lightweight
FROM python:3.12-slim

# Set environment variables to prevent Python from buffering outputs
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy dependencies file first to take advantage of Docker caching
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY src /app/src
COPY assets /app/assets

# Set the entry point to run the app
CMD ["python", "/app/src/main.py"]

# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies specified in requirements.txt
RUN pip install --no-cache-dir fastapi uvicorn requests aiohttp boto3 pandas numpy sqlalchemy asyncpg python-dotenv docker openai bs4 lxml

# Copy the rest of the application code into the container
COPY . .

# Command to run the main application
CMD ["python", "main.py"]

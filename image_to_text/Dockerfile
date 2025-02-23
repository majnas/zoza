# Use the official Python image as a base
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11-slim

# Install required dependencies
RUN apt-get update && apt-get install -y --no-install-recommends make curl

COPY requirements.txt req.txt
RUN pip install -r req.txt

# Set the working directory inside the container
WORKDIR /srv

# Copy the entire project into the container
COPY . /srv

# Set environment variable to avoid bytecode cache
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden in CI)
CMD ["bash"]

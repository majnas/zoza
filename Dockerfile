# Use the official Python image as a base
FROM python:3.12-slim

# Install required dependencies
RUN apt-get update && apt-get install -y --no-install-recommends make git iputils-ping curl supervisor

# Set the working directory inside the container
WORKDIR /app

# Copy the entire project into the container
COPY . /app
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set environment variable to avoid bytecode cache
ENV PYTHONUNBUFFERED=1

# Default command (can be overridden in CI)
# CMD ["bash"]
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

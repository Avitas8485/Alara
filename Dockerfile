# Use a smaller base image
FROM python:3.11-slim-bookworm AS builder

WORKDIR /alara

# Install build dependencies and clean up APT cache afterwards
RUN apt-get update && apt-get install -y \
    build-essential \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Runtime image
FROM python:3.11-slim-bookworm

WORKDIR /alara

# Create a non-root user and switch to it
RUN useradd -m myuser
USER myuser

# Copy only necessary files from the builder stage
COPY --from=builder /alara /alara

# Set the command to run the application
CMD ["python", "./main.py"]
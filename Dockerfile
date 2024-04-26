# FIXME: This doesn't work yet, but it's a start
# Use a smaller base image
FROM python:3.11-slim-bookworm AS builder

WORKDIR /alara

# Install build dependencies and clean up APT cache afterwards
RUN apt-get update && apt-get install -y \
    build-essential \
    portaudio19-dev \
    libportaudio2 \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

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

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Update PATH environment variable
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application code
COPY --from=builder /alara .



# Set the command to run the application
# for debugging purposes
CMD ["bash"]
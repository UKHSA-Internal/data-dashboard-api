# Build stage
FROM python:3.11-slim AS builder

# Install toolchain needed for C libraries like psycopg2 & create python virtual environment
COPY requirements-prod.txt requirements-prod.txt
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && python3 -m venv /venv \
    && rm -rf /var/cache/apt/* /var/lib/apt/lists/*

# Ensure the virtual environment is made available on the system `PATH`
ENV PATH=/venv/bin:$PATH

# Mounts the application code to the image
COPY . code
WORKDIR /code

# Install project dependencies into the virtual environment
RUN pip install --no-cache-dir -r requirements-prod.txt

# Runtime stage
FROM python:3.11-slim AS production

# Copy the virtual environment & application code
COPY --from=builder /venv /venv
COPY --from=builder /code /code

# Ensure the virtual environment is made available on the system `PATH`
ENV PATH=/venv/bin:$PATH
WORKDIR /code

EXPOSE 8000

# Adds execution permission for the entrypoint shell script
RUN chmod +x entrypoint.sh

# Opens a shell on the entrypoint, allowing the `entrypoint.sh` shell script or any other tool to be ran
ENTRYPOINT ["/bin/bash"]

# Runs the production server by default
CMD ["./entrypoint.sh"]

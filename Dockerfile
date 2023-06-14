# Build stage
FROM python:3.11-slim AS builder

# Ensure the virtual environment will be available on the `PATH` variable
ENV PATH=/venv/bin:$PATH

# Copy the production-only dependencies into place
COPY requirements-prod.txt requirements-prod.txt

# 1: Update the database of available packages
# 2: Install toolchain needed for C libraries like `psycopg2`
# 3: Create the python virtual environment
# 4: Remove dangling files from installation of libraries
# 5: Install project dependencies onto the virtual environment
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && python3 -m venv /venv \
    && rm -rf /var/cache/apt/* /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements-prod.txt

# Mounts the application code to the image
COPY . code

# Runtime stage
FROM python:3.11-slim AS production

WORKDIR /code

# Copy the virtual environment & application code
COPY --from=builder /venv /venv
COPY --from=builder /code /code

# Ensure the virtual environment is made available on the system `PATH`
ENV PATH=/venv/bin:$PATH

EXPOSE 8000

# Adds execution permission for the entrypoint shell script
RUN chmod +x entrypoint.sh

# Opens a shell on the entrypoint, allowing the `entrypoint.sh` shell script or any other tool to be ran
ENTRYPOINT ["/bin/bash"]

# Runs the production server by default
CMD ["./entrypoint.sh"]

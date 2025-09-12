###############################################################################
# Build stage
###############################################################################
# Default arguments
# This version is hardcoded but ideally it should pull from the `.python-version`
# When bumping Python versions, we currently have to update the `.python-version` file and this `ARG`
ARG PYTHON_VERSION=3.13.7

FROM python:${PYTHON_VERSION}-slim AS build

# Ensure the virtual environment will be available on the `PATH` variable
ENV PATH=/venv/bin:$PATH

# Copy the production-only dependencies into place
COPY requirements-prod.txt requirements-prod.txt
COPY requirements-prod-ingestion.txt requirements-prod-ingestion.txt

# Main build process
RUN apt-get update \
    # Update the database of available packages
    && apt-get -y install libpq-dev gcc \
    # Install toolchain needed for C libraries like `psycopg2` \
    chromium \
        # Chromium browser for Kaleido
        chromium-driver \
        # ChromeDriver for browser automation
        # Additional dependencies that Chromium might need in a headless environment
        libnss3 \
        libnspr4 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libdbus-1-3 \
        libatspi2.0-0 \
        libx11-6 \
        libxcomposite1 \
        libxdamage1 \
        libxext6 \
        libxfixes3 \
        libxrandr2 \
        libgbm1 \
        libxcb1 \
        libxkbcommon0 \
        libpango-1.0-0 \
        libcairo2 \
        libasound2 \
    && python3 -m venv /venv \
    # Create the python virtual environment
    && rm -rf /var/cache/apt/* /var/lib/apt/lists/* \
    # Remove dangling files from installation of libraries
    && pip install --upgrade pip \
    # Upgrade the pip installer to the latest version
    && pip install --no-cache-dir -r requirements-prod.txt
    # Install project dependencies onto the virtual environment

# Mounts the application code into the image
COPY . code

###############################################################################
# Production stage
###############################################################################
FROM python:${PYTHON_VERSION}-slim AS production

# Sets the working directory for subsequent `RUN`, `ENTRYPOINT` & `CMD` layers
WORKDIR /code

# Copy the virtual environment & application code from the `build` stage
COPY --from=build /venv /venv
COPY --from=build /code /code

# Ensure the virtual environment is made available on the system `PATH`
ENV PATH=/venv/bin:$PATH

# Listen on the specified port at runtime
# Note that this does not actually publish the port.
# This also assumes TCP.
EXPOSE 8000

# Install runtime dependencies including Chromium for Kaleido
RUN apt-get update \
    # Update the database of available packages
    && apt-get -y install \
        libpq-dev \
        # C library needed for `psycopg2`
        chromium \
        # Chromium browser for Kaleido
        chromium-driver \
        # ChromeDriver for browser automation
        # Additional dependencies that Chromium might need in a headless environment
        libnss3 \
        libnspr4 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libdbus-1-3 \
        libatspi2.0-0 \
        libx11-6 \
        libxcomposite1 \
        libxdamage1 \
        libxext6 \
        libxfixes3 \
        libxrandr2 \
        libgbm1 \
        libxcb1 \
        libxkbcommon0 \
        libpango-1.0-0 \
        libcairo2 \
        libasound2 \
    && rm -rf /var/cache/apt/* /var/lib/apt/lists/* \
    # Clean up apt cache to reduce image size
    && chmod +x entrypoint.sh
    # Add execution permission for the entrypoint shell script


# Set environment variables for Chromium to run in headless mode
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMIUM_FLAGS="--no-sandbox --headless --disable-gpu --disable-dev-shm-usage"


# Opens a shell on the entrypoint.
# This allows the `entrypoint.sh` shell script or any other tooling to be ran from the container
ENTRYPOINT ["/bin/bash"]

# Runs the production server by default
CMD ["./entrypoint.sh"]

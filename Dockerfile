###############################################################################
# Build stage
###############################################################################
# Default arguments
# This version is hardcoded but ideally it should pull from the `.python-version`
# When bumping Python versions, we currently have to update the `.python-version` file and this `ARG`
ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim AS build

# Declare the non-root user
ARG USER_NAME=ukhsa_user
ARG GROUP_NAME=ukhsa_group

# Ensure the virtual environment will be available on the `PATH` variable
ENV PATH=/venv/bin:$PATH

# Create a non-root user and group
RUN groupadd -r ${GROUP_NAME} && useradd -r -g ${GROUP_NAME} ${USER_NAME}

# Copy the production-only dependencies into place
COPY requirements-prod.txt requirements-prod.txt

# Main build process
RUN apt-get update \
    # Update the database of available packages
    && apt-get -y install libpq-dev gcc \
    # Install toolchain needed for C libraries like `psycopg2`
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

# Redeclare the non-root user
ARG USER_NAME=ukhsa_user
ARG GROUP_NAME=ukhsa_user

# Create a non-root user and group
RUN groupadd -r ${GROUP_NAME} && useradd -r -g ${GROUP_NAME} ${USER_NAME}

# Copy the virtual environment & application code from the `build` stage
COPY --from=build /venv /venv
COPY --from=build /code /code

# Ensure the virtual environment is made available on the system `PATH`
ENV PATH=/venv/bin:$PATH

# Listen on the specified port at runtime
# Note that this does not actually publish the port.
# This also assumes TCP.
EXPOSE 8000

# Reinstall system libraries required for PostgreSQL drivers
RUN apt-get update \
    # Update the database of available packages
    && apt-get -y install libpq-dev \
    # Reinstall the C library needed for `psycopg2`
    && chmod +x entrypoint.sh \
    # Add execution permission for the entrypoint shell script
    && chown -R ${USER_NAME}:${USER_NAME} /code
    # Add permission for the non-root user

# Switch to the non-root user
USER ${USER_NAME}

# Opens a shell on the entrypoint.
# This allows the `entrypoint.sh` shell script or any other tooling to be ran from the container
ENTRYPOINT ["/bin/bash"]

# Runs the production server by default
CMD ["./entrypoint.sh"]

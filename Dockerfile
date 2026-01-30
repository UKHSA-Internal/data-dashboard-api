# syntax=docker/dockerfile:1

###############################################################################
# Build stage (Debian-based)
###############################################################################
# Default arguments
# This version is hardcoded but ideally it should pull from the `.python-version`
# When bumping Python versions, we currently have to update the `.python-version` file and this `ARG`
ARG PYTHON_VERSION=3.12.6

FROM python:${PYTHON_VERSION}-slim-bookworm AS build

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy the production-only dependencies into place
COPY requirements-prod.txt requirements-prod.txt
COPY requirements-prod-ingestion.txt requirements-prod-ingestion.txt

# Build the runtime bundle and Python deps via a dedicated script, so the
# Dockerfile stays readable and the build logic can be tested/iterated on.
COPY docker/build_distroless_runtime.sh /usr/local/bin/build_distroless_runtime.sh
RUN bash /usr/local/bin/build_distroless_runtime.sh

# Mounts the application code into the image
COPY . /code

###############################################################################
# Production stage (distroless)
###############################################################################
FROM gcr.io/distroless/base-debian12:nonroot-arm64 AS production

# Sets the working directory for subsequent `RUN`, `ENTRYPOINT` & `CMD` layers
WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/usr/local/bin:/usr/bin:/bin \
    LD_LIBRARY_PATH=/lib/aarch64-linux-gnu:/usr/lib/aarch64-linux-gnu \
    PYTHONPATH=/opt/python

# Copy dependencies and app code from the `build` stage.
COPY --from=build /opt/runtime-libs/ /
COPY --from=build /usr/local /usr/local
COPY --from=build /opt/python /opt/python
COPY --chown=nonroot:nonroot --from=build /code /code

# Listen on the specified port at runtime.
EXPOSE 8000

# # Reinstall system libraries required for PostgreSQL drivers
# RUN apt-get update \
#     # Update the database of available packages
#     && apt-get -y install libpq-dev \
#     # Reinstall the C library needed for `psycopg2`
#     && chmod +x entrypoint.sh
#     # Add execution permission for the entrypoint shell script

# Opens a shell on the entrypoint.
# This allows the `entrypoint.sh` shell script or any other tooling to be ran from the container
ENTRYPOINT ["/bin/bash"]

# Runs the production server by default
CMD ["./docker/entrypoint.sh"]


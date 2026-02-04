# syntax=docker/dockerfile:1

###############################################################################
# Build stage (Debian-based)
###############################################################################
ARG PYTHON_VERSION=3.12.6

FROM python:${PYTHON_VERSION}-slim-bookworm AS build

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy the production-only dependencies into place
COPY requirements-prod.txt requirements-prod.txt
COPY requirements-prod-ingestion.txt requirements-prod-ingestion.txt

# Build runtime bundle and collect shared library deps via dedicated script.
COPY docker/build_distroless_runtime.sh /usr/local/bin/build_distroless_runtime.sh
RUN bash /usr/local/bin/build_distroless_runtime.sh

# Mounts the application code into the image
COPY . /code

###############################################################################
# Production stage (distroless)
###############################################################################
FROM gcr.io/distroless/cc-debian12:nonroot AS production

ARG PYTHON_VERSION=3.12.6

WORKDIR /code

# Copy dependencies and app code from the `build` stage.
COPY --from=build /usr/local/lib/ /usr/local/lib/
COPY --from=build /usr/local/bin/ /usr/local/bin/
COPY --from=build /deps/ /

# zsh, bash and minimal coreutils required by our entrypoint tooling
# bash is needed for kaleido's wrapper script
COPY --from=build /usr/bin/zsh /usr/bin/zsh
COPY --from=build /bin/bash /bin/bash
COPY --from=build /usr/bin/dirname /usr/bin/dirname

# Application code
COPY --chown=nonroot:nonroot --from=build /code /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONUNBUFFERED 1
ENV PATH /usr/local/bin:/usr/bin:/bin

EXPOSE 8000

# Opens a shell on the entrypoint.
# This allows the `./docker/entrypoint.sh` shell script or any other tooling to be ran from the container
ENTRYPOINT ["/usr/bin/zsh"]

# Runs the production server by default
CMD ["./docker/entrypoint.sh"]
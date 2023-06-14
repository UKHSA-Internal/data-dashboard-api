FROM python:3.11-slim as base

# Install toolchain & create python virtual environment
COPY requirements-prod.txt requirements-prod.txt
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && python3 -m venv /venv

ENV PATH=/venv/bin:$PATH

# Mounts the application code to the image
COPY . code
WORKDIR /code

# Install project dependencies into the virtual environment
RUN pip install --no-cache-dir -r requirements-prod.txt

EXPOSE 8000

# Adds execution permission for the entrypoint shell script
RUN chmod +x entrypoint.sh

# Opens a shell on the entrypoint, allowing the `entrypoint.sh` shell script or any other tool to be ran
ENTRYPOINT ["/bin/bash"]

# Runs the production server by default
CMD ["./entrypoint.sh"]

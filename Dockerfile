FROM python:3.8

# Allows docker to cache installed dependencies between builds
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Mounts the application code to the image
COPY . code
WORKDIR /code

EXPOSE 8000

# Adds execution permission for the entrypoint shell script
RUN chmod +x entrypoint.sh

# Runs the production server
ENTRYPOINT ./entrypoint.sh

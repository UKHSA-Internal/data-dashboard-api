FROM python:3.11

# Allows docker to cache installed dependencies between builds
COPY requirements-prod.txt requirements-prod.txt
RUN pip install --no-cache-dir -r requirements-prod.txt

# Mounts the application code to the image
COPY . code
WORKDIR /code

EXPOSE 8000

# Adds execution permission for the entrypoint shell script
RUN chmod +x entrypoint.sh


ENTRYPOINT ["/bin/bash"]

# Runs the production server by default
CMD ["./entrypoint.sh"]

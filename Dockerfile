FROM python:3.11

# ADD wpapi/main.py .
WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./wpapi .
COPY ./tests /tests
COPY ./start.sh .

RUN chmod +x start.sh

EXPOSE 80

ENTRYPOINT ["start.sh"]

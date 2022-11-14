FROM python:3.11

# ADD wpapi/main.py .
WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./wpapi .
COPY ./start.sh .
COPY ./start_local.sh .

RUN chmod +x ./start.sh
RUN chmod +x ./start_local.sh

EXPOSE 5000

ENTRYPOINT ["/app/start.sh"]

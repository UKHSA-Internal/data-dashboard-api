FROM python:3.11

# ADD wpapi/main.py .
WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./wpapi .
COPY ./tests /tests
COPY ./start.sh /opt
COPY ./start_local.sh /opt
COPY ./.env /opt

RUN chmod +x /opt/start.sh
RUN chmod +x /opt/start_local.sh

EXPOSE 5000

ENTRYPOINT ["/opt/start.sh"]

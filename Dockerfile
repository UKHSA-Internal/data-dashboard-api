FROM python:3.11

# ADD wpapi/main.py .
WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./wpapi ./opt
COPY ./tests /tests
COPY ./start.sh ./opt

RUN chmod +x opt/start.sh

EXPOSE 80

ENTRYPOINT ["start.sh"]

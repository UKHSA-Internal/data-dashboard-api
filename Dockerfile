FROM python:3.10
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
COPY ./start.sh ./code/start.sh
RUN chmod +x ./code/start.sh
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./wpapi /code/wpapi
CMD ["./start.sh"]

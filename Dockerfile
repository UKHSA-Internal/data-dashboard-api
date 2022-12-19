FROM python:3.10
WORKDIR /code

ARG POSTGRES_DB
ENV POSTGRES_DB ${POSTGRES_DB}
ARG POSTGRES_DB
ENV POSTGRES_DB ${POSTGRES_DB}
ARG POSTGRES_DB
ENV POSTGRES_DB ${POSTGRES_DB}
ARG POSTGRES_DB
ENV POSTGRES_DB ${POSTGRES_DB}


COPY ./requirements.txt /code/requirements.txt
COPY ./start.sh ./code/start.sh
RUN chmod +x ./code/start.sh
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./wpapi /code/wpapi
CMD ["./code/start.sh"]

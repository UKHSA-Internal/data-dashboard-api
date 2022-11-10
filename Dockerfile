FROM python:3.10
ADD wpapi/main.py .

#RUN pip install --upgrade pip
RUN pip3 install fastapi 
RUN pip3 install typing
RUN pip3 install pydantic 

CMD [“python”,”./main.py”]


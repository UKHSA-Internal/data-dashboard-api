FROM python:3.10
ADD main.py .

#RUN pip install --upgrade pip
RUN pip install from fastapi import FastAPI==0.86.0
RUN pip install from typing import Union
RUN pip install from pydantic import BaseModel

CMD [“python”,”./main.py”]


FROM pytorch/pytorch:latest

RUN mkdir /app
COPY app/* /app/
COPY .env /app/
COPY requirements.txt /app/

WORKDIR /app
RUN pip3 install --default-timeout=900 -r requirements.txt

ENTRYPOINT python server.py

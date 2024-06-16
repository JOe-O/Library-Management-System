FROM python:3.9-slim

USER root

WORKDIR /app

RUN apt update && apt install -y inetutils-ping

COPY . .

RUN pip install -r requirements

EXPOSE 5000

CMD [ "python3", "app.py" ]
FROM debian:bookworm-slim

ADD app /opt/app/

RUN apt-get update; apt-get -y upgrade; apt-get -y install python3 pip python3.11-venv; \
     python3 -m venv /opt/app/venv
 
WORKDIR /opt/app

CMD . /opt/app/venv/bin/activate && exec uvicorn main:app


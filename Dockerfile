FROM python:3.13.0a1-bookworm

COPY app /opt

RUN pip install -r /opt/app/requirements.txt
WORKDIR /opt/app

CMD [ "uvicorn --port 8000  --host 0.0.0.0  main:app" ]


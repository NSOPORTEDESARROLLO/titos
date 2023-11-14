#!/bin/bash

chown -R nsuser:nsgroup /opt/app

exec /usr/bin/python3 -m  uvicorn --port $PORT  --host $BIND main:app
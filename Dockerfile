FROM debian:bookworm-slim

ADD app /opt/app/
ADD dockerfiles/ns-start.sh /usr/bin/

ENV PORT="8000"
ENV BIND="0.0.0.0"


RUN apt-get update; apt-get -y upgrade; apt-get -y install python3 pip \
     python3-uvicorn python3-fastapi python3-filetype; addgroup --gid 10000 nsgroup; \
     adduser --gecos "Nsoporte User" --disabled-password nsuser --uid 10000 --gid 10000; \
     chown -R nsuser:nsgroup /opt/app;chmod +x /usr/bin/ns-start.sh

 
WORKDIR /opt/app
USER nsuser

CMD [ "/usr/bin/ns-start.sh" ]


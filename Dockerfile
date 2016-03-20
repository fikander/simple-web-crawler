
FROM ubuntu:trusty
MAINTAINER Tomasz Kustrzynski

# Update Ubuntu
RUN echo "deb http://archite.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y tar git curl nano wget dialog net-tools build-essential

# Install Python 3 tools
RUN apt-get install -y python3 python3-dev python3-pip python3-psycopg2

# Copy application folder inside the container
ADD /web-crawler /web-crawler

RUN pip3 install -r /web-crawler/requirements.txt

VOLUME /logs

WORKDIR /web-crawler

CMD python3 server.py >> /logs/server.log 2>&1

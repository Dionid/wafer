FROM ubuntu:16.04
MAINTAINER Dmitry Levin "me@playertwo.ru"

RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential locales
RUN locale-gen en_US.UTF-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

RUN pip3 install --upgrade pip
RUN pip3 install Flask netifaces
COPY server /wafer_server
WORKDIR /wafer_server
#RUN pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["server.py"]

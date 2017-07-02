FROM ubuntu:16.04
MAINTAINER Dmitry Levin "me@playertwo.ru"

RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential locales libssl-dev
RUN locale-gen en_US.UTF-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

RUN pip3 install --upgrade pip
#RUN pip3 install Flask netifaces

ENV OPENSSL_LIBDIR==lib/x86_64-linux-gnu
#RUN pip3 install -r requirements.txt
RUN pip3 install netifaces \
flask==0.12 \
web3==3.8.1  \
pysha3==1.0.2 \
gunicorn==19.7.1 \
eth-testrpc==1.2.0 \
ethereum==1.6.1 \
ethereum-abi-utils==0.4.0 \
ethereum-client-utils==0.3.2 \
ethereum-rpc-client==0.4.4 \
ethereum-utils==0.2.0 \
ethjsonrpc==0.3.0 \
bugsnag==3.1.1 \
blinker==1.4
COPY server /wafer_server
WORKDIR /wafer_server
ENTRYPOINT ["python3"]
CMD ["server.py"]

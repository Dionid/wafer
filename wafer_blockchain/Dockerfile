FROM ubuntu:16.04
MAINTAINER Dmitry Levin "me@playertwo.ru"
RUN apt update -y
#
RUN apt install -y curl
#RUN apt install -y python-dev
#RUN /bin/sh -c "curl -sL https://deb.nodesource.com/setup_8.x | bash -"
#RUN apt update -y
#RUN apt install -y nodejs

RUN /bin/sh -c "curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -"
RUN /bin/sh -c "echo 'deb https://dl.yarnpkg.com/debian/ stable main' | tee /etc/apt/sources.list.d/yarn.list"
RUN apt install -y libssl-dev
RUN apt install -y libzmq3-dev
RUN apt install -y apt-transport-https
RUN apt update -y


RUN apt install -y yarn
COPY wafer_contracts /opt/wafer_contracts
WORKDIR /opt/wafer_contracts
RUN apt install -y software-properties-common
RUN apt install -y git
RUN apt install -y build-essential
RUN /bin/sh -c "curl -sL https://deb.nodesource.com/setup_8.x | bash -"
RUN apt update -y
RUN apt install -y nodejs
RUN apt install -y curl  libssl-dev libzmq3-dev software-properties-common apt-transport-https git make build-essential
RUN apt install -y python-dev
RUN yarn install
ENTRYPOINT ["./run_testrpc.sh"]

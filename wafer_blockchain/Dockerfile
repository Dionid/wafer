FROM ubuntu:16.04
MAINTAINER Dmitry Levin "me@playertwo.ru"
RUN apt update -y
RUN apt install -y curl apt-transport-https libssl-dev libzmq3-dev software-properties-common git python-dev make build-essential

RUN /bin/sh -c "curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -"
RUN /bin/sh -c "echo 'deb https://dl.yarnpkg.com/debian/ stable main' | tee /etc/apt/sources.list.d/yarn.list"
RUN /bin/sh -c "curl -sL https://deb.nodesource.com/setup_8.x | bash -"
RUN apt update -y
RUN apt install -y yarn nodejs

COPY wafer_contracts /opt/wafer_contracts
WORKDIR /opt/wafer_contracts
RUN yarn install
ENTRYPOINT ["./run_testrpc.sh"]

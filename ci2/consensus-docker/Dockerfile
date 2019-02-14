FROM microsoft/dotnet:2.1-sdk
# Install dependencies:
RUN apt-get update && apt-get install -y \
    libleveldb-dev \
    sqlite3 \
    libsqlite3-dev \
    libunwind8-dev \
    wget \
    expect \
    screen \
    zip \
    openssh-server \
    python3 \
    psmisc \
    python3-pip \
    libssl-dev \
    expect
RUN pip3 install requests \
    websocket-client \
    base58 \
    ddt \
    cffi \
    werkzeug \
    json-rpc \
    leveldb \
    setproctitle \
    paramiko \
    numpy \
    pexpect
RUN echo "root:123" | chpasswd
WORKDIR /opt
ADD ci2/Test-master /opt/Test-master
RUN mkdir /opt/nodes
RUN chmod +x /opt/Test-master/consensus.sh
RUN chmod +x /opt/Test-master/init.sh
RUN chmod +x /opt/Test-master/service/run.sh
WORKDIR /opt/Test-master
CMD ./consensus.sh


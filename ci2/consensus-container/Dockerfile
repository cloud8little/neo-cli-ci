FROM kickseason/dotnetandpython:latest
COPY ci2/sshd_config /etc/ssh/
WORKDIR /home/neo
ADD ci2/neo-test neo-test/
RUN mkdir nodes
RUN chmod +x neo-test/service/run.sh
WORKDIR neo-test/service
CMD /etc/init.d/ssh start & ./run.sh


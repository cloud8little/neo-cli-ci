FROM kickseason/dotnetandpython:latest
COPY ci2/sshd_config /etc/ssh/
WORKDIR /home/neo
ADD ci2/Test-master Test-master/
RUN mkdir nodes
RUN chmod +x Test-master/service/run.sh
WORKDIR Test-master/service
CMD /etc/init.d/ssh start & ./run.sh


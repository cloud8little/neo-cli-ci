FROM kickseason/dotnetandpython:latest
COPY ci2/sshd_config /etc/ssh/
WORKDIR /home/neo
ADD ci2/NEO-TEST NEO-TEST/
RUN mkdir nodes
RUN chmod +x NEO-TEST/service/run.sh
WORKDIR NEO-TEST/service
CMD /etc/init.d/ssh start & ./run.sh


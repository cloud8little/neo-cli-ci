FROM cloud8little/dotnetandpython:neo
WORKDIR /home/neo
ADD ./neo-test neo-test/
RUN mkdir nodes
RUN chmod +x neo-test/service/run.sh
WORKDIR neo-test/service
CMD /etc/init.d/ssh start & ./run.sh


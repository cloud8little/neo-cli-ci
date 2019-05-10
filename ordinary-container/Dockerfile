FROM kickseason/dotnetandpython:latest
WORKDIR /home/neo
RUN mkdir nodes
# add test framework
ADD ./neo-test neo-test/
RUN chmod +x neo-test/service/run_output.sh
RUN chmod +x neo-test/run_test.sh
RUN chmod +x neo-test/src/test/run_test.sh
# prepare neo-cli
ADD pack.sh .
ADD Plugins .
RUN chmod +x pack.sh
RUN ./pack.sh
RUN tar -C neo-cli -zcvf neo-cli.tar.gz .
RUN cp neo-cli.tar.gz /home/neo/neo-test/src/resource/nodes/
RUN cp neo-cli.tar.gz /home/neo/neo-test/src/resource/nodes/neo-cli2.tar.gz
WORKDIR /home/neo/neo-test/
CMD ./run_test.sh

FROM kickseason/dotnetandpython:latest
COPY ci2/sshd_config /etc/ssh/
WORKDIR /home/neo
ADD ci2/neo-test neo-test/
RUN mkdir nodes
RUN chmod +x neo-test/service/run_output.sh
RUN chmod +x neo-test/run_test.sh
RUN chmod +x neo-test/src/test/run_test.sh
ADD neo-cli neo-cli/
WORKDIR neo-cli
RUN dotnet restore
RUN dotnet publish -c Release
WORKDIR /home/neo/neo-cli/bin/Release/netcoreapp2.1/publish
RUN tar -cvf neo-cli.tar.gz ./*
RUN cp neo-cli.tar.gz /home/neo/neo-test/src/resource/nodes/
RUN cp neo-cli.tar.gz /home/neo/neo-test/src/resource/nodes/neo-cli2.tar.gz
WORKDIR /home/neo/neo-test/
CMD ./run_test.sh

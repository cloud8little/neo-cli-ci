FROM kickseason/dotnetandpython:latest
COPY ci2/sshd_config /etc/ssh/
WORKDIR /home/neo
ADD ci2/NEO-TEST NEO-TEST/
RUN mkdir nodes
RUN chmod +x NEO-TEST/service/run_output.sh
RUN chmod +x NEO-TEST/run_test.sh
RUN chmod +x NEO-TEST/src/test/run_test.sh
ADD neo-cli neo-cli/
WORKDIR neo-cli
RUN dotnet restore
RUN dotnet publish -c Release
WORKDIR /home/neo/neo-cli/bin/Release/netcoreapp2.1/publish
RUN tar -cvf neo-cli.tar.gz ./*
RUN cp neo-cli.tar.gz /home/neo/NEO-TEST/src/resource/nodes/
RUN cp neo-cli.tar.gz /home/neo/NEO-TEST/src/resource/nodes/neo-cli2.tar.gz
WORKDIR /home/neo/NEO-TEST/
CMD ./run_test.sh

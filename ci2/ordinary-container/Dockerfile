FROM kickseason/dotnetandpython:latest
COPY ci2/sshd_config /etc/ssh/
WORKDIR /home/neo
ADD ci2/Test-master Test-master/
RUN mkdir nodes
RUN chmod +x Test-master/service/run_output.sh
RUN chmod +x Test-master/ordinary.sh
ADD neo-cli neo-cli/
WORKDIR neo-cli
RUN dotnet restore
RUN dotnet publish -c Release
WORKDIR /home/neo/neo-cli/bin/Release/netcoreapp2.1/publish
RUN tar -cvf neo-cli.tar.gz ./*
RUN cp neo-cli.tar.gz /home/neo/Test-master/src/resource/nodes/
RUN cp neo-cli.tar.gz /home/neo/Test-master/src/resource/nodes/neo-cli2.tar.gz
WORKDIR /home/neo/Test-master/
CMD ./ordinary.sh

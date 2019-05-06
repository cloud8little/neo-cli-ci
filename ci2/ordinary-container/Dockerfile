FROM kickseason/dotnetandpython:latest
WORKDIR /home/neo
RUN mkdir nodes
RUN mkdir neo-cli-build
# add test framework
ADD ci2/neo-test neo-test/
RUN chmod +x neo-test/service/run_output.sh
RUN chmod +x neo-test/run_test.sh
RUN chmod +x neo-test/src/test/run_test.sh
# build neo-cli
ADD neo-cli neo-cli/
WORKDIR neo-cli
#RUN dotnet restore
#RUN dotnet publish -c Release
#WORKDIR /home/neo/neo-cli/bin/Release/netcoreapp2.1/publish
#RUN mv ./* /home/neo/neo-cli-build
# tar neo-cli
# Jessica modify
RUN wget https://github.com/neo-project/neo-cli/releases/download/v2.10.2-preview3/neo-cli-linux-x64-preview.zip
RUN unzip neo-cli-linux-x64-preview.zip
RUN cd neo-cli-preview
RUN tar -zcvf neo-cli.tar.gz ./*
#WORKDIR /home/neo/neo-cli-build
#RUN tar -cvf neo-cli.tar.gz ./*
RUN cp neo-cli.tar.gz /home/neo/neo-test/src/resource/nodes/
RUN cp neo-cli.tar.gz /home/neo/neo-test/src/resource/nodes/neo-cli2.tar.gz
WORKDIR /home/neo/neo-test/
CMD ./run_test.sh

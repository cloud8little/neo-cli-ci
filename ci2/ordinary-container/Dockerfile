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
RUN dotnet restore
RUN dotnet publish -c Release
WORKDIR /home/neo/neo-cli/bin/Release/netcoreapp2.1/publish
RUN mv ./* /home/neo/neo-cli-build
WORKDIR /home/neo/neo-cli-build
RUN mkdir Plugins
# build plugins
WORKDIR /home/neo
RUN git clone https://github.com/neo-project/neo-plugins.git
WORKDIR ./neo-plugins
# RUN dotnet publish -c Release --framework netstandard2.0 RpcWallet/
# RUN cp -rf RpcWallet/bin/Release/netstandard2.0/RpcWallet.dll /home/neo/neo-cli-build/Plugins
RUN dotnet publish -c Release --framework netstandard2.0 ImportBlocks/
RUN cp -rf ImportBlocks/bin/Release/netstandard2.0/ImportBlocks.dll ImportBlocks/bin/Release/netstandard2.0/ImportBlocks /home/neo/neo-cli-build/Plugins/
RUN dotnet publish -c Release --framework netstandard2.0 SimplePolicy/
RUN cp -rf SimplePolicy/bin/Release/netstandard2.0/SimplePolicy.dll SimplePolicy/bin/Release/netstandard2.0/SimplePolicy /home/neo/neo-cli-build/Plugins/
RUN dotnet publish -c Release --framework netstandard2.0 ApplicationLogs/
RUN cp -rf ApplicationLogs/bin/Release/netstandard2.0/ApplicationLogs.dll ApplicationLogs/bin/Release/netstandard2.0/ApplicationLogs /home/neo/neo-cli-build/Plugins/
# tar neo-cli
WORKDIR /home/neo/neo-cli-build
RUN tar -cvf neo-cli.tar.gz ./*
RUN cp neo-cli.tar.gz /home/neo/neo-test/src/resource/nodes/
RUN cp neo-cli.tar.gz /home/neo/neo-test/src/resource/nodes/neo-cli2.tar.gz
WORKDIR /home/neo/neo-test/
CMD ./run_test.sh
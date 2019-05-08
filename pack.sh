#!/bin/bash
CLIVERSION="v2.10.2-preview3"
PLUGINS=("SimplePolicy@v2.10.1" "ImportBlocks@v2.10.1")
# download neo-cli
if [[ $CLIVERSION =~ "preview" ]] 
then
    CLIURL="https://github.com/neo-project/neo-cli/releases/download/"${CLIVERSION}"/neo-cli-linux-x64-preview.zip"
else
    CLIURL="https://github.com/neo-project/neo-cli/releases/download/"${CLIVERSION}"/neo-cli-linux-x64.zip"
fi

wget $CLIURL

if [[ $CLIVERSION =~ "preview" ]] 
then
    unzip neo-cli-linux-x64-preview.zip
    mv neo-cli-preview neo-cli
else
    unzip neo-cli-linux-x64.zip
fi
cd neo-cli
mkdir Plugins
# install plugins
# https://github.com/neo-project/neo-plugins/releases/download/v2.10.1/ApplicationLogs.zip

for plugin in ${PLUGINS[@]} 
do
    name=${plugin%%@*}
    version=${plugin##*@}
    wget "https://github.com/neo-project/neo-plugins/releases/download/"${version}"/"${name}".zip"
    unzip ${name}.zip
    rm ${name}.zip
done
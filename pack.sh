#!/bin/bash
PATH=$(pwd)
CLIVERSION="v2.10.2-preview3"
# release - will use the zip package from neo web portal
# local - will use the tar.gz file from local file under cloud8little: neo-cli-ci/neo-cli.tar.gz
NEO_CLI_OPTION="release"
# install - will install plugins when start neo-cli;
# local - will use the Plugins file from local file under cloud8little: neo-cli-cli/Plugins;
PLUGINS_OPTION="install"

PLUGINS=("SimplePolicy@v2.10.1" "ImportBlocks@v2.10.1" "RpcWallet@v2.10.1")
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

if [[ $PLUGINS_OPTION == "install" ]]
then
    for plugin in ${PLUGINS[@]} 
    do
        name=${plugin%%@*}
        version=${plugin##*@}
        wget "https://github.com/neo-project/neo-plugins/releases/download/"${version}"/"${name}".zip"
        unzip ${name}.zip
        rm ${name}.zip
    done
else
    dir=$(ls -l $PATH |awk '/^d/ {print $NF}')
    for file in $dir
    do
        if $file == "Plugins"
            cp -r $PATH/Plugins/. Plugins
        fi
    done   
fi

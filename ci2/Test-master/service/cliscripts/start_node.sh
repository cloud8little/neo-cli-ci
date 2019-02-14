#!/usr/bin/expect
cd /home/zhangtao/workspace/test/node/neo-cli3/
set timeout 5
spawn dotnet /home/zhangtao/workspace/test/node/neo-cli3/neo-cli.dll --rpc
set timeout 5
expect "*neo>"
interact

#!/usr/bin/expect
cd /home/zhangtao/workspace/test/node/neo-cli4/
set timeout 5
spawn dotnet /home/zhangtao/workspace/test/node/neo-cli4/neo-cli.dll --rpc
set timeout 5
expect "*neo>"
send_user \nSTART_CLI_COMMAND-list_asset-0\n
send "list asset\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-list_asset-0\n
set timeout 5

set timeout 5
expect "*neo>"
send "exit\r"
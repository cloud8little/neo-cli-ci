#!/usr/bin/expect
cd /home/zhangtao/workspace/test/node/neo-cli4/
set timeout 5
spawn dotnet /home/zhangtao/workspace/test/node/neo-cli4/neo-cli.dll --rpc
set timeout 5
expect "*neo>"
send_user \nSTART_CLI_COMMAND-show_gas-0\n
send "show gas\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-show_gas-0\n
set timeout 5

set timeout 5
expect "*neo>"
send "exit\r"

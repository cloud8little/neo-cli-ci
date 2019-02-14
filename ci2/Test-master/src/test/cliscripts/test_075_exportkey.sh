#!/usr/bin/expect
cd /home/zhangtao/workspace/test/node/neo-cli4/
set timeout 5
spawn dotnet /home/zhangtao/workspace/test/node/neo-cli4/neo-cli.dll --rpc
set timeout 5
expect "*neo>"
send_user \nSTART_CLI_COMMAND-list_address-0\n
send "list address\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-list_address-0\n
send_user \nSTART_CLI_COMMAND-export_key-1\n
send "export key AHwmcxyxUva8Do8swvWeS2EkdUzhZ9JP7A 1550040217.txt\r"
expect "*password:"
send "11111111\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-export_key-1\n
set timeout 5

set timeout 5
expect "*neo>"
send "exit\r"

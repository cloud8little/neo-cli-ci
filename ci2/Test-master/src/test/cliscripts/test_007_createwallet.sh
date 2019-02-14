#!/usr/bin/expect
cd /home/zhangtao/workspace/test/node/neo-cli4/
set timeout 5
spawn dotnet /home/zhangtao/workspace/test/node/neo-cli4/neo-cli.dll --rpc
set timeout 5
expect "*neo>"
send_user \nSTART_CLI_COMMAND-create_wallet-0\n
send "create wallet /home/zhangtao/workspace/test/node/neo-cli4/test223.db3\r"
expect "*password:"
send "11111111\r"
expect "*password:"
send "11111111\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-create_wallet-0\n
send_user \nSTART_CLI_COMMAND-open_wallet-1\n
send "open wallet /home/zhangtao/workspace/test/node/neo-cli4/test223.db3\r"
expect "*password:"
send "11111111\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-open_wallet-1\n
send_user \nSTART_CLI_COMMAND-list_address-2\n
send "list address\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-list_address-2\n
send_user \nSTART_CLI_COMMAND-create_wallet-3\n
send "create wallet test223.db3\r"
expect "*password:"
send "11111111\r"
expect "*password:"
send "11111111\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-create_wallet-3\n
set timeout 5

set timeout 5
expect "*neo>"
send "exit\r"

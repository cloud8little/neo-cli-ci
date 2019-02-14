#!/usr/bin/expect
cd /home/zhangtao/workspace/test/node/neo-cli4/
set timeout 5
spawn dotnet /home/zhangtao/workspace/test/node/neo-cli4/neo-cli.dll --rpc
set timeout 5
expect "*neo>"
send_user \nSTART_CLI_COMMAND-open_wallet-0\n
send "open wallet /home/zhangtao/workspace/python/Test-master/src/resource/wallet/wallet_5.json\r"
expect "*password:"
send "11111111\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-open_wallet-0\n
send_user \nSTART_CLI_COMMAND-list_address-1\n
send "list address\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-list_address-1\n
set timeout 5

set timeout 5
expect "*neo>"
send "exit\r"

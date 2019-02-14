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
send_user \nSTART_CLI_COMMAND-show_utxo-1\n
send "show utxo 0x025d82f7b00a9ff1cfe709abe3c4741a105d067178e645bc3ebad9bc79af47d4\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-show_utxo-1\n
set timeout 5

set timeout 5
expect "*neo>"
send "exit\r"

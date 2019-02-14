#!/usr/bin/expect
cd /home/zhangtao/workspace/test/node/neo-cli4/
set timeout 5
spawn dotnet /home/zhangtao/workspace/test/node/neo-cli4/neo-cli.dll --rpc
set timeout 5
expect "*neo>"
send_user \nSTART_CLI_COMMAND-show_utxo-0\n
send "show utxo 0xc56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-show_utxo-0\n
set timeout 5

set timeout 5
expect "*neo>"
send "exit\r"

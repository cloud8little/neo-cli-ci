#!/usr/bin/expect
cd /home/zhangtao/workspace/test/node/neo-cli4/
set timeout 5
spawn dotnet /home/zhangtao/workspace/test/node/neo-cli4/neo-cli.dll --rpc
set timeout 5
expect "*neo>"
send_user \nSTART_CLI_COMMAND-create_wallet-0\n
send "create wallet test.json\r"
expect "*password:"
send "11111111\r"
expect "*password:"
send "11111111\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-create_wallet-0\n
send_user \nSTART_CLI_COMMAND-open_wallet-1\n
send "open wallet test.json\r"
expect "*password:"
send "11111111\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-open_wallet-1\n
send_user \nSTART_CLI_COMMAND-rebuild_index-2\n
send "rebuild index\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-rebuild_index-2\n
send_user \nSTART_CLI_COMMAND-show_state-3\n
send "show state\r"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
expect "block:*"
send "
\r"
send_user \nFINISH_CLI_COMMAND-show_state-3\n
interact

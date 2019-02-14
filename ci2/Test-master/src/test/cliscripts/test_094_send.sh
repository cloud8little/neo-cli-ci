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
send_user \nSTART_CLI_COMMAND-list_asset-1\n
send "list asset\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-list_asset-1\n
send_user \nSTART_CLI_COMMAND-show_state-2\n
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
send "
\r"
send_user \nFINISH_CLI_COMMAND-show_state-2\n
send_user \nSTART_CLI_COMMAND-send-3\n
send "send 0xc56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b AWg3L6W68bFfSS13Tf4rt8CRdG2ktaAjGb 10 0\r"
expect "*password:"
send "11111111\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-send-3\n
interact

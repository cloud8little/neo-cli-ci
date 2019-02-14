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
send "send NEO AHwmcxyxUva8Do8swvWeS2EkdUzhZ9JP7A 10 0\r"
expect "*password:"
send "11111111\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-send-3\n
set timeout 1
expect "*neo>"
send_user \nSTART_CLI_COMMAND-show_pool-4\n
send "show pool\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-show_pool-4\n
set timeout 5

set timeout 5
expect "*neo>"
send "exit\r"

#!/usr/bin/expect
cd /home/zhangtao/workspace/test/node/neo-cli4/
set timeout 5
spawn dotnet /home/zhangtao/workspace/test/node/neo-cli4/neo-cli.dll --rpc
set timeout 5
expect "*neo>"
send_user \nSTART_CLI_COMMAND-open_wallet-0\n
send "open wallet test223.db3\r"
expect "*password:"
send "11111111\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-open_wallet-0\n
send_user \nSTART_CLI_COMMAND-import_key-1\n
send "import key /home/zhangtao/workspace/test/node/neo-cli4/akey.txt\r"
set timeout 30
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-import_key-1\n
send_user \nSTART_CLI_COMMAND-export_key-2\n
send "export key  \r"
expect "*password:"
send "11111111\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-export_key-2\n
set timeout 5

set timeout 5
expect "*neo>"
send "exit\r"

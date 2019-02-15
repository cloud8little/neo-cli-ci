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
send_user \nSTART_CLI_COMMAND-import_multisigaddress-1\n
send "import multisigaddress 021e5f82f1dac5f8662280e1e710b3a10e9c792ebd21fe31557354edd620b5d1b8 032bbbc3dd52542af02af57927862a63faeab58c78d18d072b9d754646c3a65753\r"
set timeout 5
expect "*neo>"
send_user \nFINISH_CLI_COMMAND-import_multisigaddress-1\n
set timeout 5

set timeout 5
expect "*neo>"
send "exit\r"
killall run_alltest
selected=$1
if [ x$1 = xtest_rpc ]; then
    echo '{"test_rpc": true, "test_cli": false}' > select.json
elif [ x$1 = xtest_cli ]; then
    echo '{"test_rpc": false, "test_cli": true}' > select.json
else
    echo '{"test_rpc": true, "test_cli": true}' > select.json
fi
python3 -u run_alltest.py -c select.json

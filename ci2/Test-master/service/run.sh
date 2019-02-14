if killall -9 testservice_23606 ; then
	echo "success killall testservice_23606"
else
	echo "failed killall testservice_23606"
fi

if killall -9 testservice_23616 ; then
	echo "success killall testservice_23616"
else
	echo "failed killall testservice_23616"
fi

if killall -9 testservice_23626 ; then
	echo "success killall testservice_23626"
else
	echo "failed killall testservice_23626"
fi

if killall -9 testservice_23636 ; then
	echo "success killall testservice_23636"
else
	echo "failed killall testservice_23636"
fi


python3 -u neotestservice.py -p 23606 -n "testservice_23606"> `date +%F_%H_%M_%S_23606`.log 2>&1 &
python3 -u neotestservice.py -p 23616 -n "testservice_23616"> `date +%F_%H_%M_%S_23616`.log 2>&1 &
python3 -u neotestservice.py -p 23626 -n "testservice_23626"> `date +%F_%H_%M_%S_23626`.log 2>&1 &
python3 -u neotestservice.py -p 23636 -n "testservice_23636"

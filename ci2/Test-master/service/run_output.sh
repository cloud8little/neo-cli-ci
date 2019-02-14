if killall -9 testservice_23646 ; then
	echo "success killall testservice_23646"
else
	echo "failed killall testservice_23646"
fi

if killall -9 testservice_23656 ; then
	echo "success killall testservice_23656"
else
	echo "failed killall testservice_23656"
fi


python3 -u neotestservice.py -p 23646 -n "testservice_23646"> `date +%F_%H_%M_%S_23626`.log 2>&1 &
python3 -u neotestservice.py -p 23656 -n "testservice_23656"> `date +%F_%H_%M_%S_23636`.log 2>&1 &

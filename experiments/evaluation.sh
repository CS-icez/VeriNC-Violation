#!/bin/bash

echo "Project root: ${FISSLOCK_PATH:?'

  The project root is not set. Please run `source experiments/set-env.sh` 
  before executing this script.
'}"

system_name=$1
benchmark=$2
think_time=$3
crt_num=$4

$MASTER_FISSLOCK_PATH/experiments/run-on-all.sh $system_name $benchmark $think_time $crt_num 2>tmp

echo "Monitoring the experiment progress..."

if [ "$system_name" = "netlock" ]; then
    total=$((6 * (HOST_NUM - 1)))
elif [ "$system_name" = "fisslock" ]; then
    total=$((1 * HOST_NUM))
else
    echo "Error: unknown system_name '$system_name'"
    exit 1
fi


while :
do
    done_cnt=`cat tmp | grep "granted" | wc -l`
    if (( done_cnt == total ))
    then
        break
    fi
    # sleep 1
done

echo "Killing all the processes..."

$MASTER_FISSLOCK_PATH/experiments/kill-all.sh

cp tmp $FISSLOCK_LOG_PATH/violation.log

# while :
# do
#     exit_cnt=`cat tmp | grep "exit" | wc -l`
#     if [[ $exit_cnt == $HOST_NUM ]]
#     then
#         break
#     fi
#     sleep 1
# done

# echo "All processes are killed."

# mkdir -p $RESULT_PATH/$benchmark
# $MASTER_FISSLOCK_PATH/experiments/results/throughput-calculator.sh "throughput"\
#     > $RESULT_PATH/$benchmark/thpt

# $MASTER_FISSLOCK_PATH/experiments/results/collect-results.sh $system_name $benchmark $think_time
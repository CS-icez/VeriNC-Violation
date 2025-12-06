
# The username and password on all machines in the cluster,
# including the switch control plane.
export USERNAME='root'
export PASSWORD='root'

# The paths to the project source code, benchmark traces, and 
# system output. Must be identical on all machines in the cluster.
export FISSLOCK_PATH=/home/abc/fisslock
export FISSLOCK_TRACE_PATH=$FISSLOCK_PATH/traces
export FISSLOCK_LOG_PATH=$FISSLOCK_PATH/log

# There can be a master machine which controls the cluster
# to run the experiments as well as store the experiment results.
export MASTER_FISSLOCK_PATH=/home/abc/fisslock
export RESULT_PATH=$MASTER_FISSLOCK_PATH/results

# The hostname and ID of machines in the cluster.
# Each machine is represented by a "hostname-ID" pair.
export HOSTS="worker1-1 worker2-2"
export SWITCH="tofino"

# The path for BF SDE.
export BF_SDE_PATH="/root/onl-bf-sde"


export HOST_NUM=$(echo $HOSTS | wc -w)
export LOCAL_PROJ_PATH=~/myrepo/verinc-fisslock
export SWITCH_PROJ_PATH=/root/abc/fisslock

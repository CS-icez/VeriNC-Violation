
# The username and password on all machines in the cluster,
# including the switch control plane.
export USERNAME='root'
export PASSWORD='root'

# The paths to the project source code, benchmark traces, and 
# system output. Must be identical on all machines in the cluster.
export FISSLOCK_PATH=/home/bty/netlock
export FISSLOCK_TRACE_PATH=$FISSLOCK_PATH/traces
export FISSLOCK_LOG_PATH=$FISSLOCK_PATH/log

# There can be a master machine which controls the cluster
# to run the experiments as well as store the experiment results.
export MASTER_FISSLOCK_PATH=/home/bty/netlock
export RESULT_PATH=$MASTER_FISSLOCK_PATH/results

# The hostname and ID of machines in the cluster.
# Each machine is represented by a "hostname-ID" pair.
export HOSTS="worker1-1 worker2-2 worker3-3 worker4-4"
export SWITCH="tofino"

# The path for BF SDE.
export BF_SDE_PATH="/root/onl-bf-sde"


export HOST_NUM=$(echo $HOSTS | wc -w)
export LOCAL_PROJ_PATH=~/myrepo/verinc-netlock
export SWITCH_PROJ_PATH=/root/bty/netlock

function compile_p4() {
    docker run -it --rm -v $LOCAL_PROJ_PATH:$SWITCH_PROJ_PATH sde:9.13.3-no-bsp bash -i -c \
        "bf-p4c --verbose 3 -g -a tna -b tofino --program-name fisslock_decider -o $SWITCH_PROJ_PATH/fisslock-p4-build $SWITCH_PROJ_PATH/switch/p4/switch.p4"
    docker run -it --rm -v $LOCAL_PROJ_PATH:$SWITCH_PROJ_PATH sde:9.7.0 bash -i -c \
        "bf-p4c --verbose 3 -g -a tna -b tofino --program-name netlock -o $SWITCH_PROJ_PATH/netlock-p4-build $SWITCH_PROJ_PATH/baseline/NetLock/switch/p4/netlock.p4"
}

function upload_to_master() {
    rsync -vr --delete $LOCAL_PROJ_PATH/ worker1:$MASTER_FISSLOCK_PATH
}

function upload_to_worker() {
    rsync -vr $LOCAL_PROJ_PATH worker$1:~
    ssh worker$1 "source /etc/profile && module load dpdk/dpdk-21.11.7 && cd $FISSLOCK_PATH && make SYSTEM=netlock"
}

function upload_to_switch() {
    rsync -vr $LOCAL_PROJ_PATH/fisslock-p4-build $SWITCH:$SWITCH_PROJ_PATH
    rsync -vr $LOCAL_PROJ_PATH/switch $SWITCH:$SWITCH_PROJ_PATH
    rsync -vr $LOCAL_PROJ_PATH/baseline $SWITCH:$SWITCH_PROJ_PATH
    rsync -vr $LOCAL_PROJ_PATH/experiments $SWITCH:$SWITCH_PROJ_PATH
    rsync -vr $LOCAL_PROJ_PATH/switch/control/ $SWITCH:/root/onl-bf-bsp/bf-platforms/fisslock
    # ssh $SWITCH "cd ~/onl-bf-bsp/bf-platforms && autoreconf \
    #     && export PKG_CONFIG_PATH=$SDE_INSTALL/lib/pkgconfig \
    #     && ./configure --prefix=$SDE_INSTALL --enable-grpc --enable-thrift --host=x86_64-linux-gnu \
    #     && cd fisslock && make && make install"
    
    rsync -vr $LOCAL_PROJ_PATH/netlock-p4-build $SWITCH:$SWITCH_PROJ_PATH
    rsync -vr $LOCAL_PROJ_PATH/build/netlock_len_in_switch/ \
        $SWITCH:$SWITCH_PROJ_PATH/netlock_reproduce/len_in_switch/

    ssh tofino "cp $SWITCH_PROJ_PATH/fisslock-p4-build/fisslock_decider.conf \$SDE_INSTALL/share/p4/targets/tofino"
    ssh tofino "cp $SWITCH_PROJ_PATH/netlock-p4-build/netlock.conf \$SDE_INSTALL/share/p4/targets/tofino"
}

# $SDE/run_switchd.sh -p flowlock -c `pwd`/build/flowlock.conf
# bash switch/run_lockmgr.sh -p netlock
# $SDE/run_p4_tests.sh --no-veth -p netlock -t `pwd`/baseline/NetLock/switch/control --test-params="main_dir='`pwd`/netlock_reproduce/';bm='micro'"
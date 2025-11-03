
all: tatp_trace tpcc_trace ycsb_trace dynamic_trace

tatp_trace:
	mkdir -p $(LOCAL_PROJ_PATH)/build/netlock_len_in_switch
	mkdir -p $(LOCAL_PROJ_PATH)/build/netlock_map
	mkdir -p $(LOCAL_PROJ_PATH)/build/netlock_lock_freq
	python3 netlock_analysis.py $(LOCAL_PROJ_PATH) $(LOCAL_PROJ_PATH)/traces tatp 4

tpcc_trace:
	mkdir -p $(LOCAL_PROJ_PATH)/build/netlock_len_in_switch
	mkdir -p $(LOCAL_PROJ_PATH)/build/netlock_map
	mkdir -p $(LOCAL_PROJ_PATH)/build/netlock_lock_freq
	python3 netlock_analysis.py $(LOCAL_PROJ_PATH) $(LOCAL_PROJ_PATH)/traces tpcc 30

ycsb_trace:
	mkdir -p $(LOCAL_PROJ_PATH)/build/netlock_len_in_switch
	mkdir -p $(LOCAL_PROJ_PATH)/build/netlock_map
	mkdir -p $(LOCAL_PROJ_PATH)/build/netlock_lock_freq
	python3 netlock_analysis.py $(LOCAL_PROJ_PATH) $(LOCAL_PROJ_PATH)/traces ycsb-a-uniform 4
	python3 netlock_analysis.py $(LOCAL_PROJ_PATH) $(LOCAL_PROJ_PATH)/traces ycsb-b-uniform 4
	python3 netlock_analysis.py $(LOCAL_PROJ_PATH) $(LOCAL_PROJ_PATH)/traces ycsb-c-uniform 4
	python3 netlock_analysis.py $(LOCAL_PROJ_PATH) $(LOCAL_PROJ_PATH)/traces ycsb-a-zipf 4
	python3 netlock_analysis.py $(LOCAL_PROJ_PATH) $(LOCAL_PROJ_PATH)/traces ycsb-b-zipf 4
	python3 netlock_analysis.py $(LOCAL_PROJ_PATH) $(LOCAL_PROJ_PATH)/traces ycsb-c-zipf 4

dynamic_trace:
	mkdir -p $(LOCAL_PROJ_PATH)/build/netlock_len_in_switch
	mkdir -p $(LOCAL_PROJ_PATH)/build/netlock_map
	mkdir -p $(LOCAL_PROJ_PATH)/build/netlock_lock_freq
	python3 netlock_analysis.py $(LOCAL_PROJ_PATH) $(LOCAL_PROJ_PATH)/traces dynamic 4

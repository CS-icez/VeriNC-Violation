import sys

cluster_name = "worker"
host_user = "abc"
local_home_dir = "/home/" + host_user + "/"
remote_server_home_dir = "/home/" + host_user + "/"
remote_switch_home_dir = "/root/abc/fisslock/"
remote_switch_sde_dir  = "/root/onl-bf-sde/"

switch_id = "tofino"

id_to_username_dict = {"worker1": "abc", "worker2": "abc", "worker3": "abc", "worker4": "abc", "tofino": "root"}

id_to_passwd_dict = {"worker1": "1234", "worker2": "1234", "worker3": "1234", "worker4": "1234", "tofino": "onl"}

id_to_hostname_dict = {"worker1": "10.0.0.1", "worker2": "10.0.0.2", "worker3": "10.0.0.3", "worker4": "10.0.0.4", "tofino": "10.0.0.100"}

client_id_t1 = []
client_id_t2 = []
server_id = []

def conf_3_clients_1_servers():
     global client_id_t1, client_id_t2, server_id
     # tenant 1's client id. Normally we only need this.
     client_id_t1 = ["worker1"]
     # tenant 2's client id. It's for the two tenant situation.
     client_id_t2 = []
     # Lock server's id
     server_id = ["worker2"]
     print("Clients:", client_id_t1)
     print("Servers:", server_id)

conf_3_clients_1_servers()
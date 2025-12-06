import sys

cluster_name = "worker"
host_user = "abc"
local_home_dir = "/home/" + host_user + "/"
remote_server_home_dir = "/home/" + host_user + "/"
remote_switch_home_dir = "/root/abc/netlock/"
remote_switch_sde_dir  = "/root/onl-bf-sde/"

switch_id = "tofino"

id_to_username_dict = {"worker1": "root", "worker2": "root", "worker3": "root", "worker4": "root", "tofino": "root"}

id_to_passwd_dict = {"worker1": "root", "worker2": "root", "worker3": "root", "worker4": "root", "tofino": "onl"}

id_to_hostname_dict = {"worker1": "172.20.20.11", "worker2": "172.20.20.12", "worker3": "172.20.20.13", "worker4": "172.20.20.14", "tofino": "172.20.20.100"}

client_id_t1 = []
client_id_t2 = []
server_id = []

def conf_3_clients_1_servers():
     global client_id_t1, client_id_t2, server_id
     # tenant 1's client id. Normally we only need this.
     client_id_t1 = ["worker1", "worker2", "worker3"]
     # tenant 2's client id. It's for the two tenant situation.
     client_id_t2 = []
     # Lock server's id
     server_id = ["worker4"]
     print("Clients:", client_id_t1)
     print("Servers:", server_id)

conf_3_clients_1_servers()
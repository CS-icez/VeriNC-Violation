from ipaddress import ip_address

p4 = bfrt.p4ml16.pipe.SwitchIngress
# pre = p4.pre

# print("clean appID_and_Seq")
# bfrt.switch.pipe.appID_and_Seq.clear(batch=True)

# This function can clear all the tables and later on other fixed objects
# once bfrt support is added.
# def clear_all(verbose=True, batching=True):
#     global p4
#     global bfrt

#     def _clear(table, verbose=False, batching=False):
#         if verbose:
#             print("Clearing table {:<40} ... ".
#                   format(table['full_name']), end='', flush=True)
#         try:
#             entries = table['node'].get(regex=True, print_ents=False)
#             try:
#                 if batching:
#                     bfrt.batch_begin()
#                 for entry in entries:
#                     entry.remove()
#             except Exception as e:
#                 print("Problem clearing table {}: {}".format(
#                     table['name'], e.sts))
#             finally:
#                 if batching:
#                     bfrt.batch_end()
#         except Exception as e:
#             if e.sts == 6:
#                 if verbose:
#                     print('(Empty) ', end='')
#         finally:
#             if verbose:
#                 print('Done')

#         # Optionally reset the default action, but not all tables
#         # have that
#         try:
#             table['node'].reset_default()
#         except:
#             pass

#     # The order is important. We do want to clear from the top, i.e.
#     # delete objects that use other objects, e.g. table entries use
#     # The order is important. We do want to clear from the top, i.e.
#     # delete objects that use other objects, e.g. table entries use
#     # selector groups and selector groups use action profile members


#     # Clear Match Tables
#     for table in p4.info(return_info=True, print_info=False):
#         if table['type'] in ['MATCH_DIRECT', 'MATCH_INDIRECT_SELECTOR']:
#             _clear(table, verbose=verbose, batching=batching)

#     # Clear Selectors
#     for table in p4.info(return_info=True, print_info=False):
#         if table['type'] in ['SELECTOR']:
#             _clear(table, verbose=verbose, batching=batching)

#     # Clear Action Profiles
#     for table in p4.info(return_info=True, print_info=False):
#         if table['type'] in ['ACTION_PROFILE']:
#             _clear(table, verbose=verbose, batching=batching)

# clear_all()

# 15227871767@LH

SwitchIngress = p4
modify_packet_bitmap_table = SwitchIngress.appid_seq.modify_packet_bitmap_table

modify_packet_bitmap_table.add_with_modify_packet_bitmap(dataIndex=1)

# modify_packet_bitmap_table.add_with_nop(dataIndex=0)
modify_packet_bitmap_table.add_with_modify_packet_bitmap(dataIndex=0)


MAC_address_of_worker = [
                          "98:03:9b:59:b0:34"  # 11.238.201.138 -> eth4
                        , "98:03:9b:59:af:8c"  # 11.238.201.137 -> eth4
                        , "98:03:9b:03:46:50"
                        , "98:03:9b:59:af:7c"]
len_workers = len(MAC_address_of_worker)
PORT_of_all_worker = [32, 52, 44, 48]
normal_dmac = p4.dmac
for i in range(0, len_workers):
    normal_dmac.add_with_dmac_forward(dst_addr=MAC_address_of_worker[i],port=PORT_of_all_worker[i])

# P4ML Traffic
# 48
# ps = [32]
# worker = [52, 44]

# ps = [52]
# worker = [32, 48]
# loopback = [20]
ps = [4]
worker = [0, 8]
loopback = [20]

# MAC_PS = ["98:03:9b:59:b0:34"]

# multicast_node
# pre.node.add(multicast_node_id=0, multicast_rid=0, multicast_lag_id=[], dev_port=worker)
# pre.mgid.add(mgid=1, multicast_node_id=[0], multicast_node_l1_xid_valid=[False], multicast_node_l1_xid=[0])
bfrt.pre.node.add(MULTICAST_NODE_ID=0, MULTICAST_RID=10, MULTICAST_LAG_ID=[], DEV_PORT=worker)
bfrt.pre.mgid.add(MGID=999, MULTICAST_NODE_ID=[0], MULTICAST_NODE_L1_XID_VALID=[False], MULTICAST_NODE_L1_XID=[0])
multicast_table = p4.appid_seq.atp_ack.multicast_table
multicast_table.add_with_multicast(appIDandSeqNum=0x00010000, appIDandSeqNum_mask=0xFFFF0000, isACK=1, mgid=999)

# set loopPort
# Configure loopback on dev_port 20
bfrt.port.port.mod(PORT_ENABLE=True, DEV_PORT=20, LOOPBACK_MODE="BF_LPBK_MAC_NEAR")


p4ml_dmac = p4.appid_seq.route.dmac
# first send
p4ml_dmac.add_with_dmac_forward(appIDandSeqNum=0x00010000, appIDandSeqNum_mask=0xFFFF0000, dataIndex=1, ingress_port=loopback[0], port=ps[0])
for workerPort in worker:
    p4ml_dmac.add_with_dmac_forward_and_set_dataIndex(appIDandSeqNum=0x00010000, appIDandSeqNum_mask=0xFFFF0000, dataIndex=0, ingress_port=workerPort, port=loopback[0])




bfrt.complete_operations()

# Final programming
print("""
******************* PROGAMMING RESULTS *****************
""")
print ("Table modify_packet_bitmap_table:")
print (modify_packet_bitmap_table.dump())
print ("Table p4ml_dmac_table:")
print (p4ml_dmac.dump())
print ("Table multicast_table:")
print (multicast_table.dump())
print ("Table normal_table:")
print (normal_dmac.dump())
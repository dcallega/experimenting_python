import os
import time
from typing import List, Dict
import numpy as np
from collections import defaultdict
import copy

'''
time,IP_outgoing_pkts_dropped,TCP_num_fast_retransmission,
TCP_num_retransmission_slow_start,TCP_segments_received,
TCP_segments_retransmitted,TCP_segments_sent,Total_IP_pkts_delivered,
Total_IP_pkts_received,Total_bytes_received_at_IP,Total_bytes_sent_at_IP,
UDP_pkts_received,UDP_pkts_sent,beacon signal avg,expected throughput (Mbps),
rx bitrate,signal,signal avg,tx bitrate,tx failed,tx retries
'''
def test_time_read_write():
  outfile = open("tmp.txt", "w")
  cmds = ['netstat -i', 'nstat', 'ifconfig', 'ss --info --tcp']
  start_time = time.time()
  for _ in range(100):
    stat_array = []
    for e in cmds:
      out_cmd = os.popen(e).read()
      stat_array.append(out_cmd)
    print(len(str(stat_array)))
    outfile.write(str(stat_array))
    # [print(e) for e in stat_array]
  print(time.time() - start_time)

def parse_netstat_i(interfaces: List[str] = None) -> Dict[str, Dict[str, str]]:
  """
  Dictionary contains:
  - for each interface
    - Iface : Interface name
      MTU   : Maximum Transmission Unit
      RX-OK : Reciving ok [bytes]
      RX-ERR: 
      RX-DRP:
      RX-OVR:
      TX-OK : 
      TX-ERR:
      TX-DRP:
      TX-OVR:
      Flg   : State of connection
  """
  out = os.popen('netstat -i').read()
  out = out.split("\n")
  lines = [e for e in out]
  header = out[1].split()
  if interfaces is not None:
    ifaces = [e[:5] for e in interfaces]
  ret = {}
  for e in lines[2:]:
    if len(e) > 0:
      tmp = e.split()
      if interfaces is None or tmp[0][:5] in ifaces:
        tmp_ret = {header[i]: tmp[i] for i in range(len(header))}
        ret[tmp[0]] = tmp_ret 
  return ret

def parse_wireless(interfaces: List[str] = None) -> Dict[str, Dict[str, str]]:
  """
  Returns, for each interface, signal strength, level, noise.
  """
  out = os.popen('cat /proc/net/wireless').read()
  out = out.split("\n")
  lines = [e for e in out]
  header = ["Iface", "Status", "Q_link", "Q_lev", "Q_noise"]
  ifaces = None
  if interfaces is not None:
    ifaces = [e[:5] for e in interfaces]
  ret = {}
  for e in lines[2:]:
    if len(e) > 0:
      tmp = e.split()
      interface = tmp[0].split(':')[0][:5]
      tmp[0] = interface
      if interfaces is None or interface in ifaces:
        tmp_ret = {header[i]: tmp[i] for i in range(len(header))}
        ret[interface] = tmp_ret
  return ret

def ss_info_tcp():
  """
  Returns a dictionary with information about the available tcp connections.
  Info about fields: http://man7.org/linux/man-pages/man8/ss.8.html
  wscale: window scale scale factor for send,rcv
  rto: TCP retransmisison timeout [ms]
  rtt: mean/std round trip time [ms]
  ato: ack timeout [ms]
  mss: max segment size [byte]
  pmtu: path MTU value
  mss: maximum segment size [byte]
  cwnd: congestion window [byte]
  bytes_acked
  bytes_received
  segs_out: segments out
  segs_in: segments in
  data_segs_out
  data_segs_in
  lastsnd: time since the last packet was sent [ms]
  lastrcv: time since the last packet was received [ms]
  lastack: time since the last ack was received [ms]
  busy:
  rcv_rtt: 
  rcv_space: 
  rcv_ssthresh: 
  minrtt: 
  """
  st = time.time()
  out = os.popen('ss --info --tcp').read()
  out = out.split("\n")[1:]
  print("External call {}".format(time.time()-st))
  st = time.time()
  ret = {}
  conn, i = None, 0
  while i < len(out) and len(out[i]) > 0:
    if i%2==0 and out[i][:5] == "ESTAB":
      conn = out[i].split()[3]
    elif i%2==1 and conn is not None:
      tmp = out[i].strip().split()
      tmp1 = [e.split(':') for e in tmp]
      d = defaultdict(lambda : None)
      for e in tmp1:
        if len(e) > 1:
          d[e[0]] = e[1]
      ret[conn] = d
      conn = None
    else:
      pass
      # print("Ignored line ", out[i])
    i += 1
  print("Parsing {}".format(time.time()-st))
  return ret

def iface_ip() -> Dict[str, str]:
  st = time.time()
  out = os.popen('ifconfig').read()
  out = out.split("\n")
#  print("External call takes {}".format(time.time() - st))
  st = time.time()
  ret = {}
  conn, i = None, 0
  while i < len(out):
    if len(out[i]) > 0 and out[i][0] == "w":
      conn = out[i].split(':')[0]
      ret[conn] = None
    elif conn is not None:
      if 'inet ' in out[i]:
        tmp_out_split = out[i].split()
        ip = tmp_out_split[tmp_out_split.index('inet') + 1]
        ret[conn] = ip
        conn = None
      pass
    i += 1
#  print("Parsing takes {}".format(time.time() - st))
  return ret
  
def ifconfig_all():# -> Dict[str, Dict[str, str]:
  """
  For each wireless interface (starting with 'w'), returns a dictionary including all available fields in ifconfig
  """
  def RX_packets(line: List[str]) -> Dict[str, str]:
    return {"RX-OK-pck": line[2], "RX-OK-B": line[4]}
  def RX_errors(line: List[str]) -> Dict[str, str]:
    return {"RX-ERR-pck": line[2], "RX-DRP": line[4], "RX-OVR": line[6], "RX-FR": line[8]}
  def TX_packets(line: List[str]) -> Dict[str, str]:
    return {"TX-OK-pck": line[2], "TX-OK-B": line[4]}
  def TX_errors(line: List[str]) -> Dict[str, str]:
    return {"TX-ERR-pck": line[2], "TX-DRP": line[4], "TX-OVR": line[6], "TX-FR": line[8]}
  def inet(line: List[str]) -> Dict[str, str]:
    return {"ip": line[2]}
  def out_of(line: List[str]) -> Dict[str, str]:
    return {}
  switch = {'inet ': inet, "RX pa": RX_packets, "RX er": RX_errors, "TX pa": TX_packets, "TX er": TX_errors}
  switch = defaultdict(lambda : out_of, switch)
  out = os.popen('ifconfig').read()
  out = out.split("\n")
  ret = {}
  conn, i = None, 0
  while i < len(out):
    if len(out[i]) > 1:
      first_char = out[i][0]
      if first_char == "w":
        conn = out[i].split(':')[0]
        ret[conn] = {}
      elif first_char != " ":
        conn = None
      elif out[i][:8] == " "*8 and conn is not None:
        prefix = out[i][8:13]
        ret[conn].update(switch[prefix](out[i].split()))
   #   if 
    i += 1
  return ret

def test_timing(func):
  start = time.time()
  TRIALS = 100
  timings = []
  tmp = {}
  res = []
  for _ in range(TRIALS):
    st = time.time()
    res.append(func())
    timings.append(time.time()-st)
  print(len(res))
  print(np.mean(timings), np.std(timings))
  
def get_interface_stats():
  tcp_fields = ["wscale", "rto", "rtt", "ato", "mss", "pmtu", "mss", "cwnd", "bytes_acked", "bytes_received", "segs_out", "segs_in", "data_segs_out", "data_segs_in", "lastsnd", "lastrcv", "lastack", "busy", "rcv_rtt", "rcv_space", "rcv_ssthresh", "minrtt"]
  tmp = {}
  st = [time.time(), ]
  tmp["wireless"] = parse_wireless()
  st.append(time.time())
  tmp["IP"] = ifconfig_all()
  st.append(time.time())
  tmp["ss"] = ss_info_tcp()
  st.append(time.time())
  print([st[i] - st[i+1] for i in range(len(st)-1)])
  ifaces = list(tmp["wireless"])
  for iface in ifaces:
    final = []
    final.append(iface)
    header = ["Iface nick"]
    curr_header_len = len(header)
    for key in ['wireless', 'nstat_i']:
      curr_header_len = len(header)
      for e in tmp[key]:
        if len(header) <= curr_header_len:
          header += sorted(tmp[key][e])
        if iface in e:
          [final.append(tmp[key][e][k]) for k in sorted(tmp[key][e])]
    rev_iface = {tmp["iface_ip"][e]: e[:5] for e in tmp["iface_ip"] if tmp['iface_ip'][e] is not None}
    final_per_conn = []
    curr_header_len = len(header)
    for conn in tmp['ss']:
      if len(header) <= curr_header_len:
        keys = tcp_fields
        header += tcp_fields
      ip = conn.split(':')[0]
      if ip in rev_iface:
        iface_of_ip = rev_iface[ip]
        for iface in tmp['ss']:
          if ip in iface:
            [final.append(tmp['ss'][conn][e]) for e in tcp_fields]
  return {e[0]:e[1] for e in zip(header, final)}

if __name__=="__main__":
  wireless = parse_wireless()
  ifconfig = ifconfig_all()
  interf_log = copy.deepcopy(wireless)
  for e in wireless:
    interf_log[e].update(ifconfig[e])
  tcp_info = ss_info_tcp()
  final = copy.deepcopy(tcp_info)
  good_ips = set([e.split(":")[0] for e in list(final)])
  print(good_ips)
  interf_ips = [final[i]["ip"] for i in final]
  print(final)
  print(good_ips.intersection(interf_ips))
  exit()
  for i in final:
    ips = final[i]
    print(i, final[i])
  #    conns = [e for e in tcp_info if final[i]["ip"] in e]
    
  #  for conn in conns:
      
  print(ss_info_tcp())



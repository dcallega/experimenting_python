import os
import time
from typing import List, Dict
import numpy as np

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
      if interfaces is None or tmp[0][:5] in ifaces:
        tmp_ret = {header[i]: tmp[i] for i in range(len(header))}
        ret[tmp[0]] = tmp_ret 
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
  out = os.popen('ss --info --tcp').read()
  out = out.split("\n")[1:]
  ret = {}
  conn, i = None, 0
  while i < len(out) and len(out[i]) > 0:
    if i%2==0 and out[i][:5] == "ESTAB":
      conn = out[i].split()[3]
    elif i%2==1 and conn is not None:
      tmp = out[i].strip().split()
      tmp1 = [e.split(':') for e in tmp]
      d = {}
      for e in tmp1:
        if len(e) > 1:
          d[e[0]] = e[1]
      ret[conn] = d
      conn = None
    else:
      pass
      # print("Ignored line ", out[i])
    i += 1
  return ret

def iface_ip() -> Dict[str, str]:
  out = os.popen('ifconfig').read()
  out = out.split("\n")
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
  return ret


if __name__=="__main__":
  tmp = ss_info_tcp()
  # [print(e) for e in tmp[sorted(tmp)[0]]]
  start = time.time()
  TRIALS = 1
  timings = []
  tmp = {}

  for _ in range(TRIALS):
    st = time.time()
    tmp = {}
    tmp["wireless"] = parse_wireless()
    tmp["nstat_i"] = parse_netstat_i()
    tmp["ss"] = ss_info_tcp()
    tmp["iface_ip"] = iface_ip()
    timings.append(time.time()-st)
  iface = 'wlp0s20f3'[:5]
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
  print(tmp['iface_ip'])
  print(rev_iface)
  final_per_conn = []
  curr_header_len = len(header)
  for conn in tmp['ss']:
    if len(header) <= curr_header_len:
      keys = sorted(tmp['ss'][conn])
      header += sorted(tmp['ss'][conn])
    ip = conn.split(':')[0]
    if ip in rev_iface:
      iface_of_ip = rev_iface[ip]
      for iface in tmp['ss']:
        if iface in 
      [final.append(tmp['ss'][e]) for e in keys]
    
  print(header)
  print(final)

  # print(len(header), len(final))

  # print(np.mean(timings), np.std(timings))
  # [print(e, tmp[e]) for e in tmp]

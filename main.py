import json
import csv
import os, sys
import time
import traceback

from get_server_list import get_server_list
from subprocess import Popen, PIPE

start_time = time.time()

id_server = []

header = 'id time location serverName download(mbps) upload(mbps) ping(ms) jitter(ms) result_url time_execute(s)'
header = header.split()

file = open(os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'result.csv')), 'w', newline='')
with file:
    writer = csv.writer(file)
    writer.writerow(header)

count = 0

print('Start getting server list from Ookla...')
server_list = get_server_list()
print('Finished getting server list.')

if (len(server_list) > 0):
  for d in server_list:
    print(f'Testing server: {d["name"]} in country: {d["country"]}')
    s_time = time.time()
    server_to_test = d['id']
        
    result_str = ""
    
    try:
      p = Popen(['/usr/bin/speedtest', '-f', 'json', '-s', server_to_test],
                stdin=PIPE, 
                stdout=PIPE, 
                stderr=PIPE, 
                close_fds=True, 
                bufsize=-1, 
                universal_newlines=True)
      
      out, err = p.communicate()
      tmp_result = json.loads(out)
      
      download = tmp_result["download"]["bandwidth"]
      upload = tmp_result["upload"]["bandwidth"]
      ping = tmp_result["ping"]["latency"]
      jitter = tmp_result["ping"]["jitter"]
      timestamp = tmp_result["timestamp"]
      result_url = tmp_result["result"]["url"]
      location = f'{tmp_result["server"]["location"]} - {tmp_result["server"]["country"]}'
      server_name = f'{tmp_result["server"]["name"]}'
      
      result_str = f'{d["id"]}_{timestamp}_{location}_{server_name}_{round((download*8)/(1024*1024), 2)}_{round((upload*8)/(1024*1024),2)}_{round(ping,2)}_{round(jitter,2)}_{result_url}_{round(time.time() - s_time, 2)} s'
        
    except Exception:
      traceback.print_exc() 
      result_str = 'error'
    
    file = open(os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), 'result.csv')), 'a', newline='')
    count += 1

    print(f'Number of tested server: {count}')
    
    with file:
        writer = csv.writer(file)
        writer.writerow(result_str.split("_"))

print(f'Total execution time: {time.time() - start_time} s')

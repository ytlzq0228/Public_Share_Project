# encoding=utf-8
import paramiko
import time
import re
import sys

deviceip=sys.argv[1]
link_name=sys.argv[2]
client = paramiko.SSHClient()
client.load_system_host_keys()
know_host = paramiko.AutoAddPolicy()
client.set_missing_host_key_policy(know_host)

# connect to client
client.connect(deviceip,22,'admin','password',allow_agent=False,look_for_keys=False)
 
# get shell
ssh_shell = client.invoke_shell()
# ready when line endswith '>' or other character
while True:
	line = ssh_shell.recv(1024)
	if line and str(line).endswith(">'"):
		break;
 
# send command
ssh_shell.sendall( 'dis loadbalance link brief' + '\n')
 
# get result lines
lines = []
while True:
	line = ssh_shell.recv(1024)
	if line and str(line).endswith(">'"):
		break;
	lines.append(line.decode(encoding='utf-8', errors='strict'))
result = ''.join(lines).replace('\r\r','').split('\n')

link_state='No_Link_name'

for i in result:
	if link_name and link_name in i:
		link_state=i.split()[2]

if link_state=='Active':
	print('0:Active')
elif link_state=='Busy':
	print('1:Busy')
elif link_state=='No_Link_name':
	print('1:No_Link_name')
else:
	print('2:%s'%link_state)



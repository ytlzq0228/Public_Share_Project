import paramiko
import time
import re
import sys
import json

data = json.loads(sys.argv[1])
deviceip = data['host']
client = paramiko.SSHClient()
client.load_system_host_keys()
know_host = paramiko.AutoAddPolicy()
client.set_missing_host_key_policy(know_host)

def check_CLI_endswith(ssh_shell,str):
	try:
		while True:
			line = ssh_shell.recv(1024)
			#print(line.decode(encoding='utf-8', errors='strict'))
			if line and line.decode(encoding='utf-8', errors='strict').endswith(str):
				break;
	except Exception as err:
		raise err

def receive_ssh_str(ssh_shell,endswith_str):
	try:
		lines = []
		while True:
			line = ssh_shell.recv(256)
			#print(line.decode(encoding='utf-8', errors='strict'))
			if line and line.decode(encoding='utf-8', errors='strict').endswith(endswith_str):
				break
			if line and line.decode(encoding='utf-8', errors='strict').endswith('---- More ----'):
				ssh_shell.sendall(' ')
				continue
			lines.append(line.decode(encoding='utf-8', errors='strict'))
		result = ''.join(lines).replace('\r\r','').split('\n')
	except Exception as err:
		raise err
	else:
		return result

def sent_commadn_and_receive(ssh_shell,ssh_command):
	try:
		check_CLI_endswith(ssh_shell,'>')
		ssh_shell.sendall(ssh_command+'\n')
		result=receive_ssh_str(ssh_shell,'>')
	except Exception as err:
		raise err
	else:
		return result
	
def get_interest_sensor_value_list(ssh_shell,interest_sensor_name_list):
	try:
		sensor_brief=sent_commadn_and_receive(ssh_shell,'ipmcget -t sensor -d list')
		sensor_brief.remove(sensor_brief[0])
		sensor_brief.remove(sensor_brief[0])
		sensor_brief.remove(sensor_brief[len(sensor_brief)-1])
		interest_sensor_value_list=[]
		for i in sensor_brief:
			sensor_name=i.split('|')[1].strip()
			if sensor_name in interest_sensor_name_list:
				interest_sensor_value_list.append(i)
	
	except Exception as err:
		raise err
	else:
		return interest_sensor_value_list

def printxml(interest_sensor_value_list):
	try:
		print('<?xml version="1.0" encoding="Windows-1252" ?>')
		print('<prtg>')
		print('   <result>')
		print('       <channel>Run Result</channel>')
		print('       <CustomUnit>#</CustomUnit>')
		print('       <mode>Absolute</mode>')
		print('       <float>1</float>')
		print('       <value>0</value>')
		print('   </result>')
		for i in interest_sensor_value_list:
			i=i.split('|')
			if i[2] and i[2].strip() != 'na':
				print('   <result>')
				print('       <channel>%s</channel>'%i[1].strip())
				print('       <CustomUnit>%s</CustomUnit>'%i[3].strip())
				print('       <mode>Absolute</mode>')
				print('       <float>1</float>')
				print('       <value>%s</value>'%i[2].strip())
				if i[6].strip() != 'na' or i[9].strip() != 'na' or i[7].strip() != 'na' or i[8].strip() != 'na':
					print('       <LimitMode>1</LimitMode>')
				if i[6] and i[6].strip() != 'na':
					print('       <LimitMinError>%s</LimitMinError>'%i[6].strip())
				if i[9] and i[9].strip() != 'na':
					print('       <LimitMaxError>%s</LimitMaxError>'%i[9].strip())
				if i[7] and i[7].strip() != 'na':
					print('       <LimitMinWarning>%s</LimitMinWarning>'%i[7].strip())
				if i[8] and i[8].strip() != 'na':
					print('       <LimitMaxWarning>%s</LimitMaxWarning>'%i[8].strip())
				if i[4] and i[4].strip() != 'ok':
					print('       <Warning>1</Warning>')
				print('   </result>')
		print('</prtg>')
	except Exception as err:
		raise err

def print_warning_xml():
	print('<?xml version="1.0" encoding="Windows-1252" ?>')
	print('<prtg>')
	print('   <result>')
	print('       <channel>Run Result</channel>')
	print('       <CustomUnit>#</CustomUnit>')
	print('       <mode>Absolute</mode>')
	print('       <float>1</float>')
	print('       <value>1</value>')
	print('   </result>')
	print('   <text>No XML Dara</text>')
	print('   <Warning>1</Warning>')
	print('</prtg>')
			
def main():
	try:
		interest_sensor_name_list=["Inlet Temp","Outlet Temp","PCH Temp","CPU1 Core Rem","CPU2 Core Rem","CPU1 DTS","CPU2 DTS","Cpu1 Margin","Cpu2 Margin","CPU1 MEM Temp","CPU2 MEM Temp","SYS 3.3V","SYS 5V","SYS 12V_1","SYS 12V_2","CPU1 DDR VPP1","CPU1 DDR VPP2","CPU2 DDR VPP1","CPU2 DDR VPP2","FAN1 Speed","FAN2 Speed","FAN3 Speed","FAN4 Speed","Power","Disks Temp","Power1","PS1 VIN","PS1 IIn","PS1 IOut","PS1 POut","PS1 Temp","PS1 Inlet Temp","Power2","PS2 VIN","PS2 IIn","PS2 IOut","PS2 POut","PS2 Temp","PS2 Inlet Temp","CPU1 VCore","CPU2 VCore","CPU1 DDR VDDQ","CPU1 DDR VDDQ2","CPU2 DDR VDDQ","CPU2 DDR VDDQ2","CPU1 VDDQ Temp","CPU2 VDDQ Temp","CPU1 VRD Temp","CPU2 VRD Temp","CPU1 VSA","CPU2 VSA","CPU1 VCCIO","CPU2 VCCIO","PCH VPVNN","PCH PRIM 1V05"]
		client.connect(deviceip,22,'Administrator','password',allow_agent=False,look_for_keys=False)
		ssh_shell = client.invoke_shell()
		interest_sensor_value_list=get_interest_sensor_value_list(ssh_shell,interest_sensor_name_list)
		printxml(interest_sensor_value_list)
		
	except Exception as err:
		print(err)
		print_warning_xml()

if __name__ == '__main__':
	main()

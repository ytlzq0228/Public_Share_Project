import paramiko
import time
import re
import sys
import json

data = json.loads(sys.argv[1])
deviceip = data['host']
#deviceip='10.0.31.102'
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
		check_CLI_endswith(ssh_shell,'> ')
		ssh_shell.sendall(ssh_command+'\n')
		result=receive_ssh_str(ssh_shell,'> ')
	except Exception as err:
		raise err
	else:
		return result
	
def get_interest_sensor_value_list(ssh_shell,interest_sensor_name_list):
	try:
		sensor_brief=sent_commadn_and_receive(ssh_shell,'sensor --list')
		sensor_brief.remove(sensor_brief[0])
		sensor_brief.remove(sensor_brief[0])
		#sensor_brief.remove(sensor_brief[len(sensor_brief)-1])
		interest_sensor_value_list=[]
		for i in sensor_brief:
			#print(i)
			sensor_name=i.split('|')[0].strip()
			if sensor_name in interest_sensor_name_list:
				interest_sensor_value_list.append(i)
	
	except Exception as err:
		raise err
	else:
		return interest_sensor_value_list

def print_json(interest_sensor_value_list):
	try:
		data={
			"prtg": {
			"result": [
				{
				"Channel": "Run Result",
				"CustomUnit": "#",
				"Mode":"Absolute",
				"Float":1,
				"Value":"0"
				}
			]
			}
			}
		
		for i in interest_sensor_value_list:
			i=i.split('|')
			if i[2] and i[2].strip() != 'na':
				data_channels={
					"Channel": i[0].strip(),
					"CustomUnit": i[3].strip(),
					"Mode":"Absolute",
					"Float":1,
					"Value":i[2].strip()
				}
				if i[6].strip() != 'na' or i[9].strip() != 'na' or i[7].strip() != 'na' or i[8].strip() != 'na':
					data_channels['LimitMode']=1
				if i[6] and i[6].strip() != 'na':
					data_channels['LimitMinError']=i[6].strip()
				if i[9] and i[9].strip() != 'na':
					data_channels['LimitMaxError']=i[9].strip()
				if i[7] and i[7].strip() != 'na':
					data_channels['LimitMinWarning']=i[7].strip()
				if i[8] and i[8].strip() != 'na':
					data_channels['LimitMaxWarning']=i[8].strip()
				if i[4] and i[4].strip() != 'ok':
					data_channels['Warning']='1'
			data['prtg']['result'].append(data_channels)
		print (json.dumps(data, sort_keys=True, indent=2))
	except Exception as err:
		raise err

			
def main():
	try:
		interest_sensor_name_list=["sensorname","Inlet_Temp","Outlet_Temp","CPU0_VR_Temp","CPU1_VR_Temp","M.2_Inlet_Temp","CPU0_Temp","CPU1_Temp","CPU0_DTS","CPU1_DTS","CPU0_DIMM_Temp","CPU1_DIMM_Temp","PCH_Temp","RAID0_Temp","RAID1_Temp","PSU0_Temp","PSU1_Temp","PSU0_POUT","PSU1_POUT","P3V3","P5V","P12V","CPU0_Vcore","CPU1_Vcore","CPU0_DDR_VDDQ1","CPU0_DDR_VDDQ2","CPU1_DDR_VDDQ1","CPU1_DDR_VDDQ2","CPU0_PVCCIO","CPU1_PVCCIO","PCH_P1V05","PCH_VNN","FAN0_F_Speed","FAN0_R_Speed","FAN1_F_Speed","FAN1_R_Speed","FAN2_F_Speed","FAN2_R_Speed","FAN3_F_Speed","FAN3_R_Speed","Total_Power","CPU_Power","MEM_Power","FAN_Power","HDD_Power"]
		client.connect(deviceip,22,'admin','password',allow_agent=False,look_for_keys=False)
		ssh_shell = client.invoke_shell()
		interest_sensor_value_list=get_interest_sensor_value_list(ssh_shell,interest_sensor_name_list)
		print_json(interest_sensor_value_list)
		
	except Exception as err:
		data={
          "prtg": {
           "error": 1,
           "text": str(err)
          }
         }
		print (json.dumps(data, sort_keys=True, indent=2))

if __name__ == '__main__':
	main()

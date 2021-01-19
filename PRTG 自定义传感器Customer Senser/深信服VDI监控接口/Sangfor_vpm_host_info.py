import paramiko
import time
import re
import sys
import json
import requests

requests.packages.urllib3.disable_warnings()
data = json.loads(sys.argv[1])
params=str(data['params']).replace("'",'"')
params = json.loads(params)
deviceip = params['plt_ip']
host_id = params['host_id']
name=data['linuxloginusername']
password=data['linuxloginpassword']
def get_token(deviceip):
	try:
		headers={'Content-Type':'application/json'}
		data={
			"auth": {
				"name": name,
				"password": password
			}
		}
		post_url='https://%s:11111/v1/auth/tokens'%deviceip
		request = requests.post(url=post_url,headers=headers,json=data,verify = False)
		request_text=json.loads(request.text)
		token_text=request_text['data']['token']['auth_token']
	except Exception as err:
		raise err
	else:
		return token_text


def get_server_info(deviceip,token,host_id):
	try:
		headers={'Content-Type':'application/json','Auth-Token':token}
		get_url='https://%s:11111/v1/vtp/host?vtp_id=1&host_id=%s'%(deviceip,host_id)
		request = requests.get(url=get_url,headers=headers,verify = False)

	except Exception as err:
		raise err
	else:
		return request.text

def sort_vmp_cluster_info(value_text):
	try:
		value_dict={}
		value_json=json.loads(value_text)
		value_dict['host_ip']=value_json['data']['host_ip']
		value_dict['CPU_Useage']=[float(value_json['data']['cpu_ratio']),'%',3,-1,70,-1,80]
		value_dict['Memory_Useage']=[float(value_json['data']['mem_ratio']),'%',3,-1,70,-1,80]
		value_dict['VMs_Running_Counts']=[value_json['data']['running_vms'],'#','']
		
		
	except Exception as err:
		raise err
	else:
		return value_dict
			
			
			
def print_json(value_list):
	try:
		host_ip=value_list['host_ip']
		del value_list['host_ip']
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
			],
			'text':'host_id=%s host_ip=%s'%(host_id,host_ip)
			}
			}
		
		for i in value_list:
			data_channels={
				"Channel": i,
				"CustomUnit": value_list[i][1],
				"Mode":"Absolute",
				"Float":1,
				"Value":value_list[i][0]
			}
			if value_list[i][2] !=0:
				data_channels['LimitMode']=1
				if value_list[i][2] == 1:
					data_channels['LimitMinError']=value_list[i][3]
					data_channels['LimitMaxError']=value_list[i][4]
				if value_list[i][2] == 2:
					data_channels['LimitMinWarning']=value_list[i][3]
					data_channels['LimitMaxWarning']=value_list[i][4]
				if value_list[i][2] == 3:
					data_channels['LimitMinWarning']=value_list[i][3]
					data_channels['LimitMaxWarning']=value_list[i][4]
					data_channels['LimitMinError']=value_list[i][5]
					data_channels['LimitMaxError']=value_list[i][6]
			data['prtg']['result'].append(data_channels)
		print (json.dumps(data, sort_keys=True, indent=2))
	except Exception as err:
		raise err

			
			

def main():
	try:
		token=get_token(deviceip)
		value_text=get_server_info(deviceip,token,host_id)
		value_list=sort_vmp_cluster_info(value_text)
		
		print_json(value_list)
		
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

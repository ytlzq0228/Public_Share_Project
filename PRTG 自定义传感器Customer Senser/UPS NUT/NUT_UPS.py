import telnetlib
from time import sleep
import json
import re
import sys
#PORT = '/dev/cu.usbnut-AK08ROD4'

data = json.loads(sys.argv[1])
params=str(data['params']).replace("'",'"')
params = json.loads(params)
nut_ipaddress = params['nut']
#nut_ipaddress='10.0.8.10'

def get_nut_data(nut_ipaddress):
	try:
		tn=telnetlib.Telnet(nut_ipaddress,port=3493, timeout=10)
		tn.write('LIST VAR ups'.encode()+b'\n')
		result=tn.read_until('END LIST VAR ups'.encode()).decode()
		tn.write('LOGOUT'.encode()+b'\n')
	except Exception as err:
		raise err
	else:
		return result


def sort_nut_data(nut_data):
	try:
		nut_data=nut_data.replace('BEGIN LIST VAR ups\n','').replace('\nEND LIST VAR ups','').replace('VAR ups ','')
		data=nut_data.split('\n')
		data_dict={}
		dict={}
		for i in data:
			i=i.split(' "')
			i[1]=i[1].replace('"','')
			dict[i[0]]=i[1]
		data_dict['TEXT']='Device Model:%s'%dict['device.model']
		data_dict['Battery Runtime']=[dict['battery.runtime'],'TimeSeconds']
		data_dict['Battery Power']=[dict['battery.charge'],'Percent']
		data_dict['Output Voltage']=[dict['output.voltage'],'Custom']
		data_dict['UPS Load']=[dict['ups.load'],'Percent']
		if dict['outlet.1.status']=='on':
			data_dict['UPS Output Status']=['0','Custom']
		else:
			data_dict['UPS Output Status']=['1','Custom']
			data_dict['TEXT']=data_dict['TEXT']+' Output Status:%s'%dict['outlet.1.status']
		if dict['outlet.1.switchable']=='no':
			data_dict['UPS Switchable Status']=['0','Custom']
		else:
			data_dict['UPS Switchable Status']=['1','Custom']
			data_dict['TEXT']=data_dict['TEXT']+' Switchable Status:%s'%dict['outlet.1.switchable']
		if dict['ups.status']=='OL CHRG':
			data_dict['UPS Main Status']=['0','Custom']
		else:
			data_dict['UPS Main Status']=['1','Custom']
			data_dict['TEXT']=data_dict['TEXT']+' Main Status:%s'%dict['ups.status']

	except Exception as err:
		raise err
	else:
		return data_dict
		

def print_json(value_list):
	try:

		data={
			"prtg": {
			"text":value_list['TEXT'],
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
		del value_list['TEXT']
		for i in value_list:
			data_channels={
				"Channel": i,
				"Unit": value_list[i][1],
				"Mode":"Absolute",
				"Float":2,
				"Value":value_list[i][0]
			}
			data['prtg']['result'].append(data_channels)
		print (json.dumps(data, sort_keys=True, indent=2))
	except Exception as err:
		raise err

def main():

	try:
		nut_data=get_nut_data(nut_ipaddress)
		data=sort_nut_data(nut_data)
		print_json(data)
	except Exception as err:
		data={
          "prtg": {
           "error": 1,
           "text": str(err)
          }
         }
		print (json.dumps(data, sort_keys=True, indent=2))


if __name__ == "__main__":
	main()

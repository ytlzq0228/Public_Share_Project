import os
import sys
import json

from save_log import save_log
from wechat_webhook_key import wechatwork_robot
from snmp_trap import sent_snmp_trap

def AliCloud_Alarm(data):
	try:
		data=json.loads(data)
		
		product=data['product']
		level=data['level']
		regionId=data['regionId']
		instanceName=data['instanceName']
		name=data['name']
		
		save_log('product:%s ,level:%s ,regionId:%s ,instanceName:%s ,name:%s'%(product,level,regionId,instanceName,name))
		run_result=wechatwork_robot(product,level,regionId,instanceName,name)
		sent_snmp_trap(product,level,regionId,instanceName,name)

	except Exception as err:
		save_log("run_result:%s"%err)
		return err
	else:
		save_log("run_result:%s"%run_result)
		return run_result
		
		
if __name__ == '__main__':
	AliCloud_Alarm(data)

#!/usr/bin/env python
#coding=utf-8
#VBR互联监控，包括VBR流量，延迟，丢包

import sys
import json
import demjson
import time
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcms.request.v20190101.DescribeMetricListRequest import DescribeMetricListRequest



def getapidata(instanceId,set_MetricName,vbrInstanceId):
	client = AcsClient('LTAI4**********JWM94Wqb', 'sWyYH**********fqMHhRc')
	#此处替换为真实的阿里云API秘钥授权信息
	request = DescribeMetricListRequest()
	request.set_accept_format('json')
	request.set_MetricName(set_MetricName)
	request.set_Namespace("acs_cen")
	request.set_Dimensions("{\"cenId\":\""+instanceId+"\",\"vbrInstanceId\":\""+vbrInstanceId+"\"}")
	#request.set_Dimensions("{\"cenId\":\"cen-25ju1ijg6i4g0ts26c\",\"vbrInstanceId\":\"vbr-j6c7tx9xr68bc3sm85zaq\"}")
	request.set_Length("10")
	response = client.do_action_with_exception(request)
	return (str(response, encoding='utf-8'))

def getjsonvalue(data):
	data=json.loads(data)
	data=demjson.decode(data['Datapoints'])
	value=float(data[len(data)-1]['Value'])
	return round(value,2)

def getjsontime(data):
	data=json.loads(data)
	data=demjson.decode(data['Datapoints'])
	return data[len(data)-1]['timestamp']

def getjsondelay(data):
	data=json.loads(data)
	data=demjson.decode(data['Datapoints'])
	value=float(data[len(data)-1]['avg_rtt'])
	return round(value,2)




def printxml(tx_value,rx_value,update_time_delay,delay_value,packetloss_value):
	print('<?xml version="1.0" encoding="Windows-1252" ?>')
	print('<prtg>')
	print('   <result>')
	print('       <channel>Inbound Traffic</channel>')
	print('       <CustomUnit>Kb/s</CustomUnit>')
	print('       <mode>Absolute</mode>')
	print('       <float>1</float>')
	print('       <value>'+str(round(rx_value/1000,2))+'</value>')
	print('   </result>')
	print('   <result>')
	print('       <channel>Outbound Traffic</channel>')
	print('       <CustomUnit>Kb/s</CustomUnit>')
	print('       <mode>Absolute</mode>')
	print('       <float>1</float>')
	print('       <value>'+str(round(tx_value/1000,2))+'</value>')
	print('   </result>')
	print('   <result>')
	print('       <channel>VBR Dealy Time</channel>')
	print('       <CustomUnit>ms</CustomUnit>')
	print('       <mode>Absolute</mode>')
	print('       <float>1</float>')
	print('       <value>'+str(round(delay_value,2))+'</value>')
	print('   </result>')
	print('   <result>')
	print('       <channel>VBR Packet Loss</channel>')
	print('       <Unit>Percent</Unit>')
	print('       <mode>Absolute</mode>')
	print('       <float>1</float>')
	print('       <value>'+str(round(packetloss_value,2))+'</value>')
	print('   </result>')
	print('   <result>')
	print('       <channel>Update Time Dealy</channel>')
	print('       <Unit>TimeSeconds</Unit>')
	print('       <mode>Absolute</mode>')
	print('       <float>1</float>')
	print('       <LimitMaxError>300</LimitMaxError>')
	print('       <LimitMaxWarning>180</LimitMaxWarning>')
	print('       <value>'+str(update_time_delay)+'</value>')
	print('   </result>')

	print('   <text>OK</text>')
	print('</prtg>')


def main(instanceId,vbrInstanceId):
	tx_data=getapidata(instanceId,"VBRInternetOutRate",vbrInstanceId)
	rx_data=getapidata(instanceId,"VBRInternetInRate",vbrInstanceId)
	packetloss_data=getapidata(instanceId,"VBRHealthyCheckLossRate",vbrInstanceId)
	delay_data=getapidata(instanceId,"VBRHealthyCheckLatency",vbrInstanceId)

	tx_value=getjsonvalue(tx_data)
	rx_value=getjsonvalue(rx_data)
	packetloss_value=getjsonvalue(packetloss_data)
	delay_value=getjsonvalue(delay_data)
	update_time=getjsontime(tx_data)/1000
	current_time=int(time.time())
	update_time_delay=current_time - update_time



	printxml(tx_value,rx_value,update_time_delay,delay_value,packetloss_value)

if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2])
    #input(CEN-ID,VBR-ID)

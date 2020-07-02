#!/usr/bin/env python
#coding=utf-8
#VPN网关实例监控，包括VPN网关流量，包速率

import sys
import json
import demjson
import time
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcms.request.v20190101.DescribeMetricListRequest import DescribeMetricListRequest



def getapidata(Dimensions,instanceId,set_MetricName):
	client = AcsClient('LTAI4**********JWM94Wqb', 'sWyYH**********fqMHhRc')
	#此处替换为真实的阿里云API秘钥授权信息
	request = DescribeMetricListRequest()
	request.set_accept_format('json')
	request.set_MetricName(set_MetricName)
	request.set_Namespace("acs_vpn")
	request.set_Dimensions("{\""+Dimensions+"\":\""+instanceId+"\"}")
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



def printxml(tx_value,rx_value,tx_Pkgs_value,rx_Pkgs_value,time_delay):
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
	print('       <channel>Inbound Packets</channel>')
	print('       <CustomUnit>Pkgs/s</CustomUnit>')
	print('       <mode>Absolute</mode>')
	print('       <float>1</float>')
	print('       <value>'+str(rx_Pkgs_value)+'</value>')
	print('   </result>')
	print('   <result>')
	print('       <channel>Outbound Packets</channel>')
	print('       <CustomUnit>Pkgs/s</CustomUnit>')
	print('       <mode>Absolute</mode>')
	print('       <float>1</float>')
	print('       <value>'+str(tx_Pkgs_value)+'</value>')
	print('   </result>')
	print('   <result>')
	print('       <channel>Update Time Dealy</channel>')
	print('       <Unit>TimeSeconds</Unit>')
	print('       <mode>Absolute</mode>')
	print('       <float>1</float>')
	print('       <LimitMaxError>300</LimitMaxError>')
	print('       <LimitMaxWarning>180</LimitMaxWarning>')
	print('       <value>'+str(time_delay)+'</value>')
	print('   </result>')
	print('   <text>OK</text>')
	print('</prtg>')


def main(instanceId):
	tx_data=getapidata("instanceId",instanceId,"net_tx.rate")
	rx_data=getapidata("instanceId",instanceId,"net_rx.rate")
	tx_Pkgs=getapidata("instanceId",instanceId,"net_tx.Pkgs")
	rx_Pkgs=getapidata("instanceId",instanceId,"net_rx.Pkgs")

	update_time=getjsontime(tx_data)/1000
	current_time=int(time.time())
	time_delay=current_time - update_time

	tx_value=getjsonvalue(tx_data)
	rx_value=getjsonvalue(rx_data)
	tx_Pkgs_value=getjsonvalue(tx_Pkgs)
	rx_Pkgs_value=getjsonvalue(rx_Pkgs)


	printxml(tx_value,rx_value,tx_Pkgs_value,rx_Pkgs_value,time_delay)

if __name__ == '__main__':
    main(sys.argv[1])
    #input(VPN-Instant-ID)

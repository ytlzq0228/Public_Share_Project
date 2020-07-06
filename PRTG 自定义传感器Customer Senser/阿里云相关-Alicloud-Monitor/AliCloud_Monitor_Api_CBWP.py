#!/usr/bin/env python
#coding=utf-8
#CBWP互联网共享带宽实例监控

import sys
import json
import demjson
import time
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcms.request.v20190101.DescribeMetricListRequest import DescribeMetricListRequest



def getapidata(instanceId,set_MetricName):
	client = AcsClient('LTAI4**********JWM94Wqb', 'sWyYH**********fqMHhRc')
	#此处替换为真实的阿里云API秘钥授权信息
	request = DescribeMetricListRequest()
	request.set_accept_format('json')
	request.set_MetricName(set_MetricName)
	request.set_Namespace("acs_bandwidth_package")
	request.set_Dimensions("{\"instanceId\":\""+instanceId+"\"}")
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




def printxml(update_time_delay,net_rx_rate_value,net_tx_rate_value,net_rx_Pkgs_value,net_tx_Pkgs_value,net_tx_ratePercent_value):
	print('<?xml version="1.0" encoding="Windows-1252" ?>')
	print('<prtg>')
	print('   <result>')
	print('       <channel>Inbound Traffic</channel>')
	print('       <CustomUnit>Kb/s</CustomUnit>')
	print('       <mode>Absolute</mode>')
	print('       <float>1</float>')
	print('       <value>'+str(round(net_rx_rate_value/1000,2))+'</value>')
	print('   </result>')
	print('   <result>')
	print('       <channel>Outbound Traffic</channel>')
	print('       <CustomUnit>Kb/s</CustomUnit>')
	print('       <mode>Absolute</mode>')
	print('       <float>1</float>')
	print('       <value>'+str(round(net_tx_rate_value/1000,2))+'</value>')
	print('   </result>')
	print('   <result>')
	print('       <channel>Inbound Packets</channel>')
	print('       <CustomUnit>Pkgs/s</CustomUnit>')
	print('       <mode>Absolute</mode>')
	print('       <float>1</float>')
	print('       <value>'+str(net_rx_Pkgs_value)+'</value>')
	print('   </result>')
	print('   <result>')
	print('       <channel>Outbound Packets</channel>')
	print('       <CustomUnit>Pkgs/s</CustomUnit>')
	print('       <mode>Absolute</mode>')
	print('       <float>1</float>')
	print('       <value>'+str(net_tx_Pkgs_value)+'</value>')
	print('   </result>')
	print('   <result>')
	print('       <channel>Bandwidth Useage Rate</channel>')
	print('       <Unit>Percent</Unit>')
	print('       <mode>Absolute</mode>')
	print('       <float>1</float>')
	print('       <LimitMaxError>98</LimitMaxError>')
	print('       <LimitMaxWarning>95</LimitMaxWarning>')
	print('       <value>'+str(round(net_tx_ratePercent_value,2))+'</value>')
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


def main(instanceId):
	net_rx_rate_data=getapidata(instanceId,"net_rx.rate")
	net_tx_rate_data=getapidata(instanceId,"net_tx.rate")
	net_rx_Pkgs_data=getapidata(instanceId,"net_rx.Pkgs")
	net_tx_Pkgs_data=getapidata(instanceId,"net_tx.Pkgs")
	net_tx_ratePercent_data=getapidata(instanceId,"net_tx.ratePercent")

	net_rx_rate_value=getjsonvalue(net_rx_rate_data)
	net_tx_rate_value=getjsonvalue(net_tx_rate_data)
	net_rx_Pkgs_value=getjsonvalue(net_rx_Pkgs_data)
	net_tx_Pkgs_value=getjsonvalue(net_tx_Pkgs_data)
	net_tx_ratePercent_value=getjsonvalue(net_tx_ratePercent_data)

	update_time=getjsontime(net_rx_rate_data)/1000
	current_time=int(time.time())
	update_time_delay=current_time - update_time



	printxml(update_time_delay,net_rx_rate_value,net_tx_rate_value,net_rx_Pkgs_value,net_tx_Pkgs_value,net_tx_ratePercent_value)

if __name__ == '__main__':
    main(sys.argv[1])
    #input(CBWP-ID)

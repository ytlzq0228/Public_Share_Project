#!/usr/bin/env python
#coding=utf-8
#CEN实例监控，包括CEN地域互通流量，地域延时

import sys
import json
import demjson
import time
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkcms.request.v20190101.DescribeMetricListRequest import DescribeMetricListRequest



def getapidata(instanceId,set_MetricName,geographicSpanId,localRegionId,oppositeRegionId):
	client = AcsClient('LTAI4**********JWM94Wqb', 'sWyYH**********fqMHhRc')
	#此处替换为真实的阿里云API秘钥授权信息
	request = DescribeMetricListRequest()
	request.set_accept_format('json')
	request.set_MetricName(set_MetricName)
	request.set_Namespace("acs_cen")
	if set_MetricName == "InternetOutRateByConnectionRegion":
		request.set_Dimensions("{\"cenId\":\""+instanceId+"\",\"geographicSpanId\":\""+geographicSpanId+"\",\"localRegionId\":\""+localRegionId+"\",\"oppositeRegionId\":\""+oppositeRegionId+"\"}")
	if set_MetricName == "LatencyByConnectionRegion":
		request.set_Dimensions("{\"src_region_id\":\""+localRegionId+"\",\"dst_region_id\":\""+oppositeRegionId+"\"}")
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




def printxml(tx_value,rx_value,time_delay,tx_delay_value,rx_delay_value):
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
	print('       <channel>Tx Dealy Time</channel>')
	print('       <CustomUnit>ms</CustomUnit>')
	print('       <mode>Absolute</mode>')
	print('       <float>1</float>')
	print('       <value>'+str(round(tx_delay_value,2))+'</value>')
	print('   </result>')
	print('   <result>')
	print('       <channel>Rx Dealy Time</channel>')
	print('       <CustomUnit>ms</CustomUnit>')
	print('       <mode>Absolute</mode>')
	print('       <float>1</float>')
	print('       <value>'+str(round(rx_delay_value,2))+'</value>')
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


def main(instanceId,geographicSpanId,localRegionId,oppositeRegionId):
	tx_data=getapidata(instanceId,"InternetOutRateByConnectionRegion",geographicSpanId,localRegionId,oppositeRegionId)
	rx_data=getapidata(instanceId,"InternetOutRateByConnectionRegion",geographicSpanId,oppositeRegionId,localRegionId)
	tx_delay=getapidata(instanceId,"LatencyByConnectionRegion",geographicSpanId,localRegionId,oppositeRegionId)
	rx_delay=getapidata(instanceId,"LatencyByConnectionRegion",geographicSpanId,oppositeRegionId,localRegionId)

	tx_value=getjsonvalue(tx_data)
	rx_value=getjsonvalue(rx_data)

	tx_delay_value=getjsondelay(tx_delay)
	rx_delay_value=getjsondelay(rx_delay)

	update_time=getjsontime(tx_data)/1000
	current_time=int(time.time())
	time_delay=current_time - update_time


	printxml(tx_value,rx_value,time_delay,tx_delay_value,rx_delay_value)

if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
    #input(CEN-ID,geographicSpanId,localRegionId,oppositeRegionId)
    #for_example(cen-25ju1i****4g0ts26c,asia-pacific_asia-pacific,cn-hongkong,ap-southeast-5)

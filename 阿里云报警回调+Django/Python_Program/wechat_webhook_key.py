#import http.client
import json
import urllib
import requests
import sys
import datetime
from save_log import save_log
webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=4468de24-0e5e-4616-be8d-53275s4eafc"


def wechatwork_robot(product,level,regionId,instanceName,name):
	now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	paramsList =["云产品:","告警级别:","区域:", "告警节点:" , "告警内容:"]
	valueList = [product,level,regionId,instanceName,name]
	content = ""
	headers = {"Content-Type": "text/plain"}
	title_color="warning"
	for i in range(len(paramsList)):
		content = content +"<font color=\"comment\">"+paramsList[i]+"</font>"+valueList[i]+"\n"
	data = {
		"msgtype": "markdown",
		"markdown": {
		"content": "**<font color=\""+title_color+"\">【阿里云报警小机器人】</font>**\n**通知时间:"+ now_time +"**\n"+ content,
			}
		}
	r = requests.post(url=webhook_url,headers=headers, json=data)
	print(r.text)
	save_log('wechatwork_robot result:%s'%r.text)
	return r.text



if __name__ == '__main__':
	wechatwork_robot('product2','level22','regionId222','instanceName2222','name22222')


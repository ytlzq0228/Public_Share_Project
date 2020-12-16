更好的阅读体验，可以移步原文
[【逗老师带你学IT】阿里云监控报警回调消息转发到企业微信推送+SnmpTrap+PRTG](https://ctsdn.blog.csdn.net/article/details/111276903)

本文解决了一个阿里云监控和告警中比较常见的问题。

如何让阿里云的告警推送到企业微信和第三方监控平台，本文使用报警回调+企业微信webhook+snmptrap的方式推送告警。

本文涉及的知识点：


> 1. 阿里云监控报警回调

> 2. Python Django搭建HTTP API服务器

> 3. 企业微信webhook推送接口

> 4. Python 发送SnmpTrap消息

> 5. PRTG SNMP Trap收集程序


我会按照非代码开发者的基础能力来讲解这些知识点，不要慌，你只要稍微有一点点Python开发能力，跟着这篇文章你都可以学会以上各个知识点。

对于运维开发和其他开发者，直接去github下载。

本文涉及的代码上传带github，地址如下：

[Public_Share_Project/阿里云报警回调+Django/](https://github.com/ytlzq0228/Public_Share_Project/tree/master/%E9%98%BF%E9%87%8C%E4%BA%91%E6%8A%A5%E8%AD%A6%E5%9B%9E%E8%B0%83%2BDjango)

@[TOC](目录)

# 一、阿里云报警回调

官方文档：

[文档中心>云监控>报警服务>报警规则>使用报警回调](https://www.alibabacloud.com/help/zh/doc-detail/60714.htm)

## 1、报警回调支持的监控类型

报警回调功能属于云监控产品下的功能，因此支持大部分云监控产品内的报警输出，主要有`事件报警`和`阈值报警`两大类报警。

举个栗子，ECS CPU使用量超过80%这个情况，可以触发阈值报警。ECS出现重启，可以触发之间报警。关于两大类报警如何定义，本文不做深入研究，各位可以结合自身业务场景自由定义。



但是，报警回调不支持由其他业务系统直接触发的报警。



目前阿里云上的业务，例如智能DNS的`云解析DNS`产品，尚没有接入云监控。此类产品的告警由产品本身发出，只能通过邮件或者钉钉机器人的方式发送。不过好在阿里云绝大部分产品已经接入云监控，并且后续会继续增加。


已经接入云监控的产品如下：

![在这里插入图片描述](https://img-blog.csdnimg.cn/20201216152507282.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

## 2、配置报警回调

1. 登录`云监控控制台`。

2. 在左侧导航栏，选择`报警服务` > `报警规则`。

3. 在`阈值报警`或者`事件报警`页签，单击目标规则对应操作列的修改。

4. 填写报警回调的URL地址。

5. 单击确认。



从目前的使用来看，URL支持`域名、IP+任意端口`的方式。这对于搭建HTTP API服务器而言，门槛降低了很多。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20201216152719852.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

URL的接口地址，是下文我们即将搭建的服务器地址。

## 3、调试报警回调

临时增加一个事件告警规则，选择某一个具体的云产品，以及某几个告警内容，如下图所示：

![在这里插入图片描述](https://img-blog.csdnimg.cn/20201216153033653.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

然后点击调试

![在这里插入图片描述](https://img-blog.csdnimg.cn/20201216153131815.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

临时创建一个模拟事件，然后先不需要修改任何报警内容，直接发送。如果不报错，那么恭喜你，添加报警回调接口这个事情已经完成了。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20201216153245159.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

这时候如果你已经准备好了一台空闲服务器，我们可以上去用wireshark抓个包，可以看到服务器已经收到了对方发出的HTTP POST请求。

当然，抓包的前提是你的服务器上要先随便安装一个HTTP处理程序，随便杀都行，yum install一个nginx，能响应80端口就可以了。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20201216162127526.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)


虽然我们的本机拒绝处理这个请求，但是可以看到内容格式是一个JSON，字段也是符合我们预期的。



# 二、搭建HTTP服务器

既然阿里已经开始向我们自定义的地址推送消息了，那么我们接下来就搭建一台服务器，接收并处理这些消息。

本文涉及的代码上传带github，地址如下：

[Public_Share_Project/阿里云报警回调+Django/](https://github.com/ytlzq0228/Public_Share_Project/tree/master/%E9%98%BF%E9%87%8C%E4%BA%91%E6%8A%A5%E8%AD%A6%E5%9B%9E%E8%B0%83%2BDjango)


## 1、搭建Django

之前我写过一篇文章，各位在搭建Django是有问题，可以参照这篇文章指引。

[【逗老师带你学IT】Django+IIS+Python构建微软AD域控API管理中心](https://ctsdn.blog.csdn.net/article/details/107361857)

操作到下图这一步的时候，就可以回来继续读这篇文章了。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20201216154410807.png)

后文的举例都假设将Django的站点部署在`C:\Django_API\`目录下

## 2、测试接口

把Github里面的代码下载下来，然后保存到`C:\Django_API\`下。



我们写一个临时的脚本，功能是对于所有接收的HTTP请求全部save到本地的一个log文件里。

修改`"C:\Django_API\api\views.py"`如下

```python
import os
import sys
import json


from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from ApiSite.settings import BASE_DIR
from datetime import datetime
from save_log import save_log
#save_log模块扔到C:\Django_API\Python_Program里，项目包里已经写好了

IIS_SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(r"%s\Python_Program"%IIS_SITE_DIR)
logger = logging.getLogger("sourceDns.webdns.views")

@csrf_exempt
def get_data(request):

	try:
		if request.META.get('HTTP_X_FORWARDED_FOR'):
			ip = request.META.get("HTTP_X_FORWARDED_FOR")
		else:
			ip = request.META.get("REMOTE_ADDR")
	except Exception as err:
		ip = 'unknow IP address'
	save_log("\n")
	save_log("Request from IP:%s"%ip)
	Request_method=request.method
	save_log("Request method is: %s"%Request_method)

	try:
		data = str(request.body,'utf-8').encode('utf-8').decode('unicode_escape')
		save_log("run_result:%s"%data)
		run_result=data

	except Exception as err:
		save_log("run_result:%s"%err)
		return JsonResponse({"msg": "%s"%err})
	else:
		save_log("run_result:%s"%run_result)
		return JsonResponse({"msg": run_result})
```

然后模拟一次报警后，打开`"C:\Django_API\log\API_run_log.txt"`可以看到如下日志：

好了，到这一步，我们已经可以接收阿里云的报警回调数据了。

```json
16-12-2020 16:08:45:log:Request from IP:47.74.206.122
16-12-2020 16:08:45:log:Request method is: POST
16-12-2020 16:08:45:log:run_result:{"traceId":"A914CA8D-1F92-4DC6-B6C5-9CD78A545C44","resourceId":"acs:ecs:cn-shanghai:5727269569738808:instance/{instanceId}","ver":"1.0","product":"cfw","instanceName":"instanceName","level":"WARN","userId":"5727269569738808","content":{"logStore":"dry_run","engine":"alertengine-ng033011192146.cms.aliyun-region-vpc-shanghai.et93","ExceedCount":"8","MaxBandwidth":"100M","BandwidthSpecifications":"10M"},"regionId":"cn-hangzhou","eventTime":"20201216T160841.792+0800","name":"InternetBandwidthThresholdExceeded","id":"80A5EE11-2D75-4577-910D-6CDAA9CA493F","timeMetrics":{"ingestion_in_time":1608106121817,"ingestion_out_time":1608106121000,"notify_in_time":1608106123986,"engine_in_time":1608106122552,"event_time":1608106121792,"engine_out_time":0},"status":"Exceeded"}
```


## 3、pip环境

本文需要安装俩包


```powershell
pip install requests pysnmp
```


# 三、报警数据处理

## 1、报警数据格式

通过刚才抓到的报警日志，可以看到报警回调接口推送的是一个JSON格式的数据，我们将数据格式化后，能看到几个关键的字段。

```json
{
    "product": "cfw",
    "resourceId": "acs:ecs:cn-shanghai:5727269569738808:instance/{instanceId}",
    "level": "WARN",
    "instanceName": "instanceName",
    "regionId": "cn-hangzhou",
    "name": "InternetBandwidthThresholdExceeded",
    "content": {
        "BandwidthSpecifications": "10M",
        "MaxBandwidth": "100M",
        "ExceedCount": "8"
    },
    "status": "Exceeded"
}
```

我们从中抽取我们感兴趣的字段。本文示例抽取了以下字段内容

字段|含义

-|-

product|云产品名称<br>`ECS`\|`CFW`\|`CEN`等

level|告警级别<br>`CRITICAL`\|`WARN`等

regionId|产品所在地域

instanceName|示例名称

name|告警内容

对于以上这5个感兴趣的字段，写告警处理模块的关键代码如下：

此文件位于`"C:\Django_API\Python_Program\AliCloud_Alarm.py"`

```python
def AliCloud_Alarm(data):
	try:
		data=json.loads(data)
		
		product=data['product']
		level=data['level']
		regionId=data['regionId']
		instanceName=data['instanceName']
		name=data['name']
		#抽取5个感兴趣的字段和值
		save_log('product:%s ,level:%s ,regionId:%s ,instanceName:%s ,name:%s'%(product,level,regionId,instanceName,name))
		#保存个日志
		run_result=wechatwork_robot(product,level,regionId,instanceName,name)
		#企业微信发送模块
		sent_snmp_trap(product,level,regionId,instanceName,name)
		#snmp发送模块
```

## 2、SNMP_Trap模块发送trap告警

对于第三方网管平台，可以通过很多办法传递告警消息，例如SNMP，API，syslog等。本文举例通过SNMP_Trap的方式将告警消息推送到其他告警平台

```python
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram import udp
from pyasn1.codec.ber import encoder
from pysnmp.proto import api
import sys
from save_log import save_log

def sent_snmp_trap(product,level,regionId,instanceName,name):
#传入前文定义的5个感兴趣字段值
	# Protocol version to use
	verID = api.protoVersion2c
	pMod = api.protoModules[verID]
	
	# Build PDU
	trapPDU = pMod.TrapPDU()
	pMod.apiTrapPDU.setDefaults(trapPDU)
	
	# Traps have quite different semantics among proto versions
	if verID == api.protoVersion2c:
	
		var = []
		oid = (1, 3, 6, 1, 4, 1,12149,1)
		val = pMod.OctetString('product:%s'%product)
		var.append((oid, val))
		oid = (1, 3, 6, 1, 4, 1,12149,2)
		val = pMod.OctetString('level:%s'%level)
		var.append((oid, val))
		oid = (1, 3, 6, 1, 4, 1,12149,3)
		val = pMod.OctetString('regionId:%s'%regionId)
		var.append((oid, val))
		oid = (1, 3, 6, 1, 4, 1,12149,4)
		val = pMod.OctetString('instanceName:%s'%instanceName)
		var.append((oid, val))
		oid = (1, 3, 6, 1, 4, 1,12149,5)
		val = pMod.OctetString('name:%s'%name)
		var.append((oid, val))
		#在这里可以定义多个OID，用于区分不同的字段和内容
		pMod.apiTrapPDU.setVarBinds(trapPDU, var)
		
	save_log(str(var))
	# Build message
	trapMsg = pMod.Message()

	pMod.apiMessage.setDefaults(trapMsg)
	pMod.apiMessage.setCommunity(trapMsg, 'public')
	pMod.apiMessage.setPDU(trapMsg, trapPDU)

	transportDispatcher = AsynsockDispatcher()
	transportDispatcher.registerTransport(udp.domainName, udp.UdpSocketTransport().openClientMode())
	transportDispatcher.sendMessage(encoder.encode(trapMsg), udp.domainName, ('localhost', 162))
	#这里可以修改成真实需要接受trap信息的监控服务器IP地址
	transportDispatcher.runDispatcher()
	transportDispatcher.closeDispatcher()
```

上面的这坨，我们可以加上以下内容，直接运行一下。然后去监控系统看看


```python
if __name__ == '__main__':
	sent_snmp_trap('product2','level22','regionId222','instanceName2222','name22222')
```

已经可以看到SNMP Trap消息了。这里可以使用任何一个SNMP监控软件或者平台接收trap消息，你也可以使用真实的网关平台来测试。我在这里用的是PRTG的snmp trap告警接收程序。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20201216164848759.png)


## 3、企业微信webhook消息推送模块

关于企业微信小机器人的webhook推送，以及如何添加小机器人，可以参考以下文章

[【逗老师带你学IT】PRTG监控系统通过企业微信推送告警消息](https://ctsdn.blog.csdn.net/article/details/104733958)

本文webhook模块关键代码如下，文件位于`"C:\Django_API\Python_Program\wechat_webhook_key.py"`


```powershell
#import http.client
import json
import urllib
import requests
import sys
import datetime
from save_log import save_log
webhook_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=4468de24-0e5e-4616-be8d-5324240f4efc"
#正式机器人
#传参列表
# 1        2        3       4         5       6         7       8           9
#"Key" "%probe" "%group" "%device" "%name" "%status" "%down" "%message" "%sensorid"



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
```

跟上文SNMP一样，我们在最后加一个自调用，模拟一下。

```python
if __name__ == '__main__':
	wechatwork_robot('product2','level22','regionId222','instanceName2222','name22222')
```


可以看到，企业微信群里也收到模拟的告警消息了。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20201216165959529.png)

## 4、整合、部署项目

上面的各个功能验证完毕之后。我们整合部署一下这个项目。

核对两个主要目录的文件是否齐全。

`C:\Django_API\Python_Program`目录下应该存在以下文件。


![在这里插入图片描述](https://img-blog.csdnimg.cn/20201216170426285.png)

`C:\Django_API\api`目录下应该存在以下文件，最关键的是views.py

![在这里插入图片描述](https://img-blog.csdnimg.cn/20201216170604553.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

`C:\Django_API\log`目录下存储着生成的日志，本文自定义的日志文件是API_run_log.txt

![在这里插入图片描述](https://img-blog.csdnimg.cn/20201216170704863.png)

最后，再次通过阿里云模拟一次报警。确认网关平台和企业微信均能收到告警。


![在这里插入图片描述](https://img-blog.csdnimg.cn/20201216172117611.png)

![在这里插入图片描述](https://img-blog.csdnimg.cn/2020121617221583.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)




# 四、PRTG添加SNMP Trap告警监控

## 1、添加传感器

刚才上文的程序，我们是将SNMP Trap推送到127.0.0.1本机环回口地址。其实你可以改成任何一个IP。或者干脆就将Django服务部署到PRTG的探针上去。


在PRTG里，任何一个探针服务器和核心服务器都可以接受trap告警。这里我们找一个合适的探针，将SNMP的告警发送到这个探针的IP地址。添加一个“SNMP陷阱接受程序”的传感器

![在这里插入图片描述](https://img-blog.csdnimg.cn/20201216172500264.png)

## 2、配置传感器端口

默认UDP 162端口用于接收SNMP Trap告警信息，如果修改成其他端口的话，记得在前文的代码中一并修改。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20201216172741943.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

## 3、配置Trap告警过滤器

由于前文，我们会透传阿里云的告警级别至`1.3.6.1.4.1.12149.2`这个OID。

因此我们可以在这里配置一下，让WARN级别的告警，触发PRTG的警告级别告警。CRITICAL级别的告警，触发PRTG的停机级别的告警。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20201216172822498.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

具体关于过滤器的配置预发，可以参考下图

![在这里插入图片描述](https://img-blog.csdnimg.cn/20201216172811997.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

当阿里云产生告警时，PRTG也会根据不同的级别生成相应的告警，如下图

![在这里插入图片描述](https://img-blog.csdnimg.cn/20201216173357148.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

## 4、查看告警历史消息

PRTG会收集SNMP Trap告警并保存，用于后续的统计和筛选。标准化部署监控系统的时候，需要有一个类似的监控系统来保存历史告警信息。

**告警数量统计**

可以看到分时段的，消息通知级别，警告级别，错误级别的告警数量

![在这里插入图片描述](https://img-blog.csdnimg.cn/20201216173747871.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

**历史告警查看和筛选**

![在这里插入图片描述](https://img-blog.csdnimg.cn/20201216173946751.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)






好了，至此阿里云监控告警转发到线下的网管平台，企业微信推送的功能完成了。

# 搞定！


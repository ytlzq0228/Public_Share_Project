更好的阅读体验可以移步原文链接
[【逗老师带你学IT】PRTG、Zabbix通过API监控深信服VDC和VMP云桌面运行状态](https://ctsdn.blog.csdn.net/article/details/112802985)

本文介绍，如果使用API让PRTG和Zabbix等第三方监控系统获取深信服云桌面产品（VDC+VMP）的运行状态，可以获取的监控项包括

>1、集群性能汇总（CPU、内存、存储、网络IO）

>2、集群运行状态（在线物理机数量、下线物理机数量、总虚机数量、运行虚机数量等）

>3、单台物理机性能状态（CPU、内存、存储、运行虚拟机数量）

>4、单台物理机硬件状态（CPU温度、电源功率、内存状态等IPMI监控项）



![在这里插入图片描述](https://img-blog.csdnimg.cn/20210119140605948.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

![在这里插入图片描述](https://img-blog.csdnimg.cn/20210119113423608.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

@[TOC](目录)



# 一、关于深信服VDC和VMP平台

## 1、VDC与VMP的关系

先说一下深信服桌面云产品中VDC和VMP的关系。

VDC（Virtual Desktop Controller）是云桌面的控制平台，负责云端桌面的接入、展现、控制等。

VMP（Virtual Management Platform）是虚拟化管理平台，负责将裸金属服务器构建成虚拟化集群。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20210119120255904.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)



## 2、VDC与VMP的监控指标

所以，结合一个正常云计算系统的框架，我们想象一下这二者面向的对象和能获取的监控项。

VDC面向桌面，能监控到桌面终端连接并发、用户操作行为、文件拷贝速率、虚拟桌面数量等。

VMP面向虚拟化，能监控到集群的CPU、内存、存储IO等指标。


**但是！但是！但是！**

深信服这个傻X玩意不按常理出牌，这也就是为什么我要写这么一篇文章来说明这个事情。

**先上结论：**

深信服的VMP自身就是个垃圾，对VMP的监控需要通过调用VDC的接口来实现。



那么VDC是如何获取VMP的运行情况，如一般的桌面云产品一样，VDC是可以管理VMP的，例如VDC可以直接调用VMP创建虚拟机。在深信服产品内，VDC内需要添加VMP的控制信息，如下图：

![在这里插入图片描述](https://img-blog.csdnimg.cn/20210119142416662.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)


# 二、VDC API接口说明

深信服的云桌面API接口文档已经上传[【CSDN资源】深信服桌面云开放平台（V1.2）](https://download.csdn.net/download/ytlzq0228/14792776)

其中包含了资源管理接口、角色管理接口、虚拟机管理接口、策略组管理接口、用户管理接口、用户组管理接口、VMP管理虚拟机接口、日志接口、运维接口等接口说明。感兴趣的读者可以去下载原文手册。


本文全部代码已经上传Github，地址如下：

[Public_Share_Project/PRTG 自定义传感器Customer Senser/深信服VDI监控接口/](https://github.com/ytlzq0228/Public_Share_Project/tree/master/PRTG%20%E8%87%AA%E5%AE%9A%E4%B9%89%E4%BC%A0%E6%84%9F%E5%99%A8Customer%20Senser/%E6%B7%B1%E4%BF%A1%E6%9C%8DVDI%E7%9B%91%E6%8E%A7%E6%8E%A5%E5%8F%A3)


本文对运维监控需要用到的接口做详细说明

## 1、操作权限认证接口

**POST  https://\<VDC ip\>/v1/auth/tokens**



**简介**

操作权限认证，将auth_token赋值给请求头部中Auth-Token字段才能获取其余接口的访问权限。



**请求参数**

参数|位置|类型|必选|描述
-|-|-|-|-
auth|body|object|y|认证对象
name|body|string|y|超级租户账号
password|body|string|y|超级租户密码


**返回参数**

参数|位置|类型|必选|描述
-|-|-|-|-
token|body|object|y|token对象
tenant_id|body|string|y|租户ID号
auth_token|body|string|y|认证token

**请求示例代码**

```python
def get_token(deviceip,name,password):
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
```

## 2、获取集群在线用户数量接口

**GET  https://\<VDC ip\>/v1/user_groups**



**简介**

获取指定用户组的基本信息，包括用户组ID、用户组名称、描述、父组ID、是否启用、区域名、策略组名、角色名



**请求参数**

参数|位置|类型|必选|描述
-|-|-|-|-
group_id|Path|Int|Y|用户组ID
page_size|Path|Int|Y|每页显示的数量
page|Path|Int|Y|显示的页数

**响应参数**

参数|位置|类型|必选|描述
-|-|-|-|-
id|Body|Int|Y|用户组ID
name|Body|String|Y|用户组名称
note|Body|String|Y|描述
group_id|Body|Int|Y|所属用户组ID
enable|Body|Int|Y|是否启用 1是 0否
area_name|Body|String|Y|区域名
grpolicy|Body|String|Y|策略组名
role_names|Body|String|Y|角色名列表

**响应示例**

```json
{
	"error_code":0,
	"error_message":"Operation succeeded. ",
	"data":
	{
		"total_count":"2",
		"list":
		[
			{
				"id":-1,
				"name":"Default Group",
				"note":"System protected,unable to be deleted",
				"group_id":-100,
				"enable":0,
				"area_name":"\u5f85\u5206\u914d\u533a\u57df",
				"grpolicy":"Default policy set",
				"role_names":"c"
			}
		]
	}
}
```

**请求示例代码**

```python
def get_online_user_info(deviceip,token):
	try:
		headers={'Content-Type':'application/json','Auth-Token':token}
		get_url='https://%s:11111/v1/users?group_id=-100&page_size=10&page=1&user_state=online'%deviceip
		request = requests.get(url=get_url,headers=headers,verify = False)
		value_text=request.text
	except Exception as err:
		raise err
	else:
		return value_text

def sort_online_user_info(value_text):
	try:
		value_dict={}
		value_json=json.loads(value_text)
		value_dict['Online_Users_Number']=[value_json['data']['total_count'],'#','']
	except Exception as err:
		raise err
	else:
		return value_dict
```

本示例可以获取到当前在线用户数量的监控指标，并用于后续在PRTG和Zabbix上进行展示。



## 3、获取VMP集群汇总性能信息

**GET  /v1/vtp?vtp_id=3**



**简介**

获取VMP集群的集群信息，包括集群的主机、cpu、网卡、虚拟机、存储、内存数据。

**请求参数**
参数|位置|类型|必选|描述
-|-|-|-|-
vtp_id|Path|Int|Y|VMP控制器 ID，根据添加的顺序，第一个VMP集群的vtp_id=1


**响应参数**

参数|位置|类型|必选|描述
-|-|-|-|-
cluster|Body|Object|Y|集群信息
cpu|Body|Object|Y|CPU信息
net|Body|Object|Y|网卡信息
host|Body|Object|Y|主机信息
vm|Body|Object|Y|虚拟机信息
stg|Body|Object|Y|存储信息
mem|Body|Object|Y|内存信息
total|Body|Int|Y|主机数量

**响应示例**

```json
{
    "error_code": 0,
    "data": {
        "cluster": {
            "cluster_num": 1,
            "is_cluster": 0
        },
        "is_graphics_cluster": 0,
        "cpu": {
            "ratio": "0.64",
            "used": "22127.616",
            "total": "34574.4"
        },
        "version": "VMP 5.4.2_B \nVMP5.4.0_B-2019-11-26_18:30:00\nupdate=1",
        "net": {
            "receive": 894928,
            "send": 56412,
            "total": 951340
        },
        "host": {
            "offline": 0,
            "cnt": 1,
            "online": 1
        },
        "vm": {
            "on": 27,
            "vgpu_off": 0,
            "off": 125,
            "vgpu_on": 0,
            "cnt": 152,
            "vgpu_cnt": 0
        },
        "stg": {
            "itl": 1,
            "ratio": "0.44",
            "vs": 1,
            "used": 1745930420224,
            "ext": 0,
            "total": 3994554466304,
            "cnt": 2
        },
        "mem": {
            "ratio": "0.67",
            "used": 68899549184,
            "total": 103079215104
        }
    },
    "total": 2
}

```

**请求示例代码**

```python
def get_vmp_cluster_info(deviceip,token):
	try:
		headers={'Content-Type':'application/json','Auth-Token':token}
		get_url='https://%s:11111/v1/vtp?vtp_id=1'%deviceip
		request = requests.get(url=get_url,headers=headers,verify = False)
		value_text=request.text
	except Exception as err:
		raise err
	else:
		return value_text

def sort_vmp_cluster_info(value_text):
	try:
		value_dict={}
		value_json=json.loads(value_text)
		value_dict['System_Version']=value_json['data']['data']['version'].replace('\n','')
		value_dict['CPU_Useage']=[float(value_json['data']['data']['cpu']['ratio'])*100,'%',3,-1,70,-1,80]
		value_dict['Memory_Useage']=[float(value_json['data']['data']['mem']['ratio'])*100,'%',3,-1,70,-1,80]
		value_dict['Storage_Useage']=[float(value_json['data']['data']['stg']['ratio'])*100,'%',3,-1,80,-1,85]
		value_dict['VMs_ON_Counts']=[value_json['data']['data']['vm']['on'],'#','']
		value_dict['VMs_Total_Counts']=[value_json['data']['data']['vm']['cnt'],'#','']
		value_dict['Physical_Servers_Online_Counts']=[value_json['data']['data']['host']['online'],'#','']
		value_dict['Physical_Servers_Offline_Counts']=[value_json['data']['data']['host']['offline'],'#',3,-1,0,-1,1]
		value_dict['Network_Total_Send_Speed']=[round(int(value_json['data']['data']['net']['send'])*8/1024/1024,2),'Mbps','']
		value_dict['Network_Total_Receive_Speed']=[round(int(value_json['data']['data']['net']['receive'])*8/1024/1024,2),'Mbps','']
		
		
	except Exception as err:
		raise err
	else:
		return value_dict
```

本示例可以获取到当前集群的CPU、内存等各种性能监控指标，并用于后续在PRTG和Zabbix上进行展示。



## 4、获取指定主机信息

**GET  /v1/vtp/host?vtp_id=3&host_id=xxx**



**简介**

获取指定VMP集群上的指定主机信息。



**请求参数**

参数|位置|类型|必选|描述
-|-|-|-|-
vtp_id|Path|Int|Y|VMP控制器 ID
host_id|Path|String|Y|主机ID


**响应参数**

参数|位置|类型|必选|描述
-|-|-|-|-
host_ip|Body|String|Y|IP地址
running_vms|Body|Int|Y|运行中的虚拟机数量
cpu_ratio|Body|Int|Y|CPU使用率
mem_ratio|Body|Int|Y|内存使用率


**响应示例**

```json
{
    "error_code": 0,
    "error_message": "",
    "data": {
        "host_ip": "10.70.50.5",
        "running_vms": 20,
        "cpu_ratio": 57,
        "mem_ratio": 44
    }
}
```

**请求示例代码**


```python
def get_server_info(deviceip,token,host_id):
	try:
		headers={'Content-Type':'application/json','Auth-Token':token}
		get_url='https://%s:11111/v1/vtp/host?vtp_id=1&host_id=%s'%(deviceip,host_id)
		request = requests.get(url=get_url,headers=headers,verify = False)
		value_text=request.text
	except Exception as err:
		raise err
	else:
		return value_text

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
```

本示例可以获取到单一物理机的性能指标，并用于后续在PRTG和Zabbix上进行展示。



# 三、代码使用说明

作者已经上传了PRTG监控系统可用的监控脚本，Zabbix版本大佬们简单改一下输出格式就可以了。

## 1、Github地址

本文全部代码已经上传Github，地址如下：

[Public_Share_Project/PRTG 自定义传感器Customer Senser/深信服VDI监控接口/](https://github.com/ytlzq0228/Public_Share_Project/tree/master/PRTG%20%E8%87%AA%E5%AE%9A%E4%B9%89%E4%BC%A0%E6%84%9F%E5%99%A8Customer%20Senser/%E6%B7%B1%E4%BF%A1%E6%9C%8DVDI%E7%9B%91%E6%8E%A7%E6%8E%A5%E5%8F%A3)

![在这里插入图片描述](https://img-blog.csdnimg.cn/20210119144757801.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

## 2、PRTG添加自定义传感器

先将三个py脚本全部拷贝到PRTG探针传感器的如下目录

```
C:\Program Files (x86)\PRTG Network Monitor\Custom Sensors\python
```


然后，在所有操作之前，我们首先添加一个新的设备，设备IP地址为VDC管理平台的IP地址

![在这里插入图片描述](https://img-blog.csdnimg.cn/20210119145249900.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

添加设备的时候，配置Linux登录凭据，用户名和密码为VDC管理平台的用户名和密码。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20210119145330386.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

### 2.1、添加在线用户监控项

添加一个新的传感器，传感器类型为Python自定义脚本，选中下拉列表里刚才拷贝进去的Sangfor_VDI_Oneline_Users.py脚本，同时勾选传递Linux凭据

![在这里插入图片描述](https://img-blog.csdnimg.cn/20210119145534101.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

稍等一会即可获取到监控数据。


![在这里插入图片描述](https://img-blog.csdnimg.cn/20210119145955987.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)




### 2.2、添加集群性能汇总监控项

添加一个新的传感器，传感器类型为Python自定义脚本，选中下拉列表里刚才拷贝进去的Sangfor_vmp_cluster_summary.py脚本，同时勾选传递Linux凭据


![在这里插入图片描述](https://img-blog.csdnimg.cn/20210119145841340.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

稍等一会即可获取到监控数据。


![在这里插入图片描述](https://img-blog.csdnimg.cn/20210119145935397.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)





### 2.3、添加单一物理机性能监控项

添加一个新的传感器，传感器类型为Python自定义脚本，选中下拉列表里刚才拷贝进去的Sangfor_vmp_host_info.py脚本，勾选传递Linux凭据，同时携带一个自定义参数



```
{'host_id':'host-b4055d719a00'}
```

这个host_id在登录VMP管理页面后，可以在查看物理机详情的时候通过iSCSI的IQN发现和获取。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20210119150203932.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

![在这里插入图片描述](https://img-blog.csdnimg.cn/20210119150554588.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

稍等一会即可获取到监控数据。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20210119150642279.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)



### 2.4、添加服务器带外管理监控项

关于带外管理监控项，可以参考博主之前的另一篇文章。

[【逗老师带你学IT】PRTG获取HUAWEI FusionServer iBMC传感器状态](https://ctsdn.blog.csdn.net/article/details/109262952)

深信服一般OEM浪潮的服务器，都是标准的IPMI接口，本文需要用到的浪潮IPMI监控脚本也已经上传到github，按照之前这篇文章的方式添加传感器就可以了。

![在这里插入图片描述](https://img-blog.csdnimg.cn/20210119151054974.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)

![在这里插入图片描述](https://img-blog.csdnimg.cn/20210119151133321.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)



## 3、PRTG运行Python脚本的传参

刚才细心的读者可能发现，我们在创建设备的时候填入了一个linux凭据，并且勾选了将linux凭据传递给python脚本。那么这两个字段的数据在脚本中是如何获取的呢。



我们来看一下python脚本的前几行，这里通过`linuxloginusername`字段获取linux凭据的登录名，通过`linuxloginpassword`字段获取linux登录凭据的密码。

```
data = json.loads(sys.argv[1])
deviceip = data['host']
name=data['linuxloginusername']
password=data['linuxloginpassword']
```

除了这两个字段，PRTG在运行Python脚本的时候还会传递更多的参数。所有参数以json结构体的形式传递给Python脚本。

以下是笔者抓到的PRTG给Python脚本传递的参数示例。各位同学在今后编写自定义脚本的时候。可以灵活的使用这些系统传递参数。

```json
{
"momopersistent":"",
"fastcount":"0",
"lastuptime":"0",
"hostv6":"",
"writeresult":"0",
"blockedsens":"",
"reqmsginterval":"60",
"tlsexplicit_default":"",
"tlsexplicit_imap":"",
"uptimecount":"0",
"canlinux":"0",
"isexesensor":"0",
"mutexname":"",
"reboot":"44127.3734878588",
"usednstime":"0",
"pythonscript":"save_log.py",
"tlsexplicit_port":"",
"inerror":"1",
"sensorid":"4935",
"ipversion":"0",
"tlsexplicit_smtp":"",
"params":"{'host_id':'host-b4055d719a00'}",
"host":"172.16.0.22",
"usewindowsauthentication":"0",
"simulate":"0",
"timeout":"59",
"tlsexplicit_ftp":"",
"lastmsg":"#O2",
"notonpod":"0",
"tlsexplicit_pop3":"",
"linuxloginusername":"admin",
"linuxloginpassword":"123"
#如果此前勾选传递windows凭据，这里会变化为windowsloginusername和password字段
}
```

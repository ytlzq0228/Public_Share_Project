更好的阅读体验，请阅读原文：
[【逗老师带你学IT】PRTG获取HUAWEI FusionServer iBMC传感器状态](https://ctsdn.blog.csdn.net/article/details/109262952)

本文介绍如何使PRTG获取HUAWEI FusionServer iBMC传感器状态。以及衍生出如何通过ipmi通用协议监控所有服务器的带外管理状态。
本文主要涉及的技术点：
>1、服务器ipmi命令行基本操作
>2、HUAWEI Fusion Server iBMC控制台登录
>3、PRTG Python高级自定义脚本传参
>4、PRTG Python高级自定义脚本返回值格式

PRTG监控系统内已经内置了对DELL、HPE、Cisco UCS等主流服务器的带外管理状态监控。甚至连联想的服务器都集成了带外监控功能。
但是，但是
央央我大华为的服务器，竟然没有预制的监控模板，这让我大华为的脸面何在？？

此监控方式支持对iBMC系统获取到的所有传感器值、告警上限值、告警下限值、告警状态等信息同步到PRTG监控。每个服务器只占用1个监控点授权，在1个监控点内实现对最多50个通道的传感器值进行监控。
**PRTG展示效果如下：**
![在这里插入图片描述](https://img-blog.csdnimg.cn/20201024174206359.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_center)
**原始数据如下：**
![在这里插入图片描述](https://img-blog.csdnimg.cn/20201024174903846.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_center)

本文涉及的示例Github地址
[Public_Share_Project/PRTG 自定义传感器Customer Senser/HUAWEI iBMC传感器/](https://github.com/ytlzq0228/Public_Share_Project/tree/master/PRTG%20%E8%87%AA%E5%AE%9A%E4%B9%89%E4%BC%A0%E6%84%9F%E5%99%A8Customer%20Senser/HUAWEI%20iBMC%E4%BC%A0%E6%84%9F%E5%99%A8)

# 一、关于服务器的BMC、IPMI和HUAWEI iBMC
## 1、BMC和IPMI
CSDN的开发狗们，你说你们天天说服务器服务器，可是你们知道服务器与普通PC的区别么？

谈到服务器与PC的区别，最大的莫过于服务器的**带外管理（BMC）**，所谓带外管理，是可以通过独立于主操作系统的带外管理系统（内置于主板上的专用芯片里）管理、监控服务器整机的运行情况。包括开机关机、配置RAID、监控服务器状态、远程安装操作系统、挂载ISO及USB设备等。

而BMC不仅要监控和管理CPU、内存、RAID等设备，同时又要与操作系统通信。底层硬件、BMC、OS这三者之间形成一个两两可以互访的三角形，连接这个三角形的通用接口，就是IPMI。

本文不对BMC和IPMI展开分析，喜欢的话可以参照另一个大大的文章: [BMC介绍](https://blog.csdn.net/weixin_42306122/article/details/95642613)
本文，主要针对性的说说华为的iBMC系统
## 2、HUAWEI iBMC系统
华为服务器iBMC智能管理系统（以下简称iBMC）是华为开发的具有完全自主知识产权的服务器远程管理系统，提供了丰富的管理功能。

- **丰富的管理接口**
提供标准的DCMI1.5/IPMI1.5/IPMI2.0接口、命令行接口、Redfish接口、超文本传输安全协议（HTTPS，Hypertext Transfer Protocol Secure）和简单网络管理协议（SNMP，Simple Network Management Protocol），满足多种方式的系统集成需求。

- **故障监控与诊断**
可提前发现并解决问题，保障设备7*24小时高可靠运行。
系统崩溃时临终截屏与录像功能，使得分析系统崩溃原因不再无处下手。
屏幕快照和屏幕录像，让定时巡检、操作过程记录及审计变得简单轻松。
FDM功能，支持基于部件的精准故障诊断，方便部件故障定位和更换。
支持Syslog报文、Trap报文、电子邮件上报告警，方便上层网管收集服务器故障信息。
支持LCD直接从iBMC获取设备信息。
- **安全管理手段**
通过软件镜像备份，提高系统的安全性，即使当前运行的软件完全崩溃，也可以从备份镜像启动。
多样化的用户安全控制接口，保证用户登录安全性。
支持多种证书的导入替换，保证数据传输的安全性。
- **系统维护接口**
支持虚拟KVM（Keyboard, Video, and Mouse）和虚拟媒体功能，提供方便的远程维护手段。
支持RAID的带外监控和配置，提升了RAID配置效率和管理能力。
通过Smart Provisioning实现了免光盘安装操作系统、配置RAID以及升级等功能，为用户提供更便捷的操作接口。
- **多样化的网络协议**
支持NTP，提升设备时间配置能力，用于同步网络时间。
支持域管理和目录服务，简化服务器管理网络。
- **智能电源管理**
功率封顶技术助您轻松提高部署密度；动态节能技术助您有效降低运营费用。

- **许可证管理**
通过管理许可证，可实现以授权方式使用iBMC高级版的特性。

- **iBMC高级版较标准版提供更多的高级特性，例如**：
通过Redfish实现OS部署、OS克隆和OS还原。
通过Redfish收集智能诊断的原始数据。
# 二、HUAWEI iBMC内ipmc命令行获取传感器信息
## 1、iBMC命令行简介
ipmi接口有一个标准的ipmitools命令行，华为在ipmitools命令行的基础之上，改进使用了ipmc命令行
iBMC管理软件常用命令有以下2类：

- 查询命令ipmcget
查询命令ipmcget的格式如下：
**ipmcget [-t target] -d dataitem [-v value]**

- 设置命令ipmcset
设置命令ipmcset的格式如下：
**ipmcset [-t target] -d dataitem [-v value]**

查询命令ipmcget和设置命令ipmcset的参数说明如下：

- [ ]：表明该内容不是每条命令都包含的部分。
- -t target：查询、设置操作设备上的对象。
- -d dataitem：查询、设置操作设备或操作设备上部件的特定属性。
- -v value：查询、设置操作设备上部件的参数值。

具体信息，参见[FusionServer Pro 机架服务器 iBMC (V561至V649) 用户指南 01](https://support.huawei.com/enterprise/zh/doc/EDOC1100140661/6eb29f7e)

## 2、登录iBMC命令行
您可以通过以下方式登录管理软件命令行：

- SSH
通过SSH方式登录命令行，最多允许5个用户同时登录。
SSH服务支持的加密算法有“AES128-CTR”、“AES192-CTR”和“AES256-CTR”。使用SSH登录iBMC时，请使用正确的加密算法。

- 本地串口
V5服务器提供1个iBMC默认用户“Administrator”，默认密码请参见产品的铭牌。
连续5次输入错误的密码后，系统将对此用户进行锁定。等待5分钟后，方可重新登录，亦可通过管理员在命令行下解锁。
为保证系统的安全性，初次登录时，请及时修改初始密码，并定期更新。
默认情况下，命令行超时时间为15分钟。

**通过SSH登录**
1. 在客户端下载符合SSH协议的通讯工具。
2. 将客户端连接（直连或通过网络连接）到服务器管理网口。
3. 配置客户端地址，使其可与服务器iBMC管理网口互通。
4. 在客户端打开SSH工具并配置相关参数（如IP地址）。
5. 连接到iBMC后，输入用户名和密码。

**通过串口登录**

1. 通过串口登录iBMC命令行，必须保证机箱的系统串口已经切换为iBMC串口。可以通过SSH登录命令行，执行查询和设置串口方向（serialdir）切换串口，或参考服务器产品文档中的跳线切换方式切换串口。
2. 连接串口线。
-- 通过超级终端登录串口命令行，需要设置的参数有：
-- 波特率：115200
-- 数据位：8
-- 奇偶校验：无
-- 停止位：1
-- 数据流控制：无
3. 呼叫成功后输入用户名和密码。

详细手册，参考[【华为iBMC登录命令行】](https://support.huawei.com/enterprise/zh/doc/EDOC1100140661/b704022b)
## 3、通过iBMC命令行获取传感器值列表
查询所有传感器的所有信息（sensor -d list）
**命令功能**
sensor -d list命令用来查询所有传感器信息。

**命令格式**
ipmcget -t sensor -d list

```powershell
iBMC:/->ipmcget -t sensor -d list
sensor id  | sensor name      | value      | unit         | status | lnr        | lc         | lnc        | unc      | uc         | unr        | phys   | nhys
0x1        | Inlet Temp       | 25.000     | degrees C    | ok     | na         | na         | na         | 46.000   | 48.000     | na         | 2.000  | 2.000
0x2        | Outlet Temp      | 35.000     | degrees C    | ok     | na         | na         | na         | 75.000   | na         | na         | 2.000  | 2.000
0x3        | PCH Temp         | 46.000     | degrees C    | ok     | na         | na         | na         | 86.000   | na         | na         | 2.000  | 2.000
0x4        | CPU1 Core Rem    | 47.000     | degrees C    | ok     | na         | na         | na         | na       | na         | na         | 2.000  | 2.000
.............................
```
**字段含义**
![在这里插入图片描述](https://img-blog.csdnimg.cn/20201024180856535.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_center)
这样，我们获取了传感器值的原始数据，接下来需要通过python进行整理，按照PRTG的标准格式进行输出。

# 三、PRTG Python高级自定义脚本应用
## 1、Python脚本文件
[Public_Share_Project/PRTG 自定义传感器Customer Senser/HUAWEI iBMC传感器/](https://github.com/ytlzq0228/Public_Share_Project/tree/master/PRTG%20%E8%87%AA%E5%AE%9A%E4%B9%89%E4%BC%A0%E6%84%9F%E5%99%A8Customer%20Senser/HUAWEI%20iBMC%E4%BC%A0%E6%84%9F%E5%99%A8)
**1、下载此Python脚本文件**
**2、修改登录信息**
![在这里插入图片描述](https://img-blog.csdnimg.cn/20201024181511151.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_left)
3、修改感兴趣传感器列表
`interest_sensor_name_list`内的传感器名称才会进入后续的状态计算和展示，由于PRTG限制一个传感器最多50个通道，此列表长度控制在49以内。
感兴趣传感器名称与通过`ipmcget -t sensor -d list`命令获取的`sensor name`字段需保持一致
![在这里插入图片描述](https://img-blog.csdnimg.cn/20201024181540718.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_left)
![在这里插入图片描述](https://img-blog.csdnimg.cn/20201024181749878.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_center)
## 2、PRTG添加Python脚本
### 1）上传脚本
python脚本改好后，传到PRTG`监控探针`的如下目录。注意如果是分布式探针模式，需要传到探针上，而不是核心服务器。

```powershell
Program Files (x86)\PRTG Network Monitor\Custom Sensors\python
```
### 2） PRTG内置Python安装paramiko

```powershell
"C:\Program Files (x86)\PRTG Network Monitor\python\python.exe" -m pip install paramiko
```
### 3）PRTG添加服务器设备
添加设备，IP地址或DNS域名填入服务器iBMC地址
![在这里插入图片描述](https://img-blog.csdnimg.cn/20201024183044353.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_left)
### 4）PRTG添加Python脚本
在添加好的设备里，添加传感器。传感器类型选择**Python脚本高级（PYTHON SCRIPT ADVANCED SENSOR）**
![在这里插入图片描述](https://img-blog.csdnimg.cn/20201024183223440.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_center)

Python脚本选择刚才上传的.py文件
![在这里插入图片描述](https://img-blog.csdnimg.cn/20201024183345540.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_left)
然后单击保存。
稍等片刻后，即可看到python脚本抓取的传感器信息，已经在PRTG中成功展示
![在这里插入图片描述](https://img-blog.csdnimg.cn/20201024183527221.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_center)
![在这里插入图片描述](https://img-blog.csdnimg.cn/20201024183552477.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_center)
至此，本文开头说到的功能已经完成，对于其他的服务器，复制步骤1-4，即可添加更多的服务器。
接下来，是一些拓展知识，感兴趣的同学继续阅读。
# 四、PRTG Python脚本传参格式

此前，博主已经写过好多好多关于PRTG自定义脚本的xml返回值格式，今天我们不说返回值了，说说调用参数。

关于返回值格式，可以参考之前的文章[【逗老师带你学IT】PRTG监控系统配合树莓派采集企业内部无线网络质量](https://blog.csdn.net/ytlzq0228/article/details/104739756)

前面的例子中，细心的同学会发现。Python脚本中并没有写服务器的IP地址，PRTG在添加Python脚本的时候，也没有写传递设备IP地址的参数。
那么PRTG在调用Python脚本的时候，是如何传递设备IP地址的呢？

我们在PRTG官方的手册里，对于Python脚本的传递参数并没有找到详细的解释。只有如下一句
![在这里插入图片描述](https://img-blog.csdnimg.cn/20201024183920689.png#pic_left)
表示以下字段输入的值。这......貌似毛用都没有啊
![在这里插入图片描述](https://img-blog.csdnimg.cn/2020102418395991.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_center)
关于这个问题，我们在PRTG的KB里找到了一个比较靠谱的解释。
![在这里插入图片描述](https://img-blog.csdnimg.cn/2020102418414678.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_left)
🤔，难道说，PRTG默认就会对所有执行的Python脚本传递一个JSON格式的参数？
于是，我们随便写了一个save_log的脚本，创建使用这个脚本的传感器，运行一下，看看PRTG到底传递是什么样子的参数。

```python
import os
import sys
from datetime import datetime


SITE_DIR = os.path.dirname(os.path.abspath(__file__))

result=sys.argv[1]

now = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

f = open(SITE_DIR+"\run_log.txt",'a')
f.writelines("\n%s:log:%s" %(now,result))
f.flush()
f.close()
```
结果，我们抓到了PRTG默认传递的参数是这样子的。即使在创建传感器的时候不填写任何附加参数，PRTG依然会传递以下丰富的参数给到Python脚本。

```json
{"momopersistent":"",
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
"params":"",
"host":"172.16.0.22",
"usewindowsauthentication":"0",
"simulate":"0",
"timeout":"59",
"tlsexplicit_ftp":"",
"lastmsg":"#O2",
"notonpod":"0",
"tlsexplicit_pop3":""}
```
这里面，我们看到设备IP地址写在了host字段里。同时还传递了其他各种丰富的字段，这让Python脚本的编写会更加灵活。
因此，针对本文的例子，我们可以通过以下简单的代码来提取host字段作为deviceip，用于后续ssh连接使用。

```powershell
data = json.loads(sys.argv[1])
deviceip = data['host']
```
好啦，这次就说到这里。希望能帮到大家

往期回顾：
[【逗老师带你学IT】PRTG自定义脚本ssh登录网络设备获负载均衡链路状态](https://ctsdn.blog.csdn.net/article/details/108779892)
[【逗老师带你学IT】Django+IIS+Python构建微软AD域控API管理中心](https://ctsdn.blog.csdn.net/article/details/107361857)
[【逗老师带你学IT】通过企业微信推送AD域密码即将到期提醒](https://ctsdn.blog.csdn.net/article/details/107073601)
[【逗老师带你学IT】AD域控 Dsquery 查询命令实例汇总](https://ctsdn.blog.csdn.net/article/details/107074237)
[【逗老师带你学IT】Google Admin服务账号+API管理G suit内所有网域用户](https://blog.csdn.net/ytlzq0228/article/details/105682567)
[【逗老师带你学IT】PRTG监控系统通过企业微信推送图文混排告警消息](https://blog.csdn.net/ytlzq0228/article/details/105525667)
[【逗老师带你学IT】PRTG HTTP API获取指定传感器流量图表图片](https://blog.csdn.net/ytlzq0228/article/details/105524615)
[【逗老师带你学IT】PRTG监控系统合并多个传感器通道数据](https://blog.csdn.net/ytlzq0228/article/details/104736297)
[【逗老师带你学IT】PRTG监控系统通过企业微信推送告警消息](https://blog.csdn.net/ytlzq0228/article/details/104733958)
[【逗老师带你学IT】PRTG监控系统配合树莓派采集企业内部无线网络质量](https://blog.csdn.net/ytlzq0228/article/details/104739756)
[【逗老师带你学IT】vMware ESXi 6.7合并第三方硬件驱动](https://blog.csdn.net/ytlzq0228/article/details/105194719)
[【逗老师带你学IT】Kiwi Syslog Server安装和配置教程](https://blog.csdn.net/ytlzq0228/article/details/104827014)
[【逗老师带你学IT】Kiwi Syslog Web Access与Active Directory集成认证](https://blog.csdn.net/ytlzq0228/article/details/104826989)
[【逗老师带你学IT】vMware ESXi 6.7合并第三方硬件驱动](https://blog.csdn.net/ytlzq0228/article/details/105194719)
[【逗老师带你学IT】Windows Server Network Policy Service（NPS）记账与审计](https://blog.csdn.net/ytlzq0228/article/details/104760054)
[【逗老师带你学IT】Windows Server NPS服务构建基于AD域控的radius认证](https://blog.csdn.net/ytlzq0228/article/details/104758242)
[【逗老师带你学IT】AD域控和freeradius集成认证环境，PAP，MSCHAPV2](https://blog.csdn.net/ytlzq0228/article/details/104757395)
[【逗老师带你学IT】深信服SSL远程接入与深信服行为审计同步登陆用户信息](https://blog.csdn.net/ytlzq0228/article/details/104723838)

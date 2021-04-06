# 原文地址
[【逗老师带你学IT】PRTG自定义脚本ssh登录网络设备获负载均衡链路状态](https://blog.csdn.net/ytlzq0228/article/details/108779892)
本文介绍如何使PRTG监控系统的自定义脚本功能，ssh登录网络设备，抓取很多snmp无法获取的监控指标。
本文主要涉及的技术点：
>1、python paramiko模块应用
>2、paramiko模块回显抓取
>3、PRTG value vlookup值查找功能
>4、H3C防火墙Loadbalance link状态查看


一般情况下，我们可以通过SNMP获取网络设备绝大部分的通用监控信息，但是各设备厂商均存在非标的功能，甚至存在通过厂商提供的MIB库也无法获取的监控信息。

例如，H3C的网络设备的负载均衡功能，其中链路状态信息关联NQA模板，来实现链路状态保活。

但是查阅文档后，LB的link状态，以及NQA监测点，统统没有对应的SNMP OID。
本文举例说明，将设备商通过`dis loadbalance link brief`命令获取的链路状态信息，通过Python处理后，展现在PRTG的监控指标中。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20210406135437996.png)
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200924175921599.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_left)
本文涉及的示例Github地址
[Public_Share_Project/PRTG 自定义传感器Customer Senser/H3C_FW_LB_链路状态监测/](https://github.com/ytlzq0228/Public_Share_Project/tree/master/PRTG%20%E8%87%AA%E5%AE%9A%E4%B9%89%E4%BC%A0%E6%84%9F%E5%99%A8Customer%20Senser/H3C_FW_LB_%E9%93%BE%E8%B7%AF%E7%8A%B6%E6%80%81%E7%9B%91%E6%B5%8B)
实现过程如下：
@[TOC](目录)

# 一、python paramiko模块ssh登录网络设备
下面代码片段举例介绍，如何通过paramiko模块ssh登录网络设备。
如果想通过Python登录设备执行一些命令（比如 reboot），以下代码片段就够了。

```python
import paramiko
import time
import re
import sys
client = paramiko.SSHClient()
client.load_system_host_keys()
know_host = paramiko.AutoAddPolicy()
client.set_missing_host_key_policy(know_host)
client.connect(deviceip,22,'admin','password',allow_agent=False,look_for_keys=False)
 
# get shell
ssh_shell = client.invoke_shell()
# ready when line endswith '>' or other character
while True:
	line = ssh_shell.recv(1024)
	if line and str(line).endswith(">'"):#登录后等待设备出现>标识，稳定后输入命令
		break;
 
# 发送命令
ssh_shell.sendall( 'dis loadbalance link brief' + '\n')
 
```
# 二、python paramiko模块回显抓取
本文的例子中，我们显然不能仅仅执行一个命令就完事，我们还需要获取回显结果。
paramiko的回显抓取深究起来可以专门出一篇文章，涉及ssh管道、字符编码，tcp传输期间的占位符等等。我们这里不深究，直接上一个例子大家拿去用就好了。

```python
# send command
ssh_shell.sendall( 'dis loadbalance link brief' + '\n')
 
# get result lines
lines = []
while True:
	line = ssh_shell.recv(1024)
	if line and str(line).endswith(">'"):
		break;
	lines.append(line.decode(encoding='utf-8', errors='strict'))
result = ''.join(lines).replace('\r\r','').split('\n')
```
如此，我们得到了一个list类型的返回值，其中存放着ssh命令回显的每一行，每行占一个元素。
**中间插个print，检验一下结果：**

```powershell
for i in result:
	print(i)
```
很好，跟平日里ssh登录到设备商看到的信息一样。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200924182815603.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_left)
# 三、查找指定链路名称的链路状态
我们现在，需要按照给定的链路名称，或者其他关键字，查找到这条链路的状态。
看看这个回显结果，思路很简单
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200924183344765.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_left)

```python
link_state='No_Link_name'

for i in result:
	if link_name and link_name in i:
	#判定条件，关键词不为空且关键字存在于行内。
		link_state=i.split()[2]
		# split根据空格切成3段，取第3段的值
		#不用split，用字符串截取后面6个英文字符也可以，随便搞。

if link_state=='Active':
	print('0:Active')
elif link_state=='No_Link_name':
	print('1:No_Link_name')
else:
	print('2:%s'%link_state)
```
# 四、PRTG添加自定义传感器
写好了上面的脚本之后，我们将.py文件扔到如下路径


```powershell
如果直接用PRTG的Python解释器
C:\Program Files (x86)\PRTG Network Monitor\Custom Sensors\python
```
```powershell
如果想用操作系统安装的Python，放到如下路径
C:\Program Files (x86)\PRTG Network Monitor\Custom Sensors\exe
并编写一个bat文件如下
@echo off
python H3C_FW_LB_Link_Check.py %1 %2
```

然后在PRTG中添加传感器，传感器类型选择`EXE自定义脚本`
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200924184745470.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_left)
选择我们编写好的脚本，并传入参数
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200924185129632.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_left)

本文示例的Python脚本需要传递两个参数，分别是
- 设备IP
- 链路名称关键字

使用的时候根据具体情况填写

关于互斥名称，互斥名称尽量跟参数保持一致。PRTG将逐一执行 (并非同时执行)拥有相同互斥名称的所有 EXE/脚本传感器。如果您拥有大量传感器并想要避免由同时运行进程所引起的资源高度使用，这十分有用。

配置完毕后，现在已经可以获取到接口信息了，如下图所示。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200924185437449.png#pic_left)
但是，目前我们还没有定义告警，也就是说无论程序返回啥值，PRTG都认为是正常的。
如何定义告警？借着往下看。
# 五、PRTG返回值状态定义
根据之前的Python脚本，程序会给出三种可能返回值。
>0:Active
>1:No_Link_name
>2:防火墙给出的具体错误信息，例如Probe_Fail等

对于以上三种情况，我们通过传递一个整数值给到PRTG系统，然后定义这个整形数字对应的具体意义，例如`0=正常，1=警告，3=错误`。这个定义，我们通过PRTG的值查找功能来实现。
点击通道右侧的齿轮图标，进入通道编辑，我们可以看到有关“值查找”的相关选项。
![在通道编辑](https://img-blog.csdnimg.cn/20200924185953593.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_left)
PRTG 对某些传感器和具有自定义通道的某些传感器使用查找。通常，查找将设备返回的状态值（通常是整数）映射到单词中信息量更大的表达式。此外，查找可以根据设备返回的状态值定义显示的传感器状态，就像通道限制也可以定义传感器状态一样。例如，对于返回状态值“ 1”，PRTG可以通过文本消息“ Toner Low”显示黄色警告状态的传感器，而不仅仅是显示状态值“ 1”。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200924185920999.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_left)
我们可以自定义一个文件，来定义返回值所对应的状态，并将这个文件存放到PRTG的lookup文件夹下，被PRTG引用即可。
文件路径:
```powershell

C:\Program Files (x86)\PRTG Network Monitor\lookups\custom\xxx.ovl
```
文件内容：

```xml
<?xml version="1.0" encoding="UTF-8"?>
  <ValueLookup id="00-customer.prtg.standardlookups.link.states" desiredValue="300" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="PaeValueLookup.xsd">
    <Lookups>
      <SingleInt state="Ok" value="0">
        Ok
      </SingleInt>
      <SingleInt state="Warning" value="1">
        Warning
      </SingleInt>
      <SingleInt state="Error" value="2">
        Error
      </SingleInt>
    </Lookups>
  </ValueLookup>
```
文件存好之后，进入PRTG->设置->管理工具->加载查询和文件列表，点击运行，重新加载配置文件。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200924190808590.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_left)
然后在通道编辑下，勾选“根据值查找启用报警”，并选择我们刚才保存的配置文件即可
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200924190854808.png#pic_left)


上面这个例子很简单的定义了当返回值等于0、1、2三种情况是系统的告警状态。关于PRTG的状态值查找功能，可以参阅手册原文。
[PRTG Manual: Define Lookups](https://www.paessler.com/manuals/prtg/define_lookups)

这样，当链路状态非Active时，PRTG会触发告警，例如：
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200924191231860.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70#pic_left)

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200924191208270.png#pic_left)

# 搞定！

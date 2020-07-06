原文链接
[PRTG监控系统配合树莓派采集企业内部无线网络质量](https://blog.csdn.net/ytlzq0228/article/details/104739756)
# 本文介绍了一种，如何通过树莓派采集企业内部无线网络质量，将树莓派变成无线探针，并在PRTG网络监控平台上进行显示的方法。
可以监控我们感兴趣的无线网络的各项指标，包括
>**无线丢包
ping测试最大、最小，平均，抖动
设备温度
无线信道
无线协商速率
无线连接质量
射频信号功率**

通过这个监控机制，企业网络管理者可以直观的获取无线探针所在区域的无线质量。及时发现诸如无线信道跳频，延迟增大，丢包，信号衰减等事件。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200308203020360.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200308203112166.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)
# 实现原理
树莓派运行了基于Debian的Linux系统。通过iwconfig，ping，ifconfig，iproute等linux常见命令获取设备当前的网络连接情况，并通过Python格式化数据后，转换成PRTG系统可以识别的XML格式的数据文件。
# 部署方法
## 一、树莓派无线网络连接
目前的树莓派常见的有Raspberry Pi 4，3+，3三个主要流行的版本。具体支持的无线情况如下：
型号|支持的无线频段
-|-
Raspberry Pi 4B | 5Ghz+2.4GHz
Raspberry Pi 3B+|5Ghz+2.4GHz
Raspberry Pi 3B|Only 2.4GHz
由于4B的各版本目前刚刚发布，大批量部署性价比不合适。3B版本不支持5G。
这样看来的话，使用3B+版本+POE模块其实刚刚好。
树莓派无线网络连接比较简单，编辑

```powershell
/etc/wpa_supplicant/wpa_supplicant.conf 
```
该文件记录了树莓派WIFI的相关配置

```powershell
network={
    ssid="无线网络名字"
    psk="无线密码"
    key_mgmt=WPA-PSK
}
```
配置完成之后重启网络服务

```powershell
service networking restart
```
由于我们的目标是这个树莓派不管插在任何一个网口上，甚至是不连接有线直接通过无线连接上报采集的数据，因此需要同时启用eth和wlan网口，并配置缺省路由的优先级，eth缺省路由优先级较高。编辑文件

```powershell
cat /etc/network/interfaces
```

```powershell
auto eth0
iface eth0 inet dhcp
metric 10
#eth0的metric为10 ，如果存在eth0为下一跳的缺省路由，优选此条缺省路由。

allow-hotplug wlan0
auto wlan0
iface wlan0 inet dhcp  
metric 100
#wlan的metric跳数配置比eth0高
pre-up wpa_supplicant -B w -D wext -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf 
post-down killall -q wpa_supplicant
#关联WPA_Supplicat文件
```
配置完成后，重启网络服务，重启无线网卡接口。嫌麻烦的的可以直接重启设备。

```powershell
service networking restart
ifdown wlan0
ifup eth0
```
正常联网的情况下，我们检查一下设备的路由表和网卡地址，确认是否正常。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200308205310490.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200308205412551.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)
## 二、编写shell脚本

```powershell
#!/bin/bash
PATH=/etc:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin

cd /home/pi

if [ -f checkresult.txt ]; then
   #echo "remove old checkresult.txt file ... "
    rm -f checkresult.txt
fi

if [ -f $HOSTNAME-WIFI_Check_result.txt ]; then
   #echo "$HOSTNAME-WIFI_Check_result.txt file ... "
    rm -f $HOSTNAME-WIFI_Check_result.txt
fi

if [ -f IP-WIFI-Check-$HOSTNAME.txt ]; then
   #echo IP-WIFI-Check-$HOSTNAME.txt file ... "
    rm -f IP-WIFI-Check-$HOSTNAME.txt
fi
#删除可能存在的历史文件
wlangwip=$(route | grep wlan0 | grep default)
wlangwip=${wlangwip##*default} 
wlangwip=${wlangwip%%0.0.0.0*}
#这一顿骚操作，是为了获取目前无线网络的网关IP地址
#我们尽可能的保证这个脚本的普适性，因此需要自动获取当前无线网络的网关IP

# route | grep wlan0 | grep default like this:
#default         10.0.192.1      0.0.0.0         UG    100    0        0 wlan0
#                ↑就是为了获取这个字段
#-------------------------------------------------------------------
ping -c 200 -i 0.1 $wlangwip >> checkresult.txt
#100ms间隔快速ping网关IP，结果写入checkresult.txt文件
iwconfig wlan0 >> checkresult.txt
#iwconfig命令是无线网卡的状态，将状态写入checkresult.txt文件
#-------------------------------------------------------------------
echo '<device_temp>' >> checkresult.txt
cat /sys/class/thermal/thermal_zone0/temp >> checkresult.txt
echo '</device_temp>' >> checkresult.txt
#将树莓派当前温度写入checkresult.txt文件
#-------------------------------------------------------------------
echo '<device_eth0ip>' >> checkresult.txt
ifconfig eth0 | grep "inet " | awk '{print $2}' >> checkresult.txt
echo '</device_eth0ip>' >> checkresult.txt
#-------------------------------------------------------------------
echo '<device_wlanip>' >> checkresult.txt
ifconfig wlan0 | grep "inet " | awk '{print $2}' >> checkresult.txt
echo '</device_wlanip>' >> checkresult.txt
#将有线网卡，无线网卡当前获取的IP地址写入checkresult.txt文件

NIC=$(route -n | grep UG | awk '{print $8}'| awk 'NR==1')
ifconfig $NIC | grep "inet " | awk '{print $2}' >> IP-WIFI-Check-$HOSTNAME.txt
#这两句详细解释一下
#第一句，获取当年设备缺省路由表第一行的记录，并提取其中的网卡设备名
#第二句，获取此网卡目前的IP地址
#这个地址是目前树莓派与服务器通信的主地址。仅连接无线的情况为wlan0 IP地址，同时连接有线无线的时候为eth0 IP地址
#这个地址，之后集中下发脚本的时候用得到
#-------------------------------------------------------------------
python checknetwork.py checkresult.txt $HOSTNAME-WIFI_Check_result.txt $HOSTNAME
#通过Python，格式化checkresult.txt的内容，并输出一个已HOSTNAME命名的XML文件
#-------------------------------------------------------------------
tftp 10.0.20.178 << !
put $HOSTNAME-WIFI_Check_result.txt
put IP-WIFI-Check-$HOSTNAME.txt
quit
!
tftp 10.0.20.20 << !
put IP-WIFI-Check-$HOSTNAME.txt
quit
!
#通过TFTP上传前面生成的文件,直接传递到PRTG服务器上是最方便的，也可选择使用scp,FTP或者其他的方式，自选。
#-------------------------------------------------------------------
rm -f checkresult.txt
rm -f $HOSTNAME-WIFI_Check_result.txt
rm -f IP-WIFI-Check-$HOSTNAME.txt
删除刚才生成的一堆临时文件
#-------------------------------------------------------------------
```
每行代码的功能我都注释好了，够贴心了吧，0基础保证你能看得懂。
我们现在来看一下`checkresult.txt`文件，这里面基本包含了我们关心的各项数据。下一步，我们通过Python对这些数据进行简单的处理。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200308211107864.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)
## 三、编写Python
```python
encoding=utf-8
import re
import os
import sys
import datetime
#-------------------------------------------------------------------
#定义一个读文件的函数，读取之前shell脚本生成的checkresult文件
def read_file_as_str(file_path):
    # 判断路径文件存在
    if not os.path.isfile(file_path):
        raise TypeError(file_path + " does not exist")

    all_the_text = open(file_path).read()
    # print type(all_the_text)
    return all_the_text

#-------------------------------------------------------------------
#定义一个按照关键字查找关键字前后固定长度的函数
def find_str_as_keyword(str_all,keyword,start,end):
        start=int(start)
        end=int(end)
        len_start=str_all.find(keyword)+start
        len_end=str_all.find(keyword)+end
        #print len_start
        #print len_end
        echo_str=str_all[len_start:len_end]
        return echo_str
#-------------------------------------------------------------------
#定义一个按照两个关键字查找关键字之间内容的函数
def between_str_as_keyword(str_all,keyword1,keyword2,keyword1_start=0,keyword2_end=0):
        keyword1_start=int(keyword1_start)
        keyword2_end=int(keyword2_end)
        len_start=str_all.find(keyword1)+keyword1_start
        len_end=str_all.find(keyword2)+keyword2_end
        #print len_start
        #print len_end
        echo_str=str_all[len_start:len_end]
        return echo_str
#-------------------------------------------------------------------
def main(input_file_path,output_file_path,hostname):
        checkresult=read_file_as_str(input_file_path)
        #注意：
        #搜索结果=find_str_as_keyword(待搜索字符串,关键字,搜索结果起始长度,搜索结束长度)
        #搜索keyword保证不能重复，尽可能搜索长的关键字
        #起始和结束长度从keyword第一个字符串算起，且包含keyword本身长度
        #packetloss=find_str_as_keyword(checkresult,"packet loss",-3,11)
        packetloss=between_str_as_keyword(checkresult,"received,","% packet loss",10)
        #注意丢包率长度会变-使用between函数查找区间
        minavgmaxmdev=between_str_as_keyword(checkresult,"min/avg/max/mdev","wlan0",19,-1)
        PingMin=minavgmaxmdev[0:minavgmaxmdev.find("/")]
        minavgmaxmdev=minavgmaxmdev[minavgmaxmdev.find("/")+1:]
        PingAvg=minavgmaxmdev[0:minavgmaxmdev.find("/")]
        minavgmaxmdev=minavgmaxmdev[minavgmaxmdev.find("/")+1:]
        PingMax=minavgmaxmdev[0:minavgmaxmdev.find("/")]
        minavgmaxmdev=minavgmaxmdev[minavgmaxmdev.find("/")+1:]
        PingMdev=minavgmaxmdev[0:minavgmaxmdev.find(" ms")]
        #抖动值字符串多次截取/与/之间的内容，原文格式类似于：2.103/9.325/29.067/8.392 ms
        totaltime=between_str_as_keyword(checkresult,"loss, time","rtt min/",11,-3)
        #注意总时间字符串长度会变-使用between函数查找区间
        AccessPoint=find_str_as_keyword(checkresult,"Access Point:",14,31)
        Frequency=between_str_as_keyword(checkresult,"Frequency:"," GHz",10)
        #注意信道选择字符串长度会变-使用between函数查找区间
        BitRate=between_str_as_keyword(checkresult,"Bit Rate="," Mb/s   Tx-Power",9)
        #注意连接速率长度会变
        LinkQuality=between_str_as_keyword(checkresult,"Link Quality=","/70  Signal level",13)
        #注意连接质量长度--可能--会变
        Signallevel=between_str_as_keyword(checkresult,"Signal level=","Rx invalid",13,-17)
        WlanGWIP=between_str_as_keyword(checkresult,"--- "," ping statistics ---",4)
        DeviceTemp=between_str_as_keyword(checkresult,"<device_temp>","</device_temp>",14,-1)
        DeviceTemp=float(DeviceTemp)/1000
        Eth0_IP=between_str_as_keyword(checkresult,"<device_eth0ip>","</device_eth0ip>",16,-1)
        WLAN_IP=between_str_as_keyword(checkresult,"<device_wlanip>","</device_wlanip>",16,-1)
     write_file_as_path(output_file_path,packetloss,PingMin,PingAvg,PingMax,PingMdev,totaltime,AccessPoint,Frequency,BitRate,LinkQuality,Signallevel,hostname,WlanGWIP,DeviceTemp,Eth0_IP,WLAN_IP)




if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2],sys.argv[3])
```

下面是XML文档生成的代码，先看一下，之后我们详细讲解PRTG的XML文件字段届时

```python
#-------------------------------------------------------------------
#下面这一大段是生成xml文件的函数
def write_file_as_path(file_path,write_packetloss,write_PingMin,write_PingAvg,write_PingMax,write_PingMdev,write_totaltime,write_AccessPoint,write_Frequency,write_BitRate,write_LinkQuality,write_Signallevel,write_hostname,write_WlanGWIP,write_DeviceTemp,write_Eth0_IP,write_WLAN_IP):
        f=open(file_path,'w')
        #with open(file_path,'w',encoding='gbk') as f:
        f.write('<?xml version="1.0" encoding="Windows-1252" ?>\n')
        f.write('<prtg>\n')
        f.write('   <result>\n')
        f.write('       <channel>Packet loss</channel>\n')
        f.write('       <unit>Percent</unit>\n')
        f.write('       <mode>Absolute</mode>\n')
        f.write('       <LimitMaxError>20</LimitMaxError>\n')
        f.write('       <LimitMaxWarning>10</LimitMaxWarning>\n')
        f.write('       <value>'+write_packetloss+'</value>\n')
        f.write('   </result>\n')
        f.write('   <result>\n')
        f.write('       <channel>Ping Min Time</channel>\n')
        f.write('       <CustomUnit>ms</CustomUnit>\n')
        f.write('       <mode>Absolute</mode>\n')
        f.write('       <float>1</float>\n')
        f.write('       <value>'+write_PingMin+'</value>\n')
        f.write('   </result>\n')
        f.write('   <result>\n')
        f.write('       <channel>Ping Max Time</channel>\n')
        f.write('       <CustomUnit>ms</CustomUnit>\n')
        f.write('       <mode>Absolute</mode>\n')
        f.write('       <float>1</float>\n')
        f.write('       <LimitMaxError>500</LimitMaxError>\n')
        f.write('       <LimitMaxWarning>200</LimitMaxWarning>\n')
        f.write('       <value>'+write_PingMax+'</value>\n')
        f.write('   </result>\n')
        f.write('   <result>\n')
        f.write('       <channel>Ping Avg Time</channel>\n')
        f.write('       <CustomUnit>ms</CustomUnit>\n')
        f.write('       <mode>Absolute</mode>\n')
        f.write('       <float>1</float>\n')
        f.write('       <LimitMaxError>100</LimitMaxError>\n')
        f.write('       <LimitMaxWarning>50</LimitMaxWarning>\n')
        f.write('       <value>'+write_PingAvg+'</value>\n')
        f.write('   </result>\n')
        f.write('   <result>\n')
        f.write('       <channel>Ping Mean Deviation Time</channel>\n')
        f.write('       <CustomUnit>ms</CustomUnit>\n')
        f.write('       <mode>Absolute</mode>\n')
        f.write('       <float>1</float>\n')
        f.write('       <value>'+write_PingMdev+'</value>\n')
        f.write('   </result>\n')
        f.write('   <result>\n')
        f.write('       <channel>Ping Total Time</channel>\n')
        f.write('       <CustomUnit>ms</CustomUnit>\n')
        f.write('       <mode>Absolute</mode>\n')
        f.write('       <float>1</float>\n')
        f.write('       <value>'+write_totaltime+'</value>\n')
        f.write('   </result>\n')
        f.write('   <result>\n')
        f.write('       <channel>Radio Frequency</channel>\n')
        f.write('       <CustomUnit>GHz</CustomUnit>\n')
        f.write('       <mode>Absolute</mode>\n')
        f.write('       <float>1</float>\n')
        f.write('       <value>'+write_Frequency+'</value>\n')
        f.write('   </result>\n')
        f.write('   <result>\n')
        f.write('       <channel>Radio BitRate</channel>\n')
        f.write('       <CustomUnit>Mb/s</CustomUnit>\n')
        f.write('       <mode>Absolute</mode>\n')
        f.write('       <float>1</float>\n')
        f.write('       <LimitMinError>50</LimitMinError>\n')
        f.write('       <LimitMinWarning>70</LimitMinWarning>\n')
        f.write('       <value>'+write_BitRate+'</value>\n')
        f.write('   </result>\n')
        f.write('   <result>\n')
        f.write('       <channel>Radio LinkQuality</channel>\n')
        f.write('       <CustomUnit>/70</CustomUnit>\n')
        f.write('       <mode>Absolute</mode>\n')
        f.write('       <value>'+write_LinkQuality+'</value>\n')
        f.write('   </result>\n')
        f.write('   <result>\n')
        f.write('       <channel>Radio Signallevel</channel>\n')
        f.write('       <CustomUnit>dBm</CustomUnit>\n')
        f.write('       <mode>Absolute</mode>\n')
        f.write('       <value>'+write_Signallevel+'</value>\n')
        f.write('   </result>\n')
        f.write('   <result>\n')
        f.write('       <channel>Probe Temperature</channel>\n')
        f.write('       <Unit>Temperature</Unit>\n')
        f.write('       <mode>Absolute</mode>\n')
        f.write('       <float>1</float>\n')
        f.write('       <LimitMaxError>60</LimitMaxError>\n')
        f.write('       <LimitMaxWarning>55</LimitMaxWarning>\n')
        f.write('       <value>'+str(write_DeviceTemp)+'</value>\n')
        f.write('   </result>\n')
        f.write('   <text>Updatetime:'+datetime.datetime.now().strftime('%H:%M:%S')+' Eth0_IP:'+write_Eth0_IP+' Wlan_IP:'+write_WLAN_IP+' WLAN Gateway IP:'+write_WlanGWIP+' AccessPoint:'+write_AccessPoint+'</text>\n')
        f.write('</prtg>\n')
        f.close()
```
## 四、PRTG系统配置
在PRTG探针所在的操作系统里编写如下脚本。
由于树莓派送过来的XML文件的命名格式都是：`主机名-WIFI_Check_result.txt`
所以我们的BAT脚本可以通过%1传入的参数来打印对应主机名设备的上报信息

```python
@echo off
chcp 65001
type "C:\00-tftp\%1-WIFI_Check_result.txt"
```

保存到

```python
C:\Program Files (x86)\PRTG Network Monitor\Custom Sensors\EXEXML
```

然后，在PRTG系统里面，添加传感器，搜索“EXE”，选择“高级EXE/脚本”
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200308212054936.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70 =600x)
EXE/脚本选择刚才保存的bat文件
参数填入树莓派的主机名，这样本地的脚本带入参数后，会获取你指定的树莓派的上报信息
互斥名称尽量跟参数保持一致。PRTG将逐一执行 (并非同时执行)拥有相同互斥名称的所有 EXE/脚本传感器。如果您拥有大量传感器并想要避免由同时运行进程所引起的资源高度使用，这十分有用。
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200308212246135.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)
到这基本就搞定了，你可以在这个传感器内看到刚才树莓派收集到的各种信息。
![在这里插入图片描述](https://img-blog.csdnimg.cn/2020030821300995.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)
## 五、树莓派shell脚本配置定时执行
定时执行配置很简单

```python
crontab -e
```
打开定时任务执行列表，在最后添加上一句

```python
*/1 * * * * sh /home/pi/checknetwork.sh
```
脚本地址就是我们刚才写好的shell脚本。
注意，crontab运行脚本的时候是不带系统变量的，所以我们之前的脚本里已经提前写了PATH变量。

```python
PATH=/etc:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin
```
当然还有一种办法，你再写个脚本，来调这个脚本。比如随便在root目录下写个脚本，就写一句话，调用checknetwork.sh。这样也可以避免PATH不同步的情况。

```python
#!/bin/bash
/home/pi/checknetwork.sh
```

----
# 进阶提高
看到这里，基本功能都实现了，但是接下来我们还有一些高阶的应用
## 一、多个树莓派自动更新脚本
对于网内所有的树莓派，如果shell脚本或者python程序出现迭代更新，我们设计了一个办法统一下发新版本的shell脚本和python到所有的树莓派。这对于网内有几十个树莓派的时候，非常有用。
找一台linux主机做版本服务器，写个下面的脚本

```python
#!/bin/bash

TFTPPATH="/root/tftp_file"
IPLISTPATH="/root/PRTG_WIFI_Probe/IPlist"

rm -f $IPLISTPATH/*
mv $TFTPPATH/IP-WIFI* $IPLISTPATH/

find $IPLISTPATH/ -mmin +2 -name "IP-WIFI*" -exec rm {} \;
#保留最近2分钟内更新过的IP-WIFI-*****.txt文件，之前的删除掉
cat $IPLISTPATH/IP-WIFI* > /root/PRTG_WIFI_Probe/IPlist_all.txt
#合并所有的IP-WIFI-*****.txt
for ip in `cat /root/PRTG_WIFI_Probe/IPlist_all.txt | tr -d "\r" `
do
        echo "sent file to "$ip
        scp /root/PRTG_WIFI_Probe/programfile/checknetwork.py $ip:/home/pi 
        scp /root/PRTG_WIFI_Probe/programfile/checknetwork.sh $ip:/home/pi 

done
#全部下发一遍文件
```
这里面，就涉及到了之前在树莓派上的一段骚操作。

```python
NIC=$(route -n | grep UG | awk '{print $8}'| awk 'NR==1')
ifconfig $NIC | grep "inet " | awk '{print $2}' >> IP-WIFI-Check-$HOSTNAME.txt
#这两句详细解释一下
#第一句，获取当年设备缺省路由表第一行的记录，并提取其中的网卡设备名
#第二句，获取此网卡目前的IP地址
#这个地址是目前树莓派与服务器通信的主地址。仅连接无线的情况为wlan0 IP地址，同时连接有线无线的时候为eth0 IP地址
#这个地址，之后集中下发脚本的时候用得到
```
是不是突然想发出~ 哦~的一声赞叹，赞叹这个设计的精妙。
为了更方便，可以提前把这台服务器的SSH-Keygen公钥发送到所有树莓派上，这样scp完全无密码下发文件
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200308214538771.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3l0bHpxMDIyOA==,size_16,color_FFFFFF,t_70)
## 二、树莓派保活探测
本例中，PRTG系统会读取生成的XML文件，只要这个文件存在，系统就不会告警。
因此，如果某个树莓派出现异常，不继续更新上报信息的时候。我们需要一个机制来探测，XML文件是否一直在正常更新
在PRTG探针所在的服务器上，编写以下BAT脚本

```powershell
@echo off&setlocal enabledelayedexpansion

for /f "tokens=1 delims=" %%i in ('dir C:\00-tftp /tw ^| find /i "%1-WIFI_Check_result.txt"  ') do set timeresult=%%i

set ma=%timeresult:~15,2%
set mb=%time:~3,2%

set /a ma=1%ma%-100
set /a mb=1%mb%-100
#以上两句是去除分钟为08时的异常。BAT脚本对于08xxx的数字会认为是8进制
set /a mc=%mb%-%ma%

if %mc% gtr 2 (echo %mc%:Error Time Out) else (echo %mc%:Active)
```
然后，放到如下的路径下

```python
C:\Program Files (x86)\PRTG Network Monitor\Custom Sensors\EXE
```
好了，去PRTG添加一个自定义传感器，使用这个脚本，传参为设备名。XML文件超过2分钟没更新就告警咯。

## 三、PRTG XML格式自定义传感器XML解释
来个示例

XML Return Format: Minimum Example:

    <prtg>
    	<result>
   		 <channel>通道1名称</channel>
   		 <value>通道值</value>
    </result>
    <result>
    	<channel>通道2名称</channel>
    	<value>通道值</value>
    </result>
    <text>自定义文本传递</text>
    <error>自定义错误消息</error>
    </prtg>

result 字段内可选的标签如下：
TAG|MANDATORY|DESCRIPTION|POSSIBLE CONTENT
-|-|----------|:-
《Channel》|Yes|Name of the channel as displayed in user interfaces./ This parameter is required and must be unique for the sensor.|Any string
《Value》|Yes|The value as integer or float./ Make sure the 《Float》 setting matches the kind of value provided. Otherwise PRTG shows 0 values.|Integer or float value
《Unit》|No|The unit of the value. The default is Custom. This is useful for PRTG to be able to convert volumes and times.|BytesBandwidth/BytesDisk/Temperature/Percent/TimeResponse/TimeSeconds/Custom/Count/CPU: This is a % unit that is accounted to the CPU load in index graphs./BytesFile/SpeedDisk/SpeedNet/TimeHours
《CustomUnit》|No|If Custom is used as unit, this is the text displayed behind the value.|Any string (keep it short
《SpeedSize》《VolumeSize》|No|Size used for the display value. For example, if you have a value of 50000 and use Kilo as size, the display is 50 kilo #./The default is One (value used as returned). For the Bytes and Speed units, this is overridden by the setting in the user interface.|One/Kilo/Mega/Giga/Tera/Byte/KiloByte/MegaByte/GigaByte/TeraByte/Bit/KiloBit/MegaBit/GigaBit/TeraBit
《SpeedTime》|No|See above, used when displaying the speed. The default is Second.|Second/Minute/Hour/Day
《Mode》|No|Select if the value is an absolute value or counter. The default is Absolute.|Absolute/Difference
《Float》|No|Define if the value is a float. The default is 0 (no). If set to 1 (yes), use a dot as decimal separator in values./ Define decimal places with the 《DecimalMode》 element.|0 (= no, integer)/1 (= yes, float)
《DecimalMode》|No|Init value for the Decimal Places option. If 0 is used in the 《Float》 element (use integer), the default is Auto. Otherwise (for float) the default is All./ You can change this initial setting later in the sensor's channel settings.|Auto/All
《Warning》|No|If enabled for at least one channel, the entire sensor is set to "Warning" status. The default is 0 (no).|0 (= no)/1 (= yes)
《ShowChart》|No|Init value for the Show in graphs option. The default is 1 (yes)./ The values defined with this element are only considered during the first sensor scan when the channel is newly created. They are ignored on all further sensor scans (and may be omitted). You can change this initial setting later in the sensor's channel settings.|0 (= no)/1 (= yes)
《ShowTable》|No|Init value for the Show in tables option. The default is 1 (yes)./ The values defined with this element are only considered during the first sensor scan when the channel is newly created. They are ignored on all further sensor scans (and may be omitted). You can change this initial setting later in the sensor's channel settings.|0 (= no)/1 (= yes)
《LimitMaxError》|No|Define an upper error limit for the channel. If enabled, the sensor is set to a Down status if this value is overrun and the LimitMode is activated./ Provide the limit value in the unit of the base data type, just as used in the 《Value》 element of this section. While a sensor shows a Down status triggered by a limit, it still receives data in its channels./ The values defined with this element are only considered during the first sensor scan when the channel is newly created. They are ignored on all further sensor scans (and may be omitted). You can change this initial setting later in the sensor's channel settings.|String with numbers, surrounded by quotation marks (")
《LimitMaxWarning》|No|Define an upper warning limit for the channel. If enabled, the sensor is set to a Warning status if this value is overrun and the LimitMode is activated./ Provide the limit value in the unit of the base data type, just as used in the 《Value》 element of this section. While a sensor shows a Down status triggered by a limit, it still receives data in its channels./ The values defined with this element are only considered during the first sensor scan when the channel is newly created. They are ignored on all further sensor scans (and may be omitted). You can change this initial setting later in the sensor's channel settings.|String with numbers, surrounded by quotation marks (")
《LimitMinWarning》|No|Define a lower warning limit for the channel. If enabled, the sensor is set to a Warning status if this value is undercut and the LimitMode is activated./ Provide the limit value in the unit of the base data type, just as used in the 《Value》 element of this section. While a sensor shows a Down status triggered by a limit, it still receives data in its channels./ The values defined with this element are only considered during the first sensor scan when the channel is newly created. They are ignored on all further sensor scans (and may be omitted). You can change this initial setting later in the sensor's channel settings.|String with numbers, surrounded by quotation marks (")
《LimitMinError》|No|Define a lower error limit for the channel. If enabled, the sensor is set to a Down status if this value is undercut and the LimitMode is activated./ Provide the limit value in the unit of the base data type, just as used in the 《Value》 element of this section. While a sensor shows a Down status triggered by a limit, it still receives data in its channels./ The values defined with this element are only considered during the first sensor scan when the channel is newly created. They are ignored on all further sensor scans (and may be omitted). You can change this initial setting later in the sensor's channel settings.|String with numbers, surrounded by quotation marks (")
《LimitErrorMsg》|No|Define an additional message. It is added to the sensor's message when entering a Down status that is triggered by a limit./ The values defined with this element are only considered during the first sensor scan when the channel is newly created. They are ignored on all further sensor scans (and may be omitted). You can change this initial setting later in the sensor's channel settings.|Any string
《LimitWarningMsg》|No|Define an additional message. It is added to the sensor's message when entering a Warning status that is triggered by a limit./ The values defined with this element are only considered during the first sensor scan when the channel is newly created. They are ignored on all further sensor scans (and may be omitted). You can change this initial setting later in the sensor's channel settings.|Any string
《LimitMode》|No|Define if the limit settings defined above are active. The default is 0 (no; limits inactive). If 0 is used, the limits are written to the sensor channel settings as predefined values, but limits are disabled./ The values defined with this element are only considered during the first sensor scan when the channel is newly created. They are ignored on all further sensor scans (and may be omitted). You can change this initial setting later in the sensor's channel settings.|0 (= no)/1 (= yes)
《ValueLookup》|No|Define if you want to use a lookup file (for example, to view integer values as status texts). Enter the ID of the lookup file that you want to use, or omit this element to not use lookups./ The values defined with this element are only considered during the first sensor scan when the channel is newly created. They are ignored on all further sensor scans (and may be omitted). You can change this initial setting later in the sensor's channel settings.|Any string
《NotifyChanged》|No|If a returned channel contains this tag, it triggers a change notification that you can use with the Change Trigger to send a notification.|No content requir
/



# 搞定！


# encoding=utf-8
#格式化sh脚本传递的文件，并生成PRTG对应的xml格式文件
import re
import os
import sys
import datetime

def read_file_as_str(file_path):
    # 判断路径文件存在
    if not os.path.isfile(file_path):
        raise TypeError(file_path + " does not exist")

    all_the_text = open(file_path).read()
    # print type(all_the_text)
    return all_the_text

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

def find_str_as_keyword(str_all,keyword,start,end):
	start=int(start)
	end=int(end)
	len_start=str_all.find(keyword)+start
	len_end=str_all.find(keyword)+end
	#print len_start
	#print len_end
	echo_str=str_all[len_start:len_end]
	return echo_str

def between_str_as_keyword(str_all,keyword1,keyword2,keyword1_start=0,keyword2_end=0):
	keyword1_start=int(keyword1_start)
	keyword2_end=int(keyword2_end)
	if str_all.find(keyword1) != -1 and str_all.find(keyword1) != -1:
		len_start=str_all.find(keyword1)+keyword1_start
		len_end=str_all.find(keyword2)+keyword2_end
		echo_str=str(str_all[len_start:len_end])
		return echo_str
	else:
		echo_str='N/A'
		return echo_str

def main(input_file_path,output_file_path,hostname):
	checkresult=read_file_as_str(input_file_path)
	#注意：
	#搜索结果=find_str_as_keyword(待搜索字符串,关键字,搜索结果起始长度,搜索结束长度)
	#搜索keyword保证不能重复，尽可能搜索长的关键字
	#起始和结束长度从keyword第一个字符串算起，且包含keyword本身长度
	packetloss=between_str_as_keyword(checkresult,"received,","% packet loss",10)
	#注意丢包率长度会变-使用between函数查找区间
	minavgmaxmdev=between_str_as_keyword(checkresult,"min/avg/max/mdev","wlan0",19,-1)
	if minavgmaxmdev =='N/A':
		PingMin=PingAvg=PingMax=PingMdev='N/A'
	else:
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
	DeviceTemp=str(float(DeviceTemp)/1000)
	Eth0_IP=between_str_as_keyword(checkresult,"<device_eth0ip>","</device_eth0ip>",16,-1)
	WLAN_IP=between_str_as_keyword(checkresult,"<device_wlanip>","</device_wlanip>",16,-1)

	print ('packetloss:----\n'+packetloss)
	print ('PingMin:----\n'+PingMin)
	print ('PingAvg:----\n'+PingAvg)
	print ('PingMax:----\n'+PingMax)
	print ('PingMdev:----\n'+PingMdev)
	print ('totaltime:----\n'+totaltime)
	print ('AccessPoint:----\n'+AccessPoint)
	print ('Frequency:----\n'+Frequency)
	print ('BitRate:----\n'+BitRate)
	print ('LinkQuality:----\n'+LinkQuality)
	print ('Signallevel:----\n'+Signallevel)
	print ('WlanGWIP:----\n'+WlanGWIP)
	print ('DeviceTemp:----\n'+DeviceTemp)
	print ('Eth0_IP:----\n'+Eth0_IP)
	print ('WLAN_IP:----\n'+WLAN_IP)
	write_file_as_path(output_file_path,packetloss,PingMin,PingAvg,PingMax,PingMdev,totaltime,AccessPoint,Frequency,BitRate,LinkQuality,Signallevel,hostname,WlanGWIP,DeviceTemp,Eth0_IP,WLAN_IP)
	print (read_file_as_str(output_file_path))




if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2],sys.argv[3])





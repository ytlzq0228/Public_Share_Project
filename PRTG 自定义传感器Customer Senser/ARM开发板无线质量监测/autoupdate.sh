#!/bin/bash
#服务器统一下发脚本文件到所有终端

TFTPPATH="/root/dlp_script/tftp_file"
IPLISTPATH="/root/PRTG_WIFI_Probe/IPlist"

rm -f $IPLISTPATH/*

mv $TFTPPATH/IP-wlan* $IPLISTPATH/

find $IPLISTPATH/ -mmin +2 -name "IP-wlan*" -exec rm {} \;

cat $IPLISTPATH/IP-wlan* > /root/PRTG_WIFI_Probe/IPlist_all.txt


for ip in `cat /root/PRTG_WIFI_Probe/IPlist_all.txt | tr -d "\r" `
do
	echo "sent file to "$ip
	scp /root/PRTG_WIFI_Probe/programfile/checknetwork.py $ip:/home/pi 
	scp /root/PRTG_WIFI_Probe/programfile/checknetwork.sh $ip:/home/pi 

done


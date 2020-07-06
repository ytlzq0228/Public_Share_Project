#!/bin/bash、
#采集样本数据，交由Python格式化处理，并通过TFTP上报到PRTG服务器
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


wlangwip=$(route | grep wlan0 | grep default)
wlangwip=${wlangwip##*default} 
wlangwip=${wlangwip%%0.0.0.0*}


# route | grep wlan0 | grep default like this:
#default         10.0.192.1      0.0.0.0         UG    100    0        0 wlan0


ping -c 200 -i 0.1 $wlangwip >> checkresult.txt

iwconfig wlan0 >> checkresult.txt

echo '<device_temp>' >> checkresult.txt

cat /sys/class/thermal/thermal_zone0/temp >> checkresult.txt

echo '</device_temp>' >> checkresult.txt


echo '<device_eth0ip>' >> checkresult.txt

ifconfig eth0 | grep "inet " | awk '{print $2}' >> checkresult.txt

echo '</device_eth0ip>' >> checkresult.txt

echo '<device_wlanip>' >> checkresult.txt

ifconfig wlan0 | grep "inet " | awk '{print $2}' >> checkresult.txt

echo '</device_wlanip>' >> checkresult.txt

NIC=$(route -n | grep UG | awk '{print $8}'| awk 'NR==1')
ifconfig $NIC | grep "inet " | awk '{print $2}' >> IP-WIFI-Check-$HOSTNAME.txt

#cat checkresult.txt

python checknetwork.py checkresult.txt $HOSTNAME-WIFI_Check_result.txt $HOSTNAME

tftp 10.0.20.178 << !
put $HOSTNAME-WIFI_Check_result.txt
put IP-WIFI-Check-$HOSTNAME.txt
quit
!
tftp 10.0.20.20 << !
put IP-WIFI-Check-$HOSTNAME.txt
quit
!


rm -f checkresult.txt
rm -f $HOSTNAME-WIFI_Check_result.txt
rm -f IP-WIFI-Check-$HOSTNAME.txt


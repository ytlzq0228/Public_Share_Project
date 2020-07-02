#Aruba IAP模式下SNMP获取用户连接数
@echo off
del clientnumber.txt
del clientnumber-output.txt
"C:\usr\bin\snmpwalk.exe"  -v 2c -c AkuLakusnmp 10.0.18.254 1.3.6.1.4.1.14823.2.3.3.1.2.4.1.1 | find /v /c "" >>clientnumber.txt
echo :OK >>clientnumber.txt
setlocal enabledelayedexpansion
(for /f "delims=" %%i in ('type "clientnumber.txt"') do (
    set /p =%%i<nul
))>"clientnumber-output.txt"
type clientnumber-output.txt

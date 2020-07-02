
#主机提前配置KMS服务器地址，用于探测KMS激活服务可用性
@echo off
cscript //Nologo %windir%\system32\slmgr.vbs /ato | find /i "¥ÌŒÛ" &&(echo.&echo err:0001 & echo.)||(echo 200:OK )

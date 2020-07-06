#检测某个目录下文件的存活时间
@echo off&setlocal enabledelayedexpansion

rem for /f "tokens=2 delims= " %%i in ('dir C:\00-tftp /tw ^| find /i "%1-WIFI_Check_result.txt"  ') do set timeresult=%%i
for /f "tokens=1 delims=" %%i in ('dir C:\00-tftp /tw ^| find /i "%1-WIFI_Check_result.txt"  ') do set timeresult=%%i

echo %timeresult%

set ma=%timeresult:~15,2%
set mb=%time:~3,2%

set /a ma=1%ma%-100
set /a mb=1%mb%-100

echo %ma%
echo %mb%

set /a mc=%mb%-%ma%

rem echo %mc%:Time

rem echo 0:Active

if %mc% gtr 2 (echo %mc%:Error Time Out) else (echo %mc%:Active)






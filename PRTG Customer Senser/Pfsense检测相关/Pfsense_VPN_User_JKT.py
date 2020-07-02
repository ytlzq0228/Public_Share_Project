# coding=utf-8
#Python抓取Pfsense http://10.2.2.2/status_openvpn.php 页面查看当前OpenVPN用户数量
import datetime
import re
import sys
import time
import requests

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


def login():
    headers_base = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
        'Connection': 'keep-alive',
        # 'Host': '192.168.10.3',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
        'Referer': 'http://10.2.2.2/',
    }
    # 打开首页
    indexUrl = 'http://10.2.2.2/'
    postUrl = 'http://10.2.2.2/index.php'
    session = requests.session()
    #print (session.cookies)
    #print ('=======================')
    response1 = session.get(indexUrl, headers=headers_base)
    #print (response1.content)
    reg = r'var csrfMagicToken = "(.+)";var'
    csrftoken = re.findall(reg, response1.content.decode())[0]
    #print ("csrf"+csrftoken)
    #print (session.cookies)

    # 登录系统
    postdata1 = {
        '__csrf_magic': csrftoken,
        'usernamefld': 'prtgmonitor',
        'passwordfld': 'A********rtg',
        'login': 'Sign In'
    }

    login_resp = session.post(postUrl, data=postdata1, headers=headers_base)
    csrftoken2 = re.findall(reg, login_resp.content.decode())[0]
    return ( session, csrftoken2)


def get_VPN_User_data(session, csrftoken):
    # mac freeradius页面
	regid = r'id=(\d*)" class="btn btn-sm'
	freeradius_Url = 'http://10.2.2.2/status_openvpn.php'
	headers_base = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate, sdch',
		'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
		'Connection': 'keep-alive',
		# 'Host': '192.168.10.3',
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
		'Referer': 'http://10.2.2.2/',
	}
	resp = session.get(freeradius_Url, headers=headers_base)
	return resp.content.decode('UTF-8')

def check_data(response_data):
	response_data=between_str_as_keyword(response_data,"<div class=\"panel panel-default\" id=\"tabroute-0\" style=\"display: none;\">","<td colspan=\"4")
	response_data=between_str_as_keyword(response_data,"<tbody>","</tbody>")
	#筛选出VPN User Route路由表的部分
	response_data=response_data.replace('\t','').replace('\n','')
	response_data=response_data.split("</td>")
	i=0
	for line in response_data:
		#此处匹配VPNuser客户端地址
		if "<td>172.23." in line:
			#print (line)
			i+=1
	return(str(i))

def printxml(VPN_User_Number):
	print('<?xml version="1.0" encoding="Windows-1252" ?>')
	print('<prtg>')
	print('   <result>')
	print('       <channel>VPN User</channel>')
	print('       <CustomUnit>#</CustomUnit>')
	print('       <mode>Absolute</mode>')
	print('       <float>1</float>')
	print('       <value>'+VPN_User_Number+'</value>')
	print('   </result>')
	print('   <text>OpenVPN User number:'+VPN_User_Number+'#:OK</text>')
	print('</prtg>')

def main():
	session, csrftoken = login()
	response_data=get_VPN_User_data(session, csrftoken)
	VPN_User_Number=check_data(response_data)
	printxml(VPN_User_Number)
	#直接打印XML内容



if __name__ == '__main__':
    main()

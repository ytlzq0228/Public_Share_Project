
# coding=utf-8
#Python抓取Pfsense http://10.0.20.33/status_openvpn.php 页面查看当前OpenVPN用户数量
#研发预发环境VPN用户IP和用户名抓取，传递到NPS记账数据库
import pymssql
import datetime
import re
import sys

reload(sys)

sys.setdefaultencoding('utf8')
import time
import requests



server1 = "10.0.20.28"
server2 = "10.0.20.29"
user = "sa"
password = "P**********n"
database = "NPS"
conn = pymssql.connect(server1, user, password, database)
conn2 = pymssql.connect(server2, user, password, database)
cursor = conn.cursor()
cursor2 = conn2.cursor()

def CreateTable():
	sql = """
		IF OBJECT_ID('pre_rd_vpn', 'U') IS NOT NULL DROP TABLE pre_rd_vpn
		CREATE TABLE pre_rd_vpn (User_name VARCHAR(100),ip VARCHAR(100))
		"""
	cursor.execute(sql)
	conn.commit()
	cursor2.execute(sql)
	conn2.commit()


def InsertData(User_name,ip):
	sql = "INSERT INTO pre_rd_vpn(User_name,ip) VALUES ('"+User_name+"', '"+ip+"')"
	#data = [
	#    ('zhangsan', 15),
	#    ('lisi', 16),
	#    ('wangwu T.', 17)]
	#cursor.executemany(sql, data)
	# 如果没有指定autocommit属性为True的话就需要调用commit()方法
	cursor.execute(sql)
	conn.commit()
	cursor2.execute(sql)
	conn2.commit()
	print(User_name+":"+ip)


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
        'Referer': 'http://10.0.20.73/',
    }
    # 打开首页
    indexUrl = 'http://10.0.20.73/'
    postUrl = 'http://10.0.20.73/index.php'
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
        'usernamefld': 'admin',
        'passwordfld': 'P**********n',
        'login': 'Sign In'
    }

    login_resp = session.post(postUrl, data=postdata1, headers=headers_base)
    csrftoken2 = re.findall(reg, login_resp.content.decode())[0]
    return ( session, csrftoken2)


def get_VPN_User_data(session, csrftoken):
    # mac freeradius页面
	regid = r'id=(\d*)" class="btn btn-sm'
	freeradius_Url = 'http://10.0.20.73/status_openvpn.php'
	headers_base = {
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Encoding': 'gzip, deflate, sdch',
		'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
		'Connection': 'keep-alive',
		# 'Host': '192.168.10.3',
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
		'Referer': 'http://10.0.20.73/',
	}
	resp = session.get(freeradius_Url, headers=headers_base)
	return resp.content.decode('UTF-8')

def check_data(response_data):
	response_data=between_str_as_keyword(response_data,"<div class=\"panel panel-default\" id=\"tabroute-0\" style=\"display: none;\">","<td colspan=\"4")
	response_data=between_str_as_keyword(response_data,"<tbody>","</tbody>")
	#筛选出VPN User Route路由表的部分
	response_data=response_data.replace('\t','').replace('\n','').replace('<tbody>','')
	response_data=response_data.split("</td></tr>")
	del(response_data[-1])
	result=[]
	for line in response_data:
		line=line.replace("</td>","").split("<td>")
		linelist=[]
		linelist.append(line[1])
		linelist.append(line[3])
		result.append(linelist)
		
	return(result)


def main():
	session, csrftoken = login()
	response_data=get_VPN_User_data(session, csrftoken)
	userlist=check_data(response_data)
	for i in userlist:
		print(i)
	now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	CreateTable()
	InsertData(now_time,"Update Time")
	for data_sub in userlist:
		InsertData(data_sub[0],data_sub[1])




if __name__ == '__main__':
    main()

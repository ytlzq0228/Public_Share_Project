import json
import requests
import os

CORPID="ww*********8b1"
AGENTID="1*********2"
CORPSECRET="EHH*****************************9Kw"

def gettoken():
	try:
		headers = {"Content-Type": "text/plain"}
		request = requests.post(url="https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid="+CORPID+"&corpsecret="+CORPSECRET,headers=headers)
		request=json.loads(request.text)
		access_token=request['access_token']
	except Exception as err:
		raise err
	else:
		return access_token

class weixin:
	class get:
		def userid(user_dict,CNname):
			try:
				get_userid=get_username=get_email='N/A'
				get_userid=user_dict[CNname][0]
				get_username=user_dict[CNname][1]
				get_email=user_dict[CNname][2]
			except Exception as err:
				print("Get userid failed with CNname:"+CNname)
				raise err
			else:
				return get_userid,get_username,get_email
			
		def userinfo_verbose(access_token,userid):
			try:
				headers = {"Content-Type": "text/plain"}
				request = requests.post(url="https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token="+access_token+"&userid="+userid,headers=headers)
			except Exception as err:
				raise err
			else:
				return request.text
				
		def user_dict(access_token):
			try:
				user_dict=dict()
				headers = {"Content-Type": "text/plain"}
				request = requests.post(url="https://qyapi.weixin.qq.com/cgi-bin/user/list?access_token="+access_token+"&department_id=1&fetch_child=1",headers=headers)
				request=json.loads(request.text)
				all_user_list=request['userlist']
				for user in all_user_list:
					userid=user['userid']
					username=user['name']
					email=user['email']
					email_fix=email.find("@")
					CNname=email[:email_fix]
					user_dict[CNname]=[userid,username,email]
			except Exception as err:
				raise err
			else:
				return user_dict
				
			
	class post:
		def message(access_token,agentid,userid,username):
			try:
				headers = {"Content-Type": "text/plain"}
				data={
				"touser" : userid,
				"msgtype": "markdown",
				"agentid" : agentid,
				"markdown": {
						"content": '''**<font color="warning">【重要提示】</font>**
						>亲爱的**'''+username+'''**，您好：
						>
						>您的域账号密码即将过期，域账号密码有效期为180天
						>
						>请及时访问[**erp.csdn.com**](https://erp.csdn.com/Password.html)修改您的域账号密码。
						>
						>密码过期未修改会导致您无法连接集团WIFI，VPN，以及无法登陆各种业务系统！
						>
						>忘记域账号密码，请通过以下路径自助重置：
						>**ERP系统->新建申请->自助账号密码重置->AD域密码重置**'''
				},
				"enable_duplicate_check": 0,
				"duplicate_check_interval": 1800
				}
				request = requests.post(url="https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token="+access_token,headers=headers,json=data)
			except Exception as err:
				raise err
			else:
				return request.text

def main():
	try:
		command=os.popen("dsquery user -stalepwd 173 -o upn -limit 0")
		user_list_file=command.read()
		user_list_file=user_list_file.replace('""\n','').replace('"','').replace('@al.com','')
		sent_user_list=user_list_file.split("\n")
		access_token=gettoken()
		user_dict=weixin.get.user_dict(access_token)
		for i in range(len(sent_user_list)-1):
			try:
				userid,username,email=weixin.get.userid(user_dict,sent_user_list[i])
			except Exception as err:
				print(err)
			else:
				print(userid,username,email)
				sent_result=weixin.post.message(access_token,AGENTID,userid,username)
		
	except Exception as err:
		print(err)
		


if __name__ == '__main__':
	main()




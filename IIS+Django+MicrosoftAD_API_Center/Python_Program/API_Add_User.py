#coding=utf-8
import datetime
import os
import re
import sys
import time
import requests
import httplib2
import pprint
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account
import googleapiclient

SCOPES = ['https://www.googleapis.com/auth/admin.directory.user']
SERVICE_ACCOUNT_FILE = "C:\\VPNapi\\ApiSite\\GoogleAPI\\account_manager_service_account_cc97f7d70a741.json"
#授权空间（scope）和授权秘钥



def is_Chinese(strs):
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fff':
            return True
    return False
    
class APIrequest:

	def get_credentials():
		credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
		#授权应用访问G suit控制台，获取授权信息
		credentials = credentials.with_subject('accountapi@csdn.com')
		#委派管理员权限
		return credentials
		
	def get_user_data(credentials,userKey_in):
		try:
			service = build("admin", "directory_v1", credentials=credentials)
			results = service.users().get(userKey=userKey_in).execute()
		except googleapiclient.errors.HttpError as err:
			return err._get_reason()
			#异常处理方法详见google-api-python-client/googleapiclient/errors.py第47行
			#https://github.com/googleapis/google-api-python-client/blob/master/googleapiclient/errors.py
		else:
			return results

	def add_user(credentials,primaryEmail,familyName,givenName,password,orgUnitPath,PhoneNumber):
		try:
			insert_data={
				"name": {
					"familyName": familyName,
					"givenName": givenName,
					},
				 "password": password,
				 "primaryEmail": primaryEmail,
				 "changePasswordAtNextLogin": "true",
				 "orgUnitPath": orgUnitPath,
				 "recoveryPhone": PhoneNumber
				}
			service = build("admin", "directory_v1", credentials=credentials)
			results = service.users().insert(body=insert_data).execute()
		except Exception as err:
			raise err
		else:
			return results
			
class Microsoft_AD:
	
	def add_user(primaryEmail,familyName,givenName,password,orgUnitPath,PhoneNumber):
		email_fix=primaryEmail.find("@")
		email_CNname=primaryEmail[:email_fix]
		primaryEmail=email_CNname+"@al.com"
		#提出email的前缀，并更换后缀为@al.com
		if is_Chinese(familyName+givenName):
			cnname=familyName+givenName+email_CNname
			#中文姓名全程+邮箱前缀
		else:
			cnname=email_CNname
			#英文姓名直接为邮箱前缀
		#分别处理中英文CNname格式
		orgUnitPath=orgUnitPath[1:]
		#去除OU_PATH第一位的/
		
		os.system("dsadd user \"cn=%s,ou=%s,dc=al,dc=com\" -pwd %s -tel %s -upn %s" %(cnname,orgUnitPath,password,PhoneNumber,primaryEmail))
		

def main(primaryEmail,mail_password,ad_password,familyName,givenName,orgUnitPath,PhoneNumber):

	
	credentials=APIrequest.get_credentials()
	get_user_info=""
	i=0
	email_fix=primaryEmail.find("@")
	email_CNname=primaryEmail[:email_fix]
	email_domain=primaryEmail[email_fix:]
	PhoneNumber='+'+PhoneNumber
	while get_user_info != "Resource Not Found: userKey":
		if i != 0:
			primaryEmail=email_CNname+str(i)+email_domain
			#邮箱前缀步进+1
		get_user_info=APIrequest.get_user_data(credentials,primaryEmail)
		if get_user_info == "Resource Not Found: userKey":
			APIrequest.add_user(credentials,primaryEmail,familyName,givenName,mail_password,orgUnitPath,PhoneNumber)#添加google邮箱
			Microsoft_AD.add_user(primaryEmail,familyName,givenName,ad_password,orgUnitPath,PhoneNumber)#添加AD域账号
			#print(primaryEmail+" is a new user. Will add new user with this email")
		else:
			#print(primaryEmail+" is already exist. Try next one.")
			i=i+1
	return primaryEmail




if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6],sys.argv[7])




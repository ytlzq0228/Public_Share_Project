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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user']
SERVICE_ACCOUNT_FILE = BASE_DIR+"\\account_manager_service_account_cc97f7d70a741.json"
#授权空间（scope）和授权秘钥

class APIrequest:

	def get_credentials():
		try:
			credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
			#授权应用访问G suit控制台，获取授权信息
			credentials = credentials.with_subject('accountapi@akulaku.com')
			#委派管理员权限
		except Exception as err:
			raise err
		else:
			return credentials
		
	def get_user_data(userKey_in):
		try:
			credentials=APIrequest.get_credentials()
			service = build("admin", "directory_v1", credentials=credentials)
			results = service.users().get(userKey=userKey_in).execute()
		except Exception as err:
			return err
		else:
			return results
			
	def delete_user(userKey_in):
		try:
			credentials=APIrequest.get_credentials()
			service = build("admin", "directory_v1", credentials=credentials)
			results = service.users().delete(userKey=userKey_in).execute()
		except Exception as err:
			return err
		else:
			return results
			
		
	def update_user_password(userKey_in,password_in):
		try:
			credentials=APIrequest.get_credentials()
			update_data={"password": password_in,"changePasswordAtNextLogin": "true","suspended": "false"}
			service = build("admin", "directory_v1", credentials=credentials)
			results = service.users().update(userKey=userKey_in,body=update_data).execute()
		except Exception as err:
			return err
		else:
			return results
			
	def update_user_group(userKey_in,newgroup_in):
		try:
			credentials=APIrequest.get_credentials()
			update_data={"orgUnitPath": newgroup_in}
			service = build("admin", "directory_v1", credentials=credentials)
			results = service.users().update(userKey=userKey_in,body=update_data).execute()
		except Exception as err:
			return err
		else:
			return results
	
			
	def suspend_user(userKey_in):
		try:
			credentials=APIrequest.get_credentials()
			update_data={"suspended": "true"}
			service = build("admin", "directory_v1", credentials=credentials)
			results = service.users().update(userKey=userKey_in,body=update_data).execute()
		except Exception as err:
			return err
		else:
			return results
			
	def add_user(primaryEmail,familyName,givenName,password,orgUnitPath):
		try:
			credentials=APIrequest.get_credentials()
			insert_data={
				"name": {
					"familyName": familyName,
					"givenName": givenName,
					},
				 "password": password,
				 "primaryEmail": primaryEmail,
				 "changePasswordAtNextLogin": "true",
				  "orgUnitPath": orgUnitPath
				}
			service = build("admin", "directory_v1", credentials=credentials)
			results = service.users().insert(body=insert_data).execute()
		except Exception as err:
			return err
		else:
			return results

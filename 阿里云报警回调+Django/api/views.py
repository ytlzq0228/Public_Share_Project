import os
import logging
import sys
import json


from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from ApiSite.settings import BASE_DIR
from datetime import datetime


IIS_SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(r"%s\Python_Program"%IIS_SITE_DIR)


from save_log import save_log
from AliCloud_Alarm import AliCloud_Alarm

logger = logging.getLogger("sourceDns.webdns.views")



@csrf_exempt
def get_data(request):

	try:
		if request.META.get('HTTP_X_FORWARDED_FOR'):
			ip = request.META.get("HTTP_X_FORWARDED_FOR")
		else:
			ip = request.META.get("REMOTE_ADDR")
	except Exception as err:
		ip = 'unknow IP address'
	save_log("\n")
	save_log("Request from IP:%s"%ip)
	Request_method=request.method

	save_log("Request method is: %s"%Request_method)

		
	try:
		data = str(request.body,'utf-8').encode('utf-8').decode('unicode_escape')
		save_log("run_result:%s"%data)
		run_result=AliCloud_Alarm(data)

	except Exception as err:
		save_log("run_result:%s"%err)
		return JsonResponse({"msg": "%s"%err})
	else:
		save_log("run_result:%s"%run_result)
		return JsonResponse({"msg": run_result})


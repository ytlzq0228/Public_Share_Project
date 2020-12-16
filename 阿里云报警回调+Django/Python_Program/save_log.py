import os
import logging
import sys
from datetime import datetime


IIS_SITE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(r"%s\Python_Program"%IIS_SITE_DIR)



def save_log(result):
	try:
		now = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
		f = open(IIS_SITE_DIR+"\log\API_run_log.txt",'a')
		f.writelines("\n%s:log:%s" %(now,result))
		f.flush()
		f.close()
	except Exception as err:
		raise err

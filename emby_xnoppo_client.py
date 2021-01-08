import json
import os
import sys
import asyncio
from lib.Emby_ws import xnoppo_ws
from lib.Emby_http import *
import threading
import logging

def thread_function(ws_object):
    print("Thread: starting")
    ws_object.start()
    print("Thread: finishing")

cwd = os.path.dirname(os.path.abspath(__file__))
if sys.platform.startswith('win'):
    separador="\\"
else:
    separador="/"

config_file=cwd + separador + "config.json"
with open(cwd + separador + "config.json", 'r') as f:    
        config = json.load(f)
        logfile=cwd + separador + "emby_xnoppo_client_logging.log"
        if config["DebugLevel"]==0:
            logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',datefmt='%d/%m/%Y %I:%M:%S %p',level=logging.DEBUG)
        elif config["DebugLevel"]==1:
            rfh = logging.handlers.RotatingFileHandler(
                filename=logfile, 
                mode='a',
                maxBytes=50*1024*1024,
                backupCount=2,
                encoding=None,
                delay=0
            )
            logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',datefmt='%d/%m/%Y %I:%M:%S %p',level=logging.INFO,handlers=[rfh])
        elif config["DebugLevel"]==2:
            rfh = logging.handlers.RotatingFileHandler(
                filename=logfile, 
                mode='a',
                maxBytes=5*1024*1024,
                backupCount=2,
                encoding=None,
                delay=0
            )
            logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',datefmt='%d/%m/%Y %I:%M:%S %p',level=logging.DEBUG,handlers=[rfh])
        ## new options default config values
        default = config.get("Autoscript", False)
        config["Autoscript"]=default
        ##
        version=('Xnoppo Device Script V1.5')
        print (version)
        print ("Config File            : %s" % config_file)
        print ("Emby Server            : %s" % config["emby_server"])
        print ("User Name              : %s" % config["user_name"])
        print ("User Pass              : %s" % config["user_password"])
##        print ("Oppo User Name         : %s" % config["oppo_smb_user"])
##        print ("Oppo User Pass         : %s" % config["oppo_smb_pwd"])
        print ("Oppo IP                : %s" % config["Oppo_IP"])
        print ("Autostript             : %s" % config["Autoscript"])
        print ("Timeout_oppo_conection : %s" % config["timeout_oppo_conection"])
        print ("Timeout_oppo_playitem  : %s" % config["timeout_oppo_playitem"])
        print ("TV                     : %s" % config["TV"])
        print ("TV IP                  : %s" % config["TV_IP"])
        print ("TV KRY                 : %s" % config["TV_KEY"])
        print ("TV Device Name         : %s" % config["TV_DeviceName"])
        print ("DebugLevel             : %s" % config["DebugLevel"])
        print ("AV                     : %s" % config["AV"])
        print ("AV_Ip                  : %s" % config["AV_Ip"])
        print ("AV_Input               : %s" % config["AV_Input"])
        
        logging.info("%s",version)
        logging.info('OS                     : %s' % sys.platform)
        logging.info("Config File            : %s" % config_file)
        logging.info("Emby Server            : %s" % config["emby_server"])
        logging.info("User Name              : %s" % config["user_name"])
##      logging.info("User Pass              : %s" % config["user_password"])
##      logging.info("Oppo User Name         : %s" % config["oppo_smb_user"])
##      logging.info("Oppo User Pass         : %s" % config["oppo_smb_pwd"])
        logging.info("Oppo IP                : %s" % config["Oppo_IP"])
        logging.info("Autoscript             : %s" % config["Autoscript"])
        logging.info("Timeout_oppo_conection : %s" % config["timeout_oppo_conection"])
        logging.info("Timeout_oppo_playitem  : %s" % config["timeout_oppo_playitem"])
        logging.info("TV                     : %s" % config["TV"])
        logging.info("TV IP                  : %s" % config["TV_IP"])
        logging.info("TV KEY                 : %s" % config["TV_KEY"])
        logging.info("TV Device Name         : %s" % config["TV_DeviceName"])
        logging.info("DebugLevel             : %s" % config["DebugLevel"])
        logging.info("AV                     : %s" % config["AV"])
        logging.info("AV_Ip                  : %s" % config["AV_Ip"])
        logging.info("AV_Input               : %s" % config["AV_Input"])
        logging.info("MonitoredDevice        : %s" % config["MonitoredDevice"])
        server_list=config["servers"]
        logging.info("Servers            :")
        logging.info("-----------------------------------------------------------")
        for server in server_list:
            server_data = {}
            server_data["name"] = server["name"]
            server_data["Emby_Path"] = server["Emby_Path"]
            server_data["Oppo_Path"] = server["Oppo_Path"]
            logging.info("Server Name            : %s " % server_data["name"])
            logging.info("Emby Path              : %s " % server_data["Emby_Path"])
            logging.info("Oppo Path              : %s " % server_data["Oppo_Path"])
            logging.info("-----------------------------------------------------------")
        emby_wsocket = xnoppo_ws()
        emby_wsocket.ws_config=config
        emby_wsocket.config_file=config_file
        x = threading.Thread(target=thread_function, args=(emby_wsocket,))
        x.start()
        espera=0
        estado_anterior=''
        logging.debug('Entramos en el bucle\n')
        while 3>2:
            time.sleep(1)
            espera=espera+1
            if emby_wsocket.emby_state == estado_anterior:
                estado_anterior=emby_wsocket.emby_state
            else:
                logging.debug("Estado del Emby_Sockect: %s",emby_wsocket.emby_state)
                estado_anterior=emby_wsocket.emby_state   
        logging.info('Fin proceso')
        logging.info('Finished')

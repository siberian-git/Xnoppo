import hashlib
from urllib.parse import urlparse
from urllib.parse import quote
import urllib
import requests
import json
import os
import sys
import socket
import time
import telnetlib
import threading
import logging
from .Emby_http import EmbyHttp
from .Xnoppo_AVR import *
from .Xnoppo_TV import *


def sendnotifyremote(UDP_IP):
    UDP_PORT = 7624
    MESSAGE = "NOTIFY OREMOTE LOGIN"

    logging.debug ("UDP target IP: %s", UDP_IP)
    logging.debug ("UDP target port: %s", UDP_PORT)
    logging.debug ("message: %s", MESSAGE)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(bytes(MESSAGE, "utf-8"), (UDP_IP, UDP_PORT))

    return 0

def check_socket(config,session_id=None):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.info('Comprobando apertura del puerto del OPPO ')
    result = sock.connect_ex((config["Oppo_IP"],436))
    logging.debug("Resultado Chequeo: %s",str(result))
    net_retries=config["timeout_oppo_conection"]
    net_wait=0
    while result > 0 and net_wait<net_retries:
              time.sleep(1)
              net_wait=net_wait+1
              logging.info('Esperando apertura del puerto del OPPO')
              logging.info( 'Reintento %s',str(net_wait))
              #if session_id:
              #      response_timeout = send_message2(session_id, 'Esperando conectar con el OPPO, reintento: ' + str(net_wait))
              sendnotifyremote(config["Oppo_IP"])
              result = sock.connect_ex((config["Oppo_IP"],436))
    if net_wait>=net_retries:
            logging.info('Timeout esperando puerto del OPPO')
            #sys.exit("OPPO no disponible")
            #if session_id:
            #    response_timeout = send_message2(item_data["Id"], 'OPPO no disponible')
            return(1)
    else:
            logging.info('Puerto del OPPO abierto')
            return(0)

def getmainfirmwareversion(config):
    #if config["DebugLevel"]>0: print("getmainfirmwareversion\n")
    url = "http://" + config["Oppo_IP"] + ":436/getmainfirmwareversion"
    headers = {}
    #if config["DebugLevel"]>0: print (url)
    #if config["DebugLevel"]>0: print("\n")
    response = requests.get(url, headers=headers)
    #if config["DebugLevel"]>0: print (response.text)
    return response.text

def getsetupmenu(config):
    #if config["DebugLevel"]>0: print("getsetupmenu\n")
    url = "http://" + config["Oppo_IP"] + ":436/getsetupmenu"
    headers = {}
    #if config["DebugLevel"]>0: print (url)
    #if config["DebugLevel"]>0: print("\n")
    response = requests.get(url, headers=headers)
    #if config["DebugLevel"]>0: print (response.text)
    return response.text

def OppoSignin(config):
    #if config["DebugLevel"]>0: print("OppoSignin\n")
    #url = "http://" + config["Oppo_IP"] + ":436/signin?%7B%22appIconType%22%3A1%2C%22appIpAddress%22%3A%22" + config["emby_server"] + "%22%7D"
    url = "http://" + config["Oppo_IP"] + ":436/signin?%7B%22appIconType%22%3A1%2C%22appIpAddress%22%3A%22" + '192.168.1.135' + "%22%7D"
    headers = {}
    #if config["DebugLevel"]>0: print (url)
    #if config["DebugLevel"]>0: print("\n")
    response = requests.get(url, headers=headers)
    #if config["DebugLevel"]>0: print (response.text)
    return response.text

def getdevicelist(config):
    #if config["DebugLevel"]>0: print("getdevicelist\n")
    url = "http://" + config["Oppo_IP"] + ":436/getdevicelist"
    headers = {}
    #if config["DebugLevel"]>0: print (url)
    #if config["DebugLevel"]>0: print("\n")
    response = requests.get(url, headers=headers)
    #if config["DebugLevel"]>0: print (response.text)
    return response.text

def getglobalinfo(config):
    #if config["DebugLevel"]>0: print("getglobalinfo\n")
    url = "http://" + config["Oppo_IP"] + ":436/getglobalinfo"
    headers = {}
    #if config["DebugLevel"]>0: print (url)
    #if config["DebugLevel"]>0: print("\n")
    response = requests.get(url, headers=headers)
    #if config["DebugLevel"]>0: print (response.text)
    return response.text

def getplayingtime(config):
    #if config["DebugLevel"]>0: print("getplayingtime\n")
    url = "http://" + config["Oppo_IP"] + ":436/getplayingtime"
    headers = {}
    #if config["DebugLevel"]>0: print (url)
    #if config["DebugLevel"]>0: print("\n")
    response = requests.get(url, headers=headers)
    #if config["DebugLevel"]>0: print (response.text)
    return response.text

def mountSharedFolderID(server,folder,Username,Password,config):
    if config["DebugLevel"]==2:
        print("*** mountSharedFolderID ***")
    logging.debug("*** mountSharedFolder ***")
    #url = "http://" + config["Oppo_IP"] + ":436/mountSharedFolder?{%22server%22:%22" + server + "%22,%22bWithID%22:1,%22folder%22:%22"+folder+"%22,%22userName%22:%22"+Username+"%22,%22password%22:%22"+Password+"%22,%22bRememberID%22:1}"
    url1 = "http://" + config["Oppo_IP"] + ':436/mountSharedFolder?'
    url = ''
    url = url + '{"server":"' + server + '",'
    url = url + '"bWithID":1,"folder":"'+urllib.parse.quote(folder) + '",'
    url = url + '"userName":"'+Username + '",'
    url = url + '"password":"'+Password + '",'
    url = url + '"bRememberID":1}'
    headers = {}
    url = url1 + url
    logging.debug(url)
    try:
        response = requests.get(url, headers=headers,timeout=config["timeout_oppo_mount"])
    except:
        error = '{"success":false,"retInfo":"Timeout in Mount Request"}'
        return error
    if config["DebugLevel"]==2:
        print("*** Fin mountSharedFolderID ***")
    logging.debug("*** Mount Response: %s",response.text)
    return response.text

def mountSharedFolder(server,folder,Username,Password,config,checksmb=True):
    if config["DebugLevel"]==2:
        print("*** mountSharedFolder ***")
    logging.debug("*** mountSharedFolder ***")
    if config["smbtrick"]== True and checksmb == True:
            smbtrick(server + '/' + folder,config)
    #url = "http://" + config["Oppo_IP"] + ":436/mountSharedFolder?{%22server%22:%22" + server + "%22,%22bWithID%22:0,%22folder%22:%22"+folder+"%22,%22userName%22:%22"+Username+"%22,%22password%22:%22"+Password+"%22,%22bRememberID%22:1}"
    url1 = "http://" + config["Oppo_IP"] + ':436/mountSharedFolder?'
    url = ''
    url = url + '{"server":"' + server + '",'
    url = url + '"bWithID":0,"folder":"'+urllib.parse.quote(folder) + '",'
#    url = url + '"bWithID":0,"folder":"'+ folder + '",'
    url = url + '"userName":"''",'
    url = url + '"password":"''",'
    url = url + '"bRememberID":0}'
    headers = {}
    url = url1 + url
    logging.debug(url)
    try:
        response = requests.get(url, headers=headers,timeout=config["timeout_oppo_mount"])
    except:
        error = '{"success":false,"retInfo":"Timeout in Mount Request"}'
        return error   
    if config["DebugLevel"]==2:
        print(url)
        print(response.text)
        print("*** Fin mountSharedFolder ***")
    logging.debug("*** Mount Response: %s",response.text)
    return response.text

def mountSharedNFSFolder(server,folder,Username,Password,config):
    if config["DebugLevel"]==2:
        print("*** mountSharedFolder ***")
    logging.debug("*** mountSharedFolder ***")
    #url = "http://" + config["Oppo_IP"] + ":436/mountSharedFolder?{%22server%22:%22" + server + "%22,%22bWithID%22:0,%22folder%22:%22"+folder+"%22,%22userName%22:%22"+Username+"%22,%22password%22:%22"+Password+"%22,%22bRememberID%22:1}"
    url1 = "http://" + config["Oppo_IP"] + ':436/mountNfsSharedFolder?'
    url = ''
    url = url + '{"server":"' + server + '",'
    url = url + '"folder":"'+urllib.parse.quote(folder) + '"}'
    headers = {}
    url = url1 + url
    logging.debug(url)
    try:
        response = requests.get(url, headers=headers,timeout=config["timeout_oppo_mount"])
    except:
        error = '{"success":false,"retInfo":"Timeout in Mount Request"}'
        return error
    if config["DebugLevel"]==2:
        print(url)
        print(response.text)
        print("*** Fin mountSharedFolder ***")
    if response.text=='{}':
        error = '{"success":true,"retInfo":""}'
        return error
    logging.debug("*** Mount Response: %s",response.text)
    return response.text
#mountNfsSharedFolderAgain
 #   http://192.168.1.141:436/mountNfsSharedFolder?{"server":"192.168.1.39","folder":"volume1/Para_Ver/Peliculas"}
#    http://192.168.1.141:436/playnormalfile?{"path":"/mnt/nfs1/Valerian y la ciudad de los mil planetas (2017).iso","index":0,"type":1,"appDeviceType":2,"extraNetPath":"192.168.1.39","playMode":0}
    
def LoginNFS(config,server):
    logging.debug("LoginNFS")
    url = "http://" + config["Oppo_IP"] + ':436/loginNfsServer?{"serverName":"'+ str(server) + '"}'
    headers = {}
    logging.debug(url)
    response = requests.get(url, headers=headers)
    if config["DebugLevel"]==2:
        print("*** LoginNFS Response: " + response.text)
    logging.debug("*** LoginNFS Response: %s",response.text)
    return response.text

def umountSharedFolder(config):
    logging.info('*** umountSharedFolder ***')
    host = config["Oppo_IP"]
    port = 23
    user='root'
    try:
        session = telnetlib.Telnet(host, port, timeout = 10)
        session.read_until(b"login: ",10)
        session.write(user.encode('ascii') + b"\n")
        session.write(b"umount /mnt/cifs1\n")
        session.write(b"ls\n")
        session.write(b"exit\n")
        if config["DebugLevel"]>0: print(session.read_all().decode('ascii'))
        return("OK")
    except:
        return("ERROR unmounting")

def playnormalfile(server,filename,index,config,nfs):
    if config["DebugLevel"]==2:
        print("*** playnormalfile ***")
    logging.debug("*** playnormalfile ***")
    url0 = 'http://' + config["Oppo_IP"] + ':436/playnormalfile?{' + urllib.parse.quote('"path":"/mnt/cifs1/' + filename + '","index":'+ index +',"type":1,"appDeviceType":2,"extraNetPath":"'+ server + '","playMode":0')+'}'
    #url0 = "http://" + config["Oppo_IP"] + ":436/playnormalfile?{%22path%22:%22/mnt/cifs1/" + urllib.parse.quote(filename) + "%22,%22index%22:"+ index +",%22type%22:1,%22appDeviceType%22:2,%22extraNetPath%22:%22"+ server + "%22,%22playMode%22:0}"
    if nfs:
        #url0 = "http://" + config["Oppo_IP"] + ":436/playnormalfile?{%22path%22:%22/mnt/nfs1/" + urllib.parse.quote(filename) + "%22,%22index%22:"+ index +",%22type%22:1,%22appDeviceType%22:2,%22extraNetPath%22:%22"+ server + "%22,%22playMode%22:0}"
        url0 = 'http://' + config["Oppo_IP"] + ':436/playnormalfile?{' + urllib.parse.quote('"path":"/mnt/nfs1/' + filename + '","index":'+ index +',"type":1,"appDeviceType":2,"extraNetPath":"'+ server + '","playMode":0')+'}'
    else:
        url0 = 'http://' + config["Oppo_IP"] + ':436/playnormalfile?{' + urllib.parse.quote('"path":"/mnt/cifs1/' + filename + '","index":'+ index +',"type":1,"appDeviceType":2,"extraNetPath":"'+ server + '","playMode":0')+'}'
        #url0 = "http://" + config["Oppo_IP"] + ":436/playnormalfile?{%22path%22:%22/mnt/cifs1/" + urllib.parse.quote(filename) + "%22,%22index%22:"+ index +",%22type%22:1,%22appDeviceType%22:2,%22extraNetPath%22:%22"+ server + "%22,%22playMode%22:0}"
    url1 = "http://" + config["Oppo_IP"] + ':436/playnormalfile?'
    url = ''
    url = url + '"index":"' + index + '",'
    url = url + '"type":1,'
    url = url + '"appDeviceType":2,'
    url = url + '"extraNetPath":"'+ server + '",'
    url = url + '"playMode":0}'
    headers = {}
    url = url1 + url
    logging.debug(url0)
    try:
        response = requests.get(url0, headers=headers,timeout=config["timeout_oppo_playitem"])
    except:
        error = '{"success":false,"retInfo":"Timeout in Play Request"}'
        return error
    if config["DebugLevel"]==2:
        print("*** Fin playnormalfile ***")
        print(response.text)
    logging.debug("*** Playnormalfile Response: %s",response.text)
    return response.text

def checkfolderhasbdmv(config,folder,nfs):
    if config["DebugLevel"]==2:
        print("*** checkfolderhasbdmv ***")
    logging.debug("*** checkfolderhasbdmv ***")
    if nfs:
        url = "http://" + config["Oppo_IP"] + ':436/checkfolderhasBDMV?{"folderpath":"/mnt/nfs1/' + urllib.parse.quote(folder) + '"}'
    else:
        url = "http://" + config["Oppo_IP"] + ':436/checkfolderhasBDMV?{"folderpath":"/mnt/cifs1/' + urllib.parse.quote(folder) + '"}'
    headers = {}
    logging.debug(url)
    try:
        response = requests.get(url, headers=headers,timeout=config["timeout_oppo_playitem"])
    except:
        error = '{"success":false,"retInfo":"Timeout in Play Request"}'
        return error   
    if config["DebugLevel"]==2:
        print("*** Fin checkfolderhasbdmv ***")
    logging.debug("*** Checkfolderhasbdmv Response: %s",response.text)
    return response.text

def convert(s):
    try:
        return s.group(0).encode('ISO-8859-1').decode('utf8')
    except:
        return s.group(0)

def getfilelist(config,folder,nfs):
    if config["DebugLevel"]==2:
        print("*** getfilelist ***")
    logging.debug("*** getfilelist ***")
    if nfs==True:
        url = "http://" + config["Oppo_IP"] + ':436/getfilelist?{"path":"/mnt/nfs1' + urllib.parse.quote(folder) +'","fileType":1,"mediaType":3,"flag":1}'
    else:
        url = "http://" + config["Oppo_IP"] + ':436/getfilelist?{"path":"/mnt/cifs1' + urllib.parse.quote(folder) +'","fileType":1,"mediaType":3,"flag":1}'
    headers = {}
    logging.debug(url)
    response = requests.get(url, headers=headers)
    test=response.content
    b = test.rsplit(b'\x01')
    files=[]
    file={}
    file["Id"]=0
    file["Foldername"]='..'
    files.append(file)
    indice=1
    for c in b:
        if c.find(b'\x02')==-1:
            index=0
            ult=0
            d=c
            while index!=-1:
                index=c.find(b'\x00',index)
                if index==-1:
                    d=d[ult:]
                else:
                    ult=index+1
                    index=index+1
            e=d.decode('utf-8')
            if e!='':
                file={}
                file["Id"]=indice
                file["Foldername"]=e
                #if config["DebugLevel"]>0: print (e)
                indice=indice+1
                files.append(file)
    if config["DebugLevel"]==2:
       print("*** Fin getfilelist ***")
    logging.debug("*** getfilelist Response: %s",response.text)
    return files

def getNfsShareFolderlist(config):
    if config["DebugLevel"]==2:
        print("*** getNfsShareFolderlist ***")
    logging.debug("*** getNfsShareFolderlist ***")
    url = "http://" + config["Oppo_IP"] + ':436/getNfsShareFolderlist'
    headers = {}
    logging.debug(url)
    response = requests.get(url, headers=headers)
    test=response.content
    b = test.rsplit(b'\x01')
    files=[]
    file={}
    file["Id"]=0
    file["Foldername"]='..'
    files.append(file)
    indice=1
    for c in b:
        if c.find(b'\x02')==-1:
            index=0
            ult=0
            d=c
            while index!=-1:
                index=c.find(b'\x00',index)
                if index==-1:
                    d=d[ult:]
                else:
                    ult=index+1
                    index=index+1
            e=d.decode('utf-8')
            if e!='':
                file={}
                file["Id"]=indice
                file["Foldername"]=e
                #if config["DebugLevel"]>0: print (e)
                indice=indice+1
                files.append(file)
    if config["DebugLevel"]==2:
        print("*** Fin getNfsShareFolderlist ***")
    logging.debug("*** getNfsShareFolderlist Response: %s",response.text)
    return files

def getSambaShareFolderlist(config):
    if config["DebugLevel"]==2:
        print("*** getSambaShareFolderlist ***")
    logging.debug("*** getSambaShareFolderlist ***")
    url = "http://" + config["Oppo_IP"] + ':436/getSambaShareFolderlist'
    headers = {}
    logging.debug(url)
    response = requests.get(url, headers=headers)
    test=response.content
    b = test.rsplit(b'\x01')
    files=[]
    file={}
    file["Id"]=0
    file["Foldername"]='..'
    files.append(file)
    indice=1
    for c in b:
        if c.find(b'\x02')==-1:
            index=0
            ult=0
            d=c
            while index!=-1:
                index=c.find(b'\x00',index)
                if index==-1:
                    d=d[ult:]
                else:
                    ult=index+1
                    index=index+1
            e=d.decode('utf-8')
            if e!='':
                file={}
                file["Id"]=indice
                file["Foldername"]=e
                #if config["DebugLevel"]>0: print (e)
                indice=indice+1
                files.append(file)
    if config["DebugLevel"]==2:
        print("*** Fin getSambaShareFolderlist ***")
    logging.debug("*** getSambaShareFolderlist Response: %s",response.text)
    return files

def navigate_folder(path,config):
    path = path.replace('\\\\','\\')
    path = path.replace('\\','/')
    path = path.replace('//','/')
    devices = getdevicelist(config)
    device_list=json.loads(devices)
    nfs=config["default_nfs"]
    if path=='/':
        files=[]
        indice=1
        for device in device_list["devicelist"]:
            file={}
            file["Id"]=indice
            file["Foldername"]=device["name"]
            files.append(file)
        return(files)
    else:
        word = '/'
        inicio = path.find(word)
        inicio = inicio +1 
        final = path.find(word,inicio,len(path))
        print(final)
        if final < 0:
             servidor = path[1:len(path)]
             print(path)
             print(servidor)
             for device in device_list["devicelist"]:
                if device["name"].upper()==servidor.upper():
                    if device["sub_type"]=="nfs":
                        nfs=True
                        break
                    else:
                        nfs=False
                        break
             if nfs == True:
                response_login = LoginNFS(config,servidor)
                response=json.loads(response_login)
                if response["success"]==True:
                   files=getNfsShareFolderlist(config)
                else:
                   files=[]
                   file={}
                   file["Id"]=0
                   file["Foldername"]='..'
                   files.append(file)
                   file={}
                   file["Id"]=1
                   file["Foldername"]='LOGIN FAILED:' + response["retInfo"]
                   files.append(file)
                   return(files)
             else:
                response_login = LoginSambaWithOutID(config,servidor)
                response=json.loads(response_login)
                if response["success"]==True:
                   files=getSambaShareFolderlist(config)
                else:
                   files=[]
                   file={}
                   file["Id"]=0
                   file["Foldername"]='..'
                   files.append(file)
                   file={}
                   file["Id"]=1
                   file["Foldername"]='LOGIN FAILED:' + response["retInfo"]
                   files.append(file)
                   return(files)
             return(files)
        else:
            servidor = path[inicio:final]
            final=final+1
            result=path.find(word,final,len(path))
            carpeta = path[final:len(path)]
            last_folder='/'
            #if result <0:
            #    carpeta = path[final:len(path)]
            #    last_folder='/'
            #else:
            #    carpeta=path[final:result]
            #    result=result+1
            #    last_folder=path[result:len(path)]
            for device in device_list["devicelist"]:
                if device["name"].upper()==servidor.upper():
                    if device["sub_type"]=="nfs":
                        nfs=True
                        break
                    else:
                        nfs=False
                        break
            if nfs == True:
                response_login = LoginNFS(config,servidor)
                response=json.loads(response_login)
                if response["success"]==True:
                   response_data7 = mountSharedNFSFolder(servidor,carpeta,'','',config)
                   response=json.loads(response_login)
                else:
                   files=[]
                   file={}
                   file["Id"]=0
                   file["Foldername"]='..'
                   files.append(file)
                   file={}
                   file["Id"]=1
                   file["Foldername"]='LOGIN FAILED:' + response["retInfo"]
                   files.append(file)
                   return(files)
            else:
                response_login = LoginSambaWithOutID(config,servidor)
                response=json.loads(response_login)
                if response["success"]==True:
                   response_data7 = mountSharedFolder(servidor,carpeta,'','',config)
                else:
                   files=[]
                   file={}
                   file["Id"]=0
                   file["Foldername"]='..'
                   files.append(file)
                   file={}
                   file["Id"]=1
                   file["Foldername"]='LOGIN FAILED:' + response["retInfo"]
                   files.append(file)
                   return(files)
            response_mount=json.loads(response_data7)
            if response_mount["success"]==True:
                files = getfilelist(config,last_folder,nfs)
                return(files)
            else:
                files=[]
                file={}
                file["Id"]=0
                file["Foldername"]='..'
                files.append(file)
                file={}
                file["Id"]=1
                file["Foldername"]='MOUNT FAILED:' + response_mount["retInfo"]
                files.append(file)
                return(files)
            
def setplaytime(config,playticks):
    logging.debug("setplaytime")
    secs_total=playticks/10000000
    h=secs_total//3600
    m=(secs_total%3600)//60
    s=((secs_total%3600)%60)
    url1 = "http://" + config["Oppo_IP"] + ':436/setplaytime?'
    url = ''
    url = url + '{"h":'+ str(int(h)) + ','
    url = url + '"m":' + str(int(m)) + ','
    url = url + '"s":' + str(int(s)) + '}'
    headers = {}
    url = url1 + url
    logging.debug(url)
    response = requests.get(url, headers=headers)
    logging.debug("*** setplaytime Response: %s",response.text)
    return response.text

def smbtrick(path,config):
    path = path.replace('\\\\','\\')
    path = path.replace('\\','/')
    path = path.replace('//','/')
    devices = getdevicelist(config)
    device_list=json.loads(devices)
    word = '/'
    inicio = path.find(word)
    inicio = inicio +1 
    final = path.find(word,inicio,len(path))
    servidor = path[inicio:final]
    final=final+1
    result=path.find(word,final,len(path))
    carpeta = path[final:result]
    response_login = LoginSambaWithOutID(config,servidor)
    response=json.loads(response_login)
    if response["success"]==True:
        files=getSambaShareFolderlist(config)
        for file in files:
           if file["Foldername"]!='..':
            if file["Foldername"].upper()!=carpeta.upper():
                response_data7 = mountSharedFolder(servidor,file["Foldername"],'','',config,False)
                if config["DebugLevel"]>0:
                    print(servidor  + "-" + file["Foldername"])
                return(0)
    else:        
        devices = getdevicelist(config)
        device_list=json.loads(devices)
        for device in device_list["devicelist"]:
            if device["name"].upper()!=servidor.upper():
                if device["sub_type"]=="cifs":
                    response_login = LoginSambaWithOutID(config,device["name"])
                    files=getSambaShareFolderlist(config)
                    for file in files:
                        if file["Foldername"]!='..':
                            response_data7 = mountSharedFolder(device["name"],file["Foldername"],'','',config,False)
                            return(0)

def setaudiotrack(config,audio_index):
    logging.debug("setaudiotrack")
    url = "http://" + config["Oppo_IP"] + ':436/setaudiomenulist?{"cur_index":'+ str(int(audio_index)) + '}'
    headers = {}
    logging.debug(url)
    response = requests.get(url, headers=headers)
    logging.debug("*** setaudiotrack Response: %s",response.text)
    return response.text

def LoginSambaWithOutID(config,server):
    logging.debug("LoginSambaWithOutID")
    url = "http://" + config["Oppo_IP"] + ':436/loginSambaWithOutID?{"serverName":"'+ str(server) + '"}'
    headers = {}
    logging.debug(url)
    response = requests.get(url, headers=headers)
    if config["DebugLevel"]==2:
        print("*** LoginSambaWithOutID Response: " + response.text)
    logging.debug("*** LoginSambaWithOutID Response: %s",response.text)
    return response.text

def getaudiotrack(config):
    logging.debug("getaudiotrack")
    url = "http://" + config["Oppo_IP"] + ':436/getaudiomenulist?'
    headers = {}
    logging.debug(url)
    response = requests.get(url, headers=headers)
    logging.debug("*** getaudiotrack Response: %s",response.text)
    for audio in response["audio_list"]:
        if audio["selected"]==True:
                 return(audio["index"])
    return(0)

def getmaxaudiotrack(config):
    logging.debug("getaudiotrack")
    url = "http://" + config["Oppo_IP"] + ':436/getaudiomenulist?'
    headers = {}
    logging.debug(url)
    response = requests.get(url, headers=headers)
    logging.debug("*** getaudiotrack Response: %s",response.text)
    index=0
    if config["DebugLevel"]>0: print(response.text)
    audio_list=json.loads(response.text)
    for audio in audio_list["audio_list"]:
        index=index+1
    return(index)

def setsubstrack(config,subs_index):
    logging.debug("setsubstrack")
    if config["DebugLevel"]>0: print(subs_index)
    actual_track = getsubstrack(config)
    if config["DebugLevel"]>0: print(actual_track)
    url = "http://" + config["Oppo_IP"] + ':436/setsubttmenulist?{"cur_index":'+ str(int(subs_index)) + '}'
    headers = {}
    logging.debug(url)
    timeout=0
    while actual_track!=subs_index or timeout==10:
        response = requests.get(url, headers=headers)
        logging.debug("*** setaudiotrack Response: %s",response.text)
        if config["DebugLevel"]>0: print(response.text)
        time.sleep(1)
        actual_track = getsubstrack(config)
        timeout=timeout+1
    return (0)

def getsubstrack(config):
    logging.debug("getsubstrack")
    url = "http://" + config["Oppo_IP"] + ':436/getsubtitlemenulist?'
    headers = {}
    logging.debug(url)
    response = requests.get(url, headers=headers)
    logging.debug("*** getsubtitlemenulist Response: %s",response.text)
    response_subs=json.loads(response.text)
    try:
        for subs in response_subs["subtitle_list"]:
            if subs["selected"]==True:
                     return(subs["index"])
    except:
        return(0)

def sendremotekey(key,config):
    #if config["DebugLevel"]>0: print("sendremotekey\n")
    url = "http://" + config["Oppo_IP"] + ":436/sendremotekey?%7B%22key%22%3A%22" + key + "%22%7D"
    headers = {}
    #if config["DebugLevel"]>0: print (url)
    response = requests.get(url, headers=headers)
    #if config["DebugLevel"]>0: print (response.text)
    return response.text

def playcdfile(server,filename,index):
    print("playcdfile\n")
    url = "http://" + config["Oppo_IP"] + ":436/playcdfile?{%22path%22:%22/mnt/cifs1/" + filename + "%22,%22index%22:"+ index +",%22type%22:1,%22appDeviceType%22:2,%22extraNetPath%22:%22"+ server + "%22,%22playMode%22:0}"
    headers = {}
    print (url)
    response = requests.get(url, headers=headers)
    print (response.text)
    return response.text

def playother(EmbySession,data,scripterx=False):
    if EmbySession.config["DebugLevel"]>0: print("Inicio Replay")
    logging.info("Con el OPPO iniciado le decimos que cambie de pelicula")
    EmbySession.playstate="Replay"
    params = EmbySession.process_data(data)
    ItemInfo = EmbySession.get_item_info2(EmbySession.user_info["User"]["Id"],params["item_id"],params["media_source_id"])
    FilePath = ItemInfo["Path"]
    logging.info("-----------------------------------------------------------")
    if scripterx:
            if EmbySession.config["DebugLevel"]>0: print("Iniciando en el OPPO - X")
            response_data4 = EmbySession.send_message2(params["Session_id"], EmbySession.lang["x_msg_init_oppo"])
    else:
            if EmbySession.config["DebugLevel"]>0: print("Iniciando en el OPPO")
            response_data4 = EmbySession.send_user_message(params["ControllingUserId"], EmbySession.lang["x_msg_init_oppo"])
    file_mockup = FilePath[:len(FilePath)-3] + 'txt'
    logging.debug('File_mockup: %s',file_mockup)
    if os.path.isfile(file_mockup):
            f3 = open(file_mockup,'r')
            for line in f3:
                newitem=line
            f3.close
            if EmbySession.config["DebugLevel"]>0: print ('File_encontrado - contenido: ' + line)
            logging.debug('File_encontrado - contenido: %s',line)
            ItemInfo = EmbySession.get_item_info2(EmbySession.user_info["User"]["Id"],params["item_id"],params["media_source_id"])
            movie = ItemInfo["Path"]
            Container = ItemInfo["Container"]
    else:
            if scripterx:
                if EmbySession.config["DebugLevel"]>0: print("Paramos reproduccion en el dispositivo")
                response_data2 = EmbySession.playback_stop(params["Session_id"])
            movie = ItemInfo["Path"]
            Container = ItemInfo["Container"]
    logging.info('Ruta antes de los reemplazos por server: %s', movie)
    server_list=EmbySession.config["servers"]
    for server in server_list:
            server_data = {}
            server_data["name"] = server["name"]
            server_data["Emby_Path"] = server["Emby_Path"]
            server_data["Oppo_Path"] = server["Oppo_Path"]
            logging.info("Sustituimos " + server_data["Emby_Path"] + " por " + server_data["Oppo_Path"])
            movie = movie.replace(server_data["Emby_Path"],server_data["Oppo_Path"])
            logging.info("Resultado : %s",movie)
    logging.info('Ruta antes de los reemplazos de path: %s', movie)
    movie = movie.replace('\\\\','\\')
    movie = movie.replace('\\','/')
    logging.info('Ruta despues: %s',movie)
    logging.info("-----------------------------------------------------------")
    word = '/'
    inicio = movie.find(word)
    inicio = inicio +1 
    final = movie.find(word,inicio,len(movie))
    servidor = movie[inicio:final]
    logging.info("Servidor               : %s", servidor)
    ultimo=final+1
    result=final+1
    while result > 0:
            ultimo=result+1
            result=movie.find(word,ultimo,len(movie))
    fichero=movie[ultimo:len(movie)]
    logging.info("Fichero                : %s", fichero)   
    final=final+1
    ultimo=ultimo-1
    carpeta=movie[final:ultimo]
    logging.info("Carpeta                : %s",carpeta)
    logging.info("-----------------------------------------------------------")
    EmbySession.server = servidor
    EmbySession.folder = carpeta
    EmbySession.filename = fichero
    EmbySession.playedtitle = ItemInfo["Name"]
    response_data6f = getdevicelist(EmbySession.config)
    device_list=json.loads(response_data6f)
    if EmbySession.config["DebugLevel"]>0: print(device_list)
    nfs=EmbySession.config["default_nfs"]
    for device in device_list["devicelist"]:
            if device["name"].upper()==servidor.upper():
                if device["sub_type"]=="nfs":
                    nfs=True
                    break
                else:
                    nfs=False
                    break
    if nfs:
        response_login = LoginNFS(EmbySession.config,servidor)
        response_data7 = mountSharedNFSFolder(servidor,carpeta,'','',EmbySession.config)
    else:
        response_login = LoginSambaWithOutID(EmbySession.config,servidor)
        response_data7 = mountSharedFolder(servidor,carpeta,'','',EmbySession.config)
    response_mount=json.loads(response_data7)
    #if EmbySession.config["DebugLevel"]>0: print(response)
    if Container=='bluray':
            response_data8 = checkfolderhasbdmv(EmbySession.config,fichero,nfs)
    else:
            response_data8 = playnormalfile(servidor,fichero,'0',EmbySession.config,nfs)
    response_play=json.loads(response_data8)
    timer=0
    timeout=EmbySession.config["timeout_oppo_playitem"]
    response_data_gb = getglobalinfo(EmbySession.config)
    while response_data_gb.find('"is_video_playing":false') > 0 and timer<timeout:
                time.sleep(2)
                response_data_gb = getglobalinfo(EmbySession.config)
                timer=timer+1
                logging.debug('getglobalinfo: %s',response_data_gb)
    if timer>=timeout:
       if scripterx:
          response_data9 = EmbySession.send_message2(params["Session_id"], EmbySession.lang["x_msg_timeout_play"])
       else:
          response_data9 = EmbySession.send_user_message(params["ControllingUserId"], EmbySession.lang["x_msg_timeout_play"])
          logging.info('Timeout Reproduciendo %s',movie)
       EmbySession.playstate="Playing"
    else:
        if params["auto_resume"]<=0:
            setplaytime(EmbySession.config,0)
        else:
            playticks=params["auto_resume"]
            setplaytime(EmbySession.config,playticks)
        try:
            if params["audio_stream_index"]:
                 audio_index = EmbySession.get_xnoppo_audio_index(params["ControllingUserId"],params["item_id"],params["audio_stream_index"])
                 setaudiotrack(EmbySession.config,audio_index)
        except:
                 pass
        try:
          if EmbySession.config["DebugLevel"]>0: print('llamamos a setsubstrack')    
          if EmbySession.config["DebugLevel"]>0: print(params["subtitle_stream_index"])
          subs_index = EmbySession.get_xnoppo_subs_index(params["ControllingUserId"],params["item_id"],params["subtitle_stream_index"])
          setsubstrack(EmbySession.config,subs_index)
        except:
          if EmbySession.config["DebugLevel"]>0: print('Error indicando el subtitulo')  
        EmbySession.playnow(data)
        EmbySession.currentdata=data
        EmbySession.playstate="Playing"
        if EmbySession.config["DebugLevel"]>0: print("Fin Replay")
    
def playto_file(EmbySession,data,scripterx=False):
    EmbySession.playstate="Loading"
    EmbySession.currentdata=data
    if EmbySession.config["DebugLevel"]>0: print("scripterx is " + str(scripterx))
    sendnotifyremote(EmbySession.config["Oppo_IP"])
    params = EmbySession.process_data(data)
    ItemInfo = EmbySession.get_item_info2(EmbySession.user_info["User"]["Id"],params["item_id"],params["media_source_id"])
    FilePath = ItemInfo["Path"]
    if scripterx:
       if EmbySession.config["DebugLevel"]>0: print("Paramos reproduccion en el dispositivo")
       response_data2 = EmbySession.playback_stop(params["Session_id"])
    movie = ""
    if scripterx:
        result=check_socket(EmbySession.config,params["Session_id"])
    else:
        result=check_socket(EmbySession.config)
    if result==0:
        if scripterx:
            if EmbySession.config["DebugLevel"]>0: print("Iniciando en el OPPO - X")
            response_data4 = EmbySession.send_message2(params["Session_id"], EmbySession.lang["x_msg_init_oppo"])
        else:
            if EmbySession.config["DebugLevel"]>0: print("Iniciando en el OPPO")
            response_data4 = EmbySession.send_user_message(params["ControllingUserId"], EmbySession.lang["x_msg_init_oppo"])
        response_data6a = getmainfirmwareversion(EmbySession.config)
        response_data6c = getdevicelist(EmbySession.config)
        response_data6b = getsetupmenu(EmbySession.config)
        response_data6c = OppoSignin(EmbySession.config)
        response_data6d = getdevicelist(EmbySession.config)
        response_data6e = getglobalinfo(EmbySession.config)
        response_data6f = getdevicelist(EmbySession.config)
        response_data_on = sendremotekey("EJT",EmbySession.config)
        if EmbySession.config["BRDisc"]==True:
            time.sleep(1)
            response_data_on = sendremotekey("EJT",EmbySession.config)    
        if EmbySession.config["AV"]==True:
            if EmbySession.config["DebugLevel"]>0: print("AV POWER")
            logging.info ('Comprobamos que esta encendido el AV')
            try:
                result = av_check_power(EmbySession.config)
                if EmbySession.config["DebugLevel"]>0: print(result)
                logging.info ('Resultado: %s',str(result))
            except:
               pass
        time.sleep(1)
        response_data6b = getsetupmenu(EmbySession.config)
        file_mockup = FilePath[:len(FilePath)-3] + 'txt'
        logging.debug('File_mockup: %s',file_mockup)
        if os.path.isfile(file_mockup):
            f3 = open(file_mockup,'r')
            for line in f3:
                newitem=line
            f3.close
            if EmbySession.config["DebugLevel"]>0: print ('File_encontrado - contenido: ' + line)
            logging.debug('File_encontrado - contenido: %s',line)
            ItemInfo = EmbySession.get_item_info2(EmbySession.user_info["User"]["Id"],newitem,params["media_source_id"])
            movie = ItemInfo["Path"]
            Container = ItemInfo["Container"]
        else:
##            if scripterx:
##                if EmbySession.config["DebugLevel"]>0: print("Paramos reproduccion en el dispositivo")
##                response_data2 = EmbySession.playback_stop(params["Session_id"])
            movie = ItemInfo["Path"]
            Container = ItemInfo["Container"]
        logging.info("-----------------------------------------------------------")
        logging.info('Ruta antes de los reemplazos por server: %s', movie)
        server_list=EmbySession.config["servers"]
        for server in server_list:
            server_data = {}
            server_data["name"] = server["name"]
            server_data["Emby_Path"] = server["Emby_Path"]
            server_data["Oppo_Path"] = server["Oppo_Path"]
            logging.info("Sustituimos " + server_data["Emby_Path"] + " por " + server_data["Oppo_Path"])
            movie = movie.replace(server_data["Emby_Path"],server_data["Oppo_Path"])
            logging.info("Resultado : %s",movie)
        logging.info('Ruta antes de los reemplazos de path: %s', movie)
        movie = movie.replace('\\\\','\\')
        movie = movie.replace('\\','/')
        logging.info('Ruta despues: %s',movie)
        logging.info("-----------------------------------------------------------")
        word = '/'
        inicio = movie.find(word)
        inicio = inicio +1 
        final = movie.find(word,inicio,len(movie))
        servidor = movie[inicio:final]
        ultimo=final+1
        result=final+1
        while result > 0:
            ultimo=result+1
            result=movie.find(word,ultimo,len(movie))
        fichero=movie[ultimo:len(movie)]

        final=final+1
        ultimo=ultimo-1
        carpeta=movie[final:ultimo]
        # test
        #final = carpeta.find(word)
        #SharedFolder = carpeta[0:final]
        #carpeta=carpeta[final+1:len(carpeta)]
        #fichero=carpeta + word + fichero
        #carpeta = SharedFolder
        # /test
        logging.info("Servidor               : %s", servidor)
        logging.info("Fichero                : %s", fichero)   
        logging.info("Carpeta                : %s",carpeta)
        logging.info("-----------------------------------------------------------")
        EmbySession.server = servidor
        EmbySession.folder = carpeta
        EmbySession.filename = fichero
        EmbySession.playedtitle = ItemInfo["Name"]

        if EmbySession.config["wait_nfs"]==True:
            text = 'sub_type":"nfs'
        else:
            text = 'sub_type'
        while response_data6f.find(text) == 0:
              time.sleep(1)
              response_data6f = getdevicelist(EmbySession.config)
              response_data_on = sendremotekey("QPW",EmbySession.config)
              logging.debug('Query POWER ON: %s',response_data_on)
        device_list=json.loads(response_data6f)
        if EmbySession.config["DebugLevel"]>0: print(device_list)
        nfs=EmbySession.config["default_nfs"]
        for device in device_list["devicelist"]:
            if device["name"].upper()==servidor.upper():
                if device["sub_type"]=="nfs":
                    nfs=True
                    break
                else:
                    nfs=False
                    break
        if nfs:
            response_login = LoginNFS(EmbySession.config,servidor)
            response_share = getNfsShareFolderlist(EmbySession.config)
        else:
            response_login = LoginSambaWithOutID(EmbySession.config,servidor)
            response_share = getSambaShareFolderlist(EmbySession.config)
        # Test
        #for share in response_share:
        #    if EmbySession.config["DebugLevel"]>0: print(share["Foldername"])
        #    if carpeta.upper().startswith(share["Foldername"].upper()):
        #            sharefolder=share["Foldername"]
        #            i = len(sharefolder)
        #            nfolder = carpeta[i+1:len(carpeta)]
        #            fichero= nfolder + '/' + fichero
        #            carpeta = sharefolder
        #            if EmbySession.config["DebugLevel"]>0: print(carpeta)
        #            if EmbySession.config["DebugLevel"]>0: print(fichero)
        #            break
        if EmbySession.config["Always_ON"]==False:
            time.sleep(5)
        response_data6b = getsetupmenu(EmbySession.config)
        if scripterx:
            response_data9 = EmbySession.send_message2(params["Session_id"], EmbySession.lang["x_msg_wait_for_mount"] ,1999)
        else:
            response_data9 = EmbySession.send_user_message(params["ControllingUserId"], EmbySession.lang["x_msg_wait_for_mount"] ,1999)
        if nfs:
            response_data7 = mountSharedNFSFolder(servidor,carpeta,'','',EmbySession.config)
        else:
            response_data7 = mountSharedFolder(servidor,carpeta,'','',EmbySession.config)
        response_mount=json.loads(response_data7)
        #if EmbySession.config["DebugLevel"]>0: print(response)
        if response_mount["success"]==True:
            if Container=='bluray':
                response_data8 = checkfolderhasbdmv(EmbySession.config,fichero,nfs)
            else:
                response_data8 = playnormalfile(servidor,fichero,'0',EmbySession.config,nfs)
            response_play=json.loads(response_data8)
            if response_play["success"]==True:
                response_data_gb = getglobalinfo(EmbySession.config)
                timer=0
                timeout=EmbySession.config["timeout_oppo_playitem"]
                while response_data_gb.find('"is_video_playing":false') > 0 and timer<timeout:
                        time.sleep(1)
                        response_data_gb = getglobalinfo(EmbySession.config)
                        timer=timer+1
                        logging.debug('getglobalinfo: %s',response_data_gb)
                        if scripterx:
                            response_data9 = EmbySession.send_message2(params["Session_id"], EmbySession.lang["x_msg_wait_for_play"] + str(timer) + 's',999)
                        else:
                            response_data9 = EmbySession.send_user_message(params["ControllingUserId"], EmbySession.lang["x_msg_wait_for_play"] + str(timer) + 's',999)                
                logging.debug('getglobalinfo: %s',response_data_gb)
                if timer>=timeout:
                    if scripterx:
                        response_data9 = EmbySession.send_message2(params["Session_id"], EmbySession.lang["x_msg_timeout_play"])
                    else:
                        response_data9 = EmbySession.send_user_message(params["ControllingUserId"], EmbySession.lang["x_msg_timeout_play"])
                    logging.info('Timeout Reproduciendo %s',movie)
                else:
                    #if scripterx==False:
                    EmbySession.playstate="Playing"
                    EmbySession.playnow(data)
                    if EmbySession.config["DebugLevel"]>0: print(params["auto_resume"])
                    if params["auto_resume"]<=0:
                        setplaytime(EmbySession.config,0)
                        if EmbySession.config["DebugLevel"]>0: print('Se inicia desde el principio el video')
                    else:
                        playticks=params["auto_resume"]
                        setplaytime(EmbySession.config,playticks)
                        if EmbySession.config["DebugLevel"]>0: print('Se restablece la reproduccion en ' + str(playticks))
                    try:
                        if params["audio_stream_index"]:
                            audio_index = EmbySession.get_xnoppo_audio_index(params["ControllingUserId"],params["item_id"],params["audio_stream_index"])
                            setaudiotrack(EmbySession.config,audio_index)
                    except:
                        pass
                    if EmbySession.config["TV"]==True:
                        logging.info ('Cambiamos HDMI de la TV')
                        try:
                            result = tv_change_hdmi(EmbySession.config)
                            if EmbySession.config["DebugLevel"]>0: print(result)
                            logging.info ('Resultado: %s',str(result))
                        except:
                            pass
                        if scripterx:
                            response_data5 = EmbySession.playback_stop(params["Session_id"])
                            if EmbySession.config["DebugLevel"]>0: print (response_data5)
                    else:
                        if scripterx==True:
                            response_data9 = EmbySession.send_message2(params["Session_id"], EmbySession.lang["x_msg_init_play"] + movie)
                        #else:
                        #    response_data9 = EmbySession.send_user_message(params["ControllingUserId"], 'Reproduccion Iniciada: ' + movie)
                        logging.info('Reprodución iniciada: %s',movie)
                    if EmbySession.config["AV"]==True:
                        if EmbySession.config["DebugLevel"]>0: print("AV")
                        logging.info ('Cambiamos HDMI del AV')
                        try:
                            time.sleep(EmbySession.config["av_delay_hdmi"])
                            result = av_change_hdmi(EmbySession.config)
                            if EmbySession.config["DebugLevel"]>0: print(result)
                            logging.info ('Resultado: %s',str(result))
                        except:
                            pass
                    response_data_gb = getglobalinfo(EmbySession.config)
                    cur_time=0
                    total_time=0
                    playingtime={}
                    playingtime["total_time"]=total_time
                    playingtime["cur_time"]=cur_time
                    positionticks=0
                    totalticks=0
                    ispaused=False
                    ismuted=False
                    try:
                        if EmbySession.config["DebugLevel"]>0: print('llamamos a setsubstrack')    
                        if EmbySession.config["DebugLevel"]>0: print(params["subtitle_stream_index"])
                        subs_index = EmbySession.get_xnoppo_subs_index(params["ControllingUserId"],params["item_id"],params["subtitle_stream_index"])
                        setsubstrack(EmbySession.config,subs_index)
                    except:
                        if EmbySession.config["DebugLevel"]>0: print('Error indicando el subtitulo')  
                    while response_data_gb.find('"is_video_playing":true') > 0:
                          time.sleep(1)
                          if EmbySession.playstate!='Replay':
                              response_data_gb = getglobalinfo(EmbySession.config)
                              if response_data_gb.find('"is_video_playing":true') > 0:
                                  response_playing_time = getplayingtime(EmbySession.config)
                                  playingtime = json.loads(response_playing_time)
                          if response_data_gb.find('"is_video_playing":true') > 0:
                              if EmbySession.config["DebugLevel"]>0: print('PlayingTime: ' + str(playingtime["cur_time"]) + ' de ' + str(playingtime["total_time"]))
                              logging.debug('PlayingTime: %s de %s',str(playingtime["cur_time"]),str(playingtime["total_time"]))
                              if playingtime["cur_time"]>0 and playingtime["total_time"]>0:
                                  positionticks=playingtime["cur_time"]*10000000
                                  total_time=playingtime["total_time"]
                                  totalticks=total_time*10000000
                              if scripterx==False:
                              #if EmbySession.config["DebugLevel"]>0: print(EmbySession.currentdata['ItemIds'])
                                  EmbySession.playingprogress(EmbySession.currentdata,positionticks,totalticks,ispaused,ismuted)
                                  EmbySession.setitemplaybackposition(EmbySession.currentdata,positionticks,False)
                    logging.info("-----------------------------------------------------------")
                    logging.debug('getglobalinfo: %s',response_data_gb)
                    logging.debug('PlayingTime: %s de %s',str(playingtime["cur_time"]),str(total_time))
                    if EmbySession.config["DebugLevel"]>0: print('PlayingTime Final: ' + str(playingtime["cur_time"]) + " de " + str(total_time))
                    #positionticks=playingtime["cur_time"]*10000000
                    #if scripterx==False:
                    #if EmbySession.config["DebugLevel"]>0: print(EmbySession.currentdata['ItemIds'])
                    EmbySession.playingstopped(EmbySession.currentdata,positionticks,ispaused,ismuted)
                    played=False
                    if total_time>0:
                        if (positionticks/total_time)>0.95:
                            played=True
                    #if EmbySession.config["DebugLevel"]>0: print(EmbySession.currentdata['ItemIds'])
                    EmbySession.setitemplaybackposition(EmbySession.currentdata,positionticks,played)
                    #params["DeviceName"]=EmbySession.config["TV_DeviceName"]
                    if EmbySession.config["TV"]==True:
                        if EmbySession.config["DebugLevel"]>0: print("Cambiamos a la app anterior en la TV")
                        logging.info ("Cambiamos a la app anterior en la TV")
                        try:
                            result = tv_set_prev(EmbySession.config)
                            if EmbySession.config["DebugLevel"]>0: print(result)
                            logging.info ('Resultado: %s',str(result))
                        except:
                            pass
            else:
                try:
                   error = response_play["msg"]
                except:
                   error='No hay mas info'
                if scripterx:
                   response_data9 = EmbySession.send_message2(params["Session_id"],EmbySession.lang["x_msg_error_play"] + fichero + '- info:' + error,5000)
                else:
                   response_data9 = EmbySession.send_user_message(params["ControllingUserId"], EmbySession.lang["x_msg_error_play"] + fichero + ' - info:' + error,5000)
                #   response_data3 = set_movie(item_data["Id"],sys.argv[3],sys.argv[4],sys.argv[5])                    
        else:
           try:
               error = response_mount["retInfo"]
           except:
               error='No hay mas info'
           if scripterx:
               l=len(servidor + '/' + carpeta)
               response_data9 = EmbySession.send_message2(params["Session_id"],EmbySession.lang["x_msg_error_mount"] + servidor + '/' + carpeta + ' - info:' + error + ' long:' + l,5000)
           else:
               l=len(servidor + '/' + carpeta)
               response_data9 = EmbySession.send_user_message(params["ControllingUserId"], EmbySession.lang["x_msg_error_mount"]  + servidor + '/' + carpeta + ' - info:' + error + ' long:' + l,5000)
        if EmbySession.config["Autoscript"]==True:
            result=umountSharedFolder(EmbySession.config)
            if EmbySession.config["DebugLevel"]>0: print("Unmount result: " + result)
        if EmbySession.config["AV"]==True and EmbySession.config["AV_Always_ON"]==False:
            if EmbySession.config["DebugLevel"]>0: print ("AV POWER OFF")
            result = av_power_off(EmbySession.config)
        if EmbySession.config["Always_ON"]==False:
            response_data_off = sendremotekey("POF",EmbySession.config)
    else:
        if scripterx==True:
            response_timeout = EmbySession.send_message2(params["Session_id"], EmbySession.lang["x_msg_error_no_oppo"] )
        else:
            response_timeout = EmbySession.send_user_message(params["ControllingUserId"], EmbySession.lang["x_msg_error_no_oppo"])
    if scripterx==True:
        response_data3 = EmbySession.set_movie(params["Session_id"],params["item_id"],ItemInfo["Type"],ItemInfo["Name"])
    EmbySession.playstate="Free"
    EmbySession.server = ""
    EmbySession.playedtitle = ""
    EmbySession.folder = ""
    EmbySession.filename = ""
    logging.info("Fin Playto_File %s",movie)

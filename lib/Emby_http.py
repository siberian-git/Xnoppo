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
import threading
import logging

class EmbyHttp(threading.Thread):
    config=None
    user_info=None
    playstate="Free"
    playedtitle=None
    PlaySessionId=''
    server=None
    folder=None
    filename=None
    currentdata=None
    lang=None
    def __init__(self,config):
        self.config=config
        threading.Thread.__init__(self)
        self.user_info = self.authenticate()
        logging.info('EmbyHttp Iniciado')

    def authenticate(self):

        url = self.config.get("emby_server") + "/Users/AuthenticateByName?format=json"
        pwd_pre = self.config.get("user_password", "").encode('utf-8')
        pwd_sha = hashlib.sha1(pwd_pre).hexdigest()

        user_name = quote(self.config.get("user_name", ""))
        pwd_text = quote(self.config.get("user_password", ""))

        message_data = {}
        message_data["username"] = user_name
        message_data["password"] = pwd_sha
#        message_data["pw"] = pwd_text
        message_data["pw"] = pwd_pre

        headers = self.get_headers()

#        print ("Auth Url     : %s" % url)
#        print ("Auth Msg     : %s" % message_data)
#        print ("Auth Headers : %s" % headers)
        response = requests.post(url, data=message_data, headers=headers)
#        print(response.text)
        return response.json()

    def process_data(self,data):
        startat = data.get('StartPositionTicks', -1)
        item_ids = data['ItemIds']
        media_source_id = data.get("MediaSourceId", "")
        subtitle_stream_index = data.get("SubtitleStreamIndex", -1)
        audio_stream_index = data.get("AudioStreamIndex", 1)
        start_index = data.get("StartIndex", 0)
        params = {}
        if self.config["DebugLevel"]>0: print(len(item_ids))
        if len(item_ids) > 0:
             item_ids = item_ids[0]
        if start_index > 0 and start_index < len(item_ids):
            item_ids = item_ids[start_index:]
        #if len(item_ids) == 1:
        #     item_ids = item_ids[0]
        if startat <0:
            iteminfo=self.get_item_info(data.get("ControllingUserId",""),item_ids)
            #print(iteminfo)
            startat = iteminfo["UserData"]["PlaybackPositionTicks"]                            
        params = {}
        params["item_id"] = item_ids
        params["auto_resume"] = startat
        params["media_source_id"] = media_source_id
        params["subtitle_stream_index"] = subtitle_stream_index
        params["audio_stream_index"] = audio_stream_index
        params["ControllingUserId"]= data.get("ControllingUserId", "")
        params["Session_id"] = data.get("SessionID", None)
        params["DeviceName"] = data.get("DeviceName", "")
        params["Device_Id"] = data.get("Device_Id", "")
        

        if self.config["DebugLevel"]>0:  print(params)
        return(params)

    def playnow(self,data):

        url = self.config.get("emby_server") + '/emby/Sessions/Playing/?format=json'
        params = self.process_data(data)

        url2 = self.config.get("emby_server") + '/Items/' + str(params["item_id"]) + '/PlaybackInfo?format=json'
        response_data2 = self.get_ulr_data(url2, self.config,self.user_info)
        item_list2 = json.loads(response_data2)
        print(item_list2)
        self.PlaySessionId = item_list2["PlaySessionId"]

        session_info = self.user_info["SessionInfo"]
        message_data = {
                      "CanSeek": True,
                      "ItemId": params["item_id"],
                      "SessionId": session_info["Id"],
                      "MediaSourceId": params["media_source_id"],
                      "AudioStreamIndex": params["audio_stream_index"],
                      "SubtitleStreamIndex": params["subtitle_stream_index"],
                      "IsPaused": False,
                      "IsMuted": False,
                      "PositionTicks": 0,
                      "PlayMethod": "DirectPlay",
                      "PlaySessionId" : self.PlaySessionId,
                      "RepeatMode": "RepeatNone"
                        }
        headers = self.get_headers(self.user_info)
    
        response = requests.post(url, data=message_data, headers=headers)
        if self.config["DebugLevel"]>0: print (response.text)

        return response

    def playingprogress(self,data,positionticks,totalticks,ispaused,ismuted):

        url = self.config.get("emby_server") + '/emby/Sessions/Playing/Progress?format=json'
        params = self.process_data(data)
        session_info = self.user_info["SessionInfo"]
        message_data = {
                      "CanSeek": True,
                      "ItemId": params["item_id"],
                      "SessionId": session_info["Id"],
                      "MediaSourceId": params["media_source_id"],
                      "AudioStreamIndex": params["audio_stream_index"],
                      "SubtitleStreamIndex": params["subtitle_stream_index"],
                      "IsPaused": ispaused,
                      "IsMuted": ismuted,
                      "PositionTicks": positionticks,
                      "RunTimeTicks": totalticks,
                      "PlayMethod": "DirectPlay",
                      "PlaySessionId" : self.PlaySessionId,
                      "RepeatMode": "RepeatNone",
                      "EventName": "timeupdate"
                        }
        headers = self.get_headers(self.user_info)
    
        response = requests.post(url, data=message_data, headers=headers)
        if self.config["DebugLevel"]>0: print (response.text)

        return response

    def playingstopped(self,data,positionticks,ispaused,ismuted):

        url = self.config.get("emby_server") + '/emby/Sessions/Playing/Stopped?format=json'
        params = self.process_data(data)
        session_info = self.user_info["SessionInfo"]
        message_data = {
                      "CanSeek": True,
                      "ItemId": params["item_id"],
                      "SessionId": session_info["Id"],
                      "MediaSourceId": params["media_source_id"],
                      "AudioStreamIndex": params["audio_stream_index"],
                      "SubtitleStreamIndex": params["subtitle_stream_index"],
                      "IsPaused": ispaused,
                      "IsMuted": ismuted,
                      "PositionTicks": positionticks,
                      "PlayMethod": "DirectPlay",
                      "PlaySessionId" : self.PlaySessionId,
                      "RepeatMode": "RepeatNone",
                      "EventName": "timeupdate"
                        }
        headers = self.get_headers(self.user_info)
    
        response = requests.post(url, data=message_data, headers=headers)
        if self.config["DebugLevel"]>0: print (response.text)

        return response
    
    def setitemplaybackposition(self,data,positionticks,played):

        params = self.process_data(data)
        url = self.config.get("emby_server") + '/Users/' + str(self.user_info["User"]["Id"]) + '/Items/' + str(params["item_id"]) +'/UserData?format=json'
        
        message_data = {
                    "played" : played,
                    "PlaybackPositionTicks" : positionticks
                        }
        headers = self.get_headers(self.user_info)
        logging.debug ('setitemplaybackposition data: %s',message_data)
        response = requests.post(url, data=message_data, headers=headers)
        logging.debug ('setitemplaybackposition respuesta: %s',response.text)

        return response

        user_info["User"]["Id"]

    def playback_stop(self,session_id):

        url = self.config.get("emby_server") + '/emby/Sessions/' + str(session_id) + "/Playing/Stop?format=json"
        print(url)
        message_data = {}
        message_data["Command"] = 'Stop'
        message_data["SeekPositionTicks"] = 0
        message_data["ControllingUserId"] = 'string'
    
        headers = self.get_headers(self.user_info)
    
        response = requests.post(url, data=message_data, headers=headers)
        if self.config["DebugLevel"]>0: print (response.text)

        return response


    def get_headers(self,user_info=None):

        auth_string = "MediaBrowser Client=\"Emby Xnoppo\",Device=\"Xnoppo\",DeviceId=\"Xnoppo\",Version=\"0.5\""

        if user_info:
            auth_string += ",UserId=\"" + user_info["User"]["Id"] + "\""

        headers = {}

        if user_info:
            headers["X-MediaBrowser-Token"] = user_info["AccessToken"]

        headers["Accept-encoding"] = "gzip"
        headers["Accept-Charset"] = "UTF-8,*"

        headers["X-Emby-Authorization"] = auth_string

        return headers

    def send_message2(self,session_id, sms_txt, timeout=3500):
        url = self.config.get("emby_server") + '/emby/Sessions/' + session_id + "/Message?Text=" + sms_txt + "&Header=Notification&TimeoutMs=" + str(timeout)
        message_data = {}
        headers = self.get_headers(self.user_info)
        response = requests.post(url, data=message_data, headers=headers)
        if self.config["DebugLevel"]>0: print (response.text)

        return response

    def set_capabilities(self):
        url = self.config.get("emby_server") + '/emby/Sessions/Capabilities/Full?format=json'
        message_data = {
                'IconUrl': "https://img.alicdn.com/imgextra/i1/1840220527/O1CN018lXYlv1FlPES6Bgcw_!!1840220527.png",
                'SupportsMediaControl': True,
                'PlayableMediaTypes': ["Video", "Audio"],
                'SupportedCommands': ["Play",
                                      "Playstate",
                                      "MoveUp",
                                      "MoveDown",
                                      "MoveLeft",
                                      "MoveRight",
                                      "Select",
                                      "Back",
                                      "ToggleContextMenu",
                                      "ToggleFullscreen",
                                      "ToggleOsdMenu",
                                      "GoHome",
                                      "PageUp",
                                      "NextLetter",
                                      "GoToSearch",
                                      "GoToSettings",
                                      "PageDown",
                                      "PreviousLetter",
                                      "TakeScreenshot",
                                      "VolumeUp",
                                      "VolumeDown",
                                      "ToggleMute",
                                      "SendString",
                                      "DisplayMessage",
                                      "SetAudioStreamIndex",
                                      "SetSubtitleStreamIndex",
                                      "SetRepeatMode",
                                      "Mute",
                                      "Unmute",
                                      "SetVolume",
                                      "PlayNext",
                                      "PlayMediaSource"],
                'DeviceProfile':{}
            }
        headers = self.get_headers(self.user_info)
        if self.config["DebugLevel"]>0: print(message_data)
        response = requests.post(url, data=message_data, headers=headers)
        if self.config["DebugLevel"]>0: print (response.text)

        return response

    def set_movie(self,session_id,item_id,item_type,item_name):

        url = self.config.get("emby_server") + '/emby/Sessions/' + str(session_id) + "/Viewing?ItemType=" + str(item_type) + "&ItemId=" + str(item_id) + '&ItemName=' + str(item_name)

        message_data = {}
        headers = self.get_headers(self.user_info)
        response = requests.post(url, data=message_data, headers=headers)
        if self.config["DebugLevel"]>0: print (response.text)

        return response


    def get_ulr_data(self,url, config, user_info):

        if url.find("{server}") != -1:
            server = config["emby_server"]
            url = url.replace("{server}", server)

        if url.find("{userid}") != -1:
            user_id = user_info["User"]["Id"]
            url = url.replace("{userid}", user_id)

        headers = self.get_headers(user_info)
        #print (url)
        logging.debug(url)
        response = requests.get(url, headers=headers)
        #print (response.text)
        return response.text


    def set_watched(item_id, watched_status, config, user_info):

        url = "{server}/emby/Users/{userid}/PlayedItems/" + item_id

        if url.find("{server}") != -1:
            server = config["emby_server"]
            url = url.replace("{server}", server)

        if url.find("{userid}") != -1:
            user_id = user_info["User"]["Id"]
            url = url.replace("{userid}", user_id)

        headers = get_headers(user_info)

        if watched_status:
            requests.post(url, headers=headers)
        else:
            requests.delete(url, headers=headers)

    def send_user_message(self,user_id,message,timeout=3500):
        url = ('{server}/emby/Sessions?ControllableByUserId=' + user_id)
        response_data = self.get_ulr_data(url, self.config, self.user_info)
        item_list = json.loads(response_data)
        logging.debug('Session_Info Response Data: %s',response_data)
        for item in item_list:
           item_data = {}
           item_data["Id"] = item["Id"]
           self.send_message2(item_data["Id"],message,timeout)
        return item_data

    def get_session_info(self,device_id):
        url = ('{server}/emby/Sessions?DeviceId=' + device_id)
        response_data = self.get_ulr_data(url, self.config, self.user_info)
        item_list = json.loads(response_data)
        logging.debug('Session_Info Response Data: %s',response_data)
        for item in item_list:
           item_data = {}
           item_data["Id"] = item["Id"]
           item_data["Client"] = item["Client"]
           item_data["DeviceName"] = item["DeviceName"]
           item_data["NowPlayingItem"] = item["NowPlayingItem"]
           logging.info("Session ID             : %s " % item_data["Id"])
           logging.info("Client                 : %s " % item_data["Client"])
           logging.info("DeviceName             : %s " % item_data["DeviceName"])
           logging.info("Path                   : %s " % item_data["NowPlayingItem"]["Path"])
           logging.info("-----------------------------------------------------------\n")
        return item_data

    def get_session_user_info(self,user_id,device_id):
            #url = ('{server}/emby/Sessions?ControllableByUserId=' + str(user_id) + '&DeviceID=' + str(device_id))
            url = ('{server}/emby/Sessions?DeviceiD=' + str(device_id))
            time.sleep(1)
            response_data = self.get_ulr_data(url, self.config, self.user_info)
            item_list = json.loads(response_data)
            logging.debug('Session_user_info Response Data: %s',response_data)
            item = {}
            for item in item_list:
               item_data = {}
               item_data["Id"] = item["Id"]
               item_data["Client"] = item["Client"]
               item_data["DeviceName"] = item["DeviceName"]
               logging.info("Session ID             : %s " % item_data["Id"])
               logging.info("Client                 : %s " % item_data["Client"])
               logging.info("DeviceName             : %s " % item_data["DeviceName"])
               try:
                   if item["NowPlayingItem"]:
                       item_data["NowPlayingItem"] = item["NowPlayingItem"]
                       logging.info("Path                   : %s " % item_data["NowPlayingItem"]["Path"])
                       logging.info("Name                   : %s " % item_data["NowPlayingItem"]["Name"])
               except:
                   pass
               logging.info("-----------------------------------------------------------\n")
            return item


    def get_item_path(self,user_id,item_id):
        url2 = ('{server}/emby/Users/' + str(user_id) + '/Items/' + str(item_id))
        response_data_item = self.get_ulr_data(url2, self.config, self.user_info)
        item_list_data = json.loads(response_data_item)
        logging.debug('Item List Data Path %s',item_list_data["Path"])
        return item_list_data["Path"]

    def get_item_info(self,user_id,item_id):
        url2 = ('{server}/emby/Users/' + str(user_id) + '/Items/' + str(item_id))
        response_data_item = self.get_ulr_data(url2, self.config, self.user_info)
        item_list_data = json.loads(response_data_item)
        logging.debug('Item List Data %s',item_list_data)
        return item_list_data

    def get_item_info2(self,user_id,item_id,mediasource_id):
        url2 = ('{server}/emby/Users/' + str(user_id) + '/Items/' + str(item_id))
        response_data_item = self.get_ulr_data(url2, self.config, self.user_info)
        item_list_data = json.loads(response_data_item)
        logging.debug('Item List Data %s',item_list_data)
        for mediasource in item_list_data["MediaSources"]:
            if mediasource["Id"]==mediasource_id:
                return(mediasource)
        return item_list_data
    
    def get_item_container(self,user_id,item_id):
        url2 = ('{server}/emby/Users/' + str(user_id) + '/Items/' + str(item_id))
        response_data_item = self.get_ulr_data(url2, self.config, self.user_info)
        item_list_data = json.loads(response_data_item)
        logging.debug('Item List Data Container %s',item_list_data["Container"])
        return item_list_data["Container"]

    def get_item_ascenstors(self,item_id):
        url2 = ('{server}/emby/Items/' + str(item_id) + '/Ancestors')
        response_data_item = self.get_ulr_data(url2, self.config, self.user_info)
        item_list_data = json.loads(response_data_item)
        logging.debug('Item List Data Container %s',item_list_data)
        return item_list_data
   
    def get_user_views(self,user_id):
        url2 = ('{server}/emby/Users/' + str(user_id) + '/Views?IncludeExternalContent=false')
        response_data_item = self.get_ulr_data(url2, self.config, self.user_info)
        item_list_data = json.loads(response_data_item)
        logging.debug('Item List Data User Views %s',item_list_data)
        return item_list_data["Items"]
    
    def get_view_items(self,user_id,view_id):
        url1 = ('{server}/emby/Users/' + str(user_id) + '/Items?parentId=' + str(view_id))
        url2 = ('{server}/emby/Items?parentId=' + str(view_id))
        response_data_item = self.get_ulr_data(url2, self.config, self.user_info)
        item_list_data = json.loads(response_data_item)
        #if item_list_data!=None:
            #logging.debug('Item List Data View Items %s',item_list_data)
        return item_list_data["Items"]

    def get_view_items2(self,user_id,view_id,item_id):
        url2 = ('{server}/emby/Users/' + str(user_id) + '/Items?parentId=' + str(view_id) + '&item_id=' + str(item_id))
        response_data_item = self.get_ulr_data(url2, self.config, self.user_info)
        item_list_data = json.loads(response_data_item)
        #if item_list_data!=None:
            #logging.debug('Item List Data View Items %s',item_list_data)
        return item_list_data["Items"]

    def get_info_from_device(self,device_id):
        url = ('{server}/emby/Sessions?DeviceId=' + device_id)
        response_data = self.get_ulr_data(url, self.config, self.user_info)
        item_list = json.loads(response_data)
        if self.config["DebugLevel"]>2:
            logging.debug('Response Data: %s',response_data)
        for item in item_list:
            item_data = {}
            item_data["Id"] = item["Id"]
            item_data["Client"] = item["Client"]
            item_data["DeviceName"] = item["DeviceName"]
            print (item_data["Id"])
            logging.info ("Session ID             : %s " % item_data["Id"])
            logging.info ("Client                 : %s " % item_data["Client"])
            logging.info ("DeviceName             : %s " % item_data["DeviceName"])
            logging.info ("-----------------------------------------------------------")
        return(item)

    def is_item_in_library(self,ViewID,item_id):
        resultado=False
        ItemList = self.get_view_items(self.user_info["User"]["Id"],ViewID)
        for Item in ItemList:
                #print(Item["Id"])
                if Item["Id"]==item_id:
                    return(True)
        return(resultado)

    def is_item_in_library2(self,ViewID,item_path):
        resultado=False
        MediaFolders = self.get_emby_selectablefolders()
        for Folder in MediaFolders:
            if Folder["Id"]==ViewID:
                for SubFolder in Folder["SubFolders"]:
                    resultado=item_path.startswith(SubFolder["Path"])
                    if resultado:
                        return(resultado)
        return(resultado)

    def get_emby_devices(self):
        url = ('{server}/emby/Devices?')
        response_data = self.get_ulr_data(url, self.config, self.user_info)
        item_list = json.loads(response_data)
        return(item_list)


    def get_emby_selectablefolders(self):
        url = ('{server}/emby/Library/SelectableMediaFolders?')
        response_data = self.get_ulr_data(url, self.config, self.user_info)
        item_list = json.loads(response_data)
        return(item_list)

    def get_xnoppo_audio_index(self,user_id,item_id,index):
        response = self.get_item_info(user_id,item_id)
        audio_index=0
        for media in response["MediaStreams"]:
            if media["Type"]=="Audio":
                audio_index=audio_index+1
                if media["Index"]==index:
                    return(audio_index)
        return(1)

    def get_xnoppo_subs_index(self,user_id,item_id,index):
        if index < 0:
            return(0)
        else:
            response = self.get_item_info(user_id,item_id)
            if self.config["DebugLevel"]>0: print(response["MediaStreams"])
            subs_index=0
            for media in response["MediaStreams"]:
                if media["Type"]=="Subtitle":
                    subs_index=subs_index+1
                    if media["Index"]==index:
                        return(subs_index)
            return(0)

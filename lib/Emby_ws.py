#
# Thanks for websocket-client library. 
#
# Copyright 2018 Hiroki Ohtani.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import threading
from websocket import WebSocketApp    
import logging
import json
import time
from .Emby_http import EmbyHttp
from .Xnoppo import *

class xnoppo_ws(threading.Thread):
    emby_state=''
    stop_websocket = False
    ws_config=None
    ws_user_info=None
    EmbySession=None
    MonitoredState=''
    config_file=''
    ws_lang=None

    def stop(self):
        print('ws stop')
        self.stop_websocket=True;
        self.ws.close()
        exit
    def __init__(self):

        self.emby_state='Init'
        threading.Thread.__init__(self)
        logging.info('Ws:Fin init\n')

    def thread_function_play(self,data,scripterx=False):
        print("Thread Play: starting")
        playto_file(self.EmbySession,data,scripterx)
        self.recargar_config()
        print("Thread Play: finishing")
    
    def set_lang(self,lang):
        self.ws_lang=lang
        self.EmbySession.lang=lang

    def recargar_config(self):
        if self.ws_config["DebugLevel"]>0: print('Recargando Configuracion')
        with open(self.config_file, 'r') as f:    
                config = json.load(f)
        f.close
        ## new options default config values
        default = config.get("Autoscript", False)
        config["Autoscript"]=default
        default = config.get("enable_all_libraries", False)
        config["enable_all_libraries"]=default
        default = config.get("TV_model", "")
        config["TV_model"]=default
        default = config.get("TV_SOURCES", [])
        config["TV_SOURCES"] = default
        default = config.get("AV_model", "")
        config["AV_model"]=default
        default = config.get("AV_SOURCES", [])
        config["AV_SOURCES"] = default
        default = config.get("AV_Port", 23)
        config["AV_Port"]=default
        default = config.get("TV_script_init", "")
        config["TV_script_init"]=default
        default = config.get("TV_script_end", "")
        config["TV_script_end"]=default
        default = config.get("av_delay_hdmi", 0)
        config["av_delay_hdmi"]=default
        default = config.get("language","es-ES")
        config["language"]=default
        default = config.get("default_nfs",False)
        config["default_nfs"]=default
        default = config.get("wait_nfs",False)
        config["wait_nfs"]=default
        default = config.get("refresh_time",5)
        config["refresh_time"]=default
        default = config.get("check_beta",False)
        config["check_beta"]=default
        default = config.get("smbtrick",False)
        config["smbtrick"]=default

        ##
        self.ws_config=config
        self.EmbySession.config=config
        return(config)
    
    def _play(self, data):
        command = data['PlayCommand']
        if command == 'PlayNow':
            #self.EmbySession.playnow(data)
            if self.EmbySession.playstate=="Loading" or self.EmbySession.playstate=="Replay":
                if self.ws_config["DebugLevel"]>0: print("Esta en la pantalla de Loading, tenemos que esperar")
                timeout=60
                time=0
                while self.EmbySession.playstate=="Loading" or time>timeout:
                    time.sleep(3)
                    time=time+3
            if self.EmbySession.playstate=="Playing":
                if self.ws_config["DebugLevel"]>0: print("ya se esta reproduciendo algo")
                playother(self.EmbySession,data,False)
            else:
                x = threading.Thread(target=self.thread_function_play, args=(data,))
                x.start()
            #playto_file(self.EmbySession,data)
    def _general_commands(self,data):
        cmd = data['Name']
        args = data['Arguments']
        #print(cmd)
        #print(args)
        if cmd == 'SetAudioStreamIndex':
            params = self.EmbySession.process_data(self.EmbySession.currentdata)
            audio_index = self.EmbySession.get_xnoppo_audio_index(params["ControllingUserId"],params["item_id"],int(args['Index']))
            setaudiotrack(self.ws_config,audio_index)
            self.EmbySession.currentdata["AudioStreamIndex"]=int(args['Index'])
        elif cmd == 'SetSubtitleStreamIndex':
            params = self.EmbySession.process_data(self.EmbySession.currentdata)
            subs_index = self.EmbySession.get_xnoppo_subs_index(params["ControllingUserId"],params["item_id"],int(args['Index']))
            setsubstrack(self.ws_config,subs_index)
            self.EmbySession.currentdata["SubtitleStreamIndex"]=int(args['Index'])
        #elif cmd == 'SetVolume'
        
    def _check_state(self,data):
        if self.ws_config["MonitoredDevice"]:
            item_data = self.EmbySession.get_session_user_info(data["UserId"],self.ws_config["MonitoredDevice"])
##            if item_data:
            try:
                if item_data["NowPlayingItem"]:
                    #print(item_data)
                    if self.MonitoredState == '':
                        #print('Started Playing')
                        if self.ws_config["DebugLevel"]>0: print(item_data["DeviceName"])
                        if self.ws_config["DebugLevel"]>0: print(item_data["NowPlayingItem"]["Name"])
                        if self.ws_config["DebugLevel"]>0: print(item_data["NowPlayingItem"]["Container"])
                        self.MonitoredState=item_data["NowPlayingItem"]["Name"]
                        itemtype=item_data["NowPlayingItem"]["Type"]
                        item_id=item_data["NowPlayingItem"]["ParentId"]
                        item_name=item_data["NowPlayingItem"]["Name"]
                        if itemtype=="Episode":
                            #item_lib_id=item_data["NowPlayingItem"]["SeriesId"]
                            item_lib_id=item_data["NowPlayingItem"]["Path"]
                        elif itemtype=="Movie":
                            #item_lib_id=item_data["NowPlayingItem"]["Id"]
                            item_lib_id=item_data["NowPlayingItem"]["Path"]
                        views_list=self.ws_config["Libraries"]
                        LibraryName=""
                        encontrado=False
                        if self.ws_config["enable_all_libraries"]:
                               LibraryName="All Libraries Enabled"
                               encontrado=True
                        else:
                            for view in views_list:
                                view_data = {}
                                if view["Active"]==True:
                                        view_data["Name"] = view["Name"]
                                        view_data["Id"] = view["Id"]
                                        encontrado=self.EmbySession.is_item_in_library2(view["Id"],item_lib_id)
                                        if encontrado:
                                            LibraryName=view_data["Name"]
                                            break
                        if encontrado:
                            if self.ws_config["DebugLevel"]>0: print("LIBRARY NAME: " + LibraryName)
                            logging.debug('El item %s es de la libreria %s',item_name,LibraryName)
                            userdatalist=data["UserDataList"]
                            userdata=userdatalist[0]
                            try:
                                playstate = item_data["PlayState"]
                            except:
                                playstate = {}
                            data2 = {
                                    "ItemIds":[int(item_data["NowPlayingItem"]["Id"])],
                                    "StartIndex":0,
                                    "StartPositionTicks": userdata["PlaybackPositionTicks"],
                                    "MediaSourceId": playstate.get("MediaSourceId",""),
                                    "AudioStreamIndex": playstate.get("AudioStreamIndex",1),
                                    "SubtitleStreamIndex": playstate.get("SubtitleStreamIndex",-1),
                                    "ControllingUserId":data["UserId"],
                                    "SessionID": item_data["Id"],
                                    "DeviceName": item_data["DeviceName"],
                                    "Device_Id": self.ws_config["MonitoredDevice"]
                                   }
                            if self.ws_config["DebugLevel"]>0: print(data2)
                            timeout=60
                            time=0
                            while self.EmbySession.playstate=="Loading" or time>timeout:
                                    time.sleep(3)
                                    time=time+3
                            if self.EmbySession.playstate=="Playing" or self.EmbySession.playstate=="Replay":
                                if self.ws_config["DebugLevel"]>0: print("ya se esta reproduciendo algo")
                                playother(self.EmbySession,data2,True)
                            else:
                                x = threading.Thread(target=self.thread_function_play, args=(data2,True))
                                x.start()
                            return(0)
                        else:
                            if self.ws_config["DebugLevel"]>0: print('El item no es de ninguna libreria activa: ' + item_name)
                            logging.debug('El item %s no es de ninguna libreria activa',item_name)
                    elif item_data["NowPlayingItem"]["Name"]==self.MonitoredState:
                        if self.ws_config["DebugLevel"]>0: print('Continue Playing')
                        if self.ws_config["DebugLevel"]>0: print(item_data["DeviceName"])
                        if self.ws_config["DebugLevel"]>0: print(self.MonitoredState)
                        if self.ws_config["DebugLevel"]>0: print(item_data["NowPlayingItem"]["Name"])
                    else:
                        if self.ws_config["DebugLevel"]>0: print('Change Playing')
                        if self.ws_config["DebugLevel"]>0: print(item_data["DeviceName"])
                        if self.ws_config["DebugLevel"]>0: print(self.MonitoredState)
                        if self.ws_config["DebugLevel"]>0: print(item_data["NowPlayingItem"]["Name"])
##            else:
            except:
                if self.MonitoredState!='':
                    if self.ws_config["DebugLevel"]>0: print('Stopped Playing')
                    if self.ws_config["DebugLevel"]>0: print(item_data["DeviceName"])
                    if self.ws_config["DebugLevel"]>0: print(self.MonitoredState)
                    self.MonitoredState=''

    def _playstate(self, data):
        command = data['Command']
        if command == 'Stop':
            sendremotekey('STP',self.ws_config)
        elif command == 'Pause':
            sendremotekey('PAU',self.ws_config)
        elif command == 'Unpause':
            sendremotekey('PLA',self.ws_config)
        elif command == 'NextTrack':
            sendremotekey('NXT',self.ws_config)
        elif command == 'PreviousTrack':
            sendremotekey('PRE',self.ws_config)
        elif command == 'Seek':
            playticks=data["SeekPositionTicks"]
            setplaytime(self.ws_config,playticks)
        elif command == 'Rewind':
            sendremotekey('REV',self.ws_config)
        elif command == 'FastForward':
            sendremotekey('FWD',self.ws_config)
        elif command == 'PlayPause':
            sendremotekey('PAU',self.ws_config)

    def on_message(ws, msg):
        if ws.ws_config["DebugLevel"]>0: print ("Ws:Message Arrived:" + msg)
        if ws.ws_config["DebugLevel"]>0: print (ws.EmbySession.playstate)
        logging.debug ("Ws:Message Arrived: %s",msg)
        ws.emby_state="Message Arrived:" + msg
        msg_json = json.loads(msg)
        msg_type = msg_json['MessageType']

        if msg_type == 'Play':
            data = msg_json['Data']
            ws._play(data)

        elif msg_type == 'Playstate':
            data = msg_json['Data']
            ws._playstate(data)

        elif msg_type == "UserDataChanged":
            data = msg_json['Data']
            ws._check_state(data)

        elif msg_type == "LibraryChanged":
            data = msg_json['Data']
#          ws._library_changed(data)

        elif msg_type == "GeneralCommand":
            data = msg_json['Data']
            ws._general_commands(data)

        else:
            logging.debug("WebSocket Message Type: %s", msg_type)
    def on_error(ws, error):
        if ws.ws_config["DebugLevel"]>0: print (error)
        ws.emby_state='Ws::Error'
        
    def on_close(ws):
        if ws.ws_config["DebugLevel"]>0: print ("Ws:Connection Closed")
        ws.emby_state='Closed'

    def on_open(ws):
       if ws.ws_config["DebugLevel"]>0: print('Ws:Open')
       ws.emby_state='Opened'
       ws.send("Hello!")

    def run(self):
        self.EmbySession=EmbyHttp(self.ws_config)
        self.EmbySession.lang=self.ws_lang
        self.ws_user_info = self.EmbySession.user_info
        self.EmbySession.set_capabilities()
        uri = self.ws_config["emby_server"].replace('http://', 'ws://').replace('https://', 'wss://')
        uri = uri + '/?api_key=' + self.ws_user_info["AccessToken"] + '&deviceId=''Xnoppo'''
        if self.ws_config["DebugLevel"]>0: print(uri)
        self.ws = WebSocketApp(uri,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        if self.ws_config["DebugLevel"]>0: print('Ws:Fin open ws\n')
        self.emby_state='Run'
        while not self.stop_websocket:
            self.ws.run_forever(ping_interval=10)
            if self.ws_config["DebugLevel"]>0: print("after run forever")
            if self.stop_websocket:
                break
            self.emby_state='On run_forever'
            #print("Reconnecting WebSocket")

        if self.ws_config["DebugLevel"]>0: print("WebSocketClient Stopped")


import json
import os
import sys
import asyncio
from importlib import reload
from lib.Emby_http import *
from lib.Xnoppo import *
from lib.Xnoppo_TV import *
import lib.Xnoppo_AVR
from lib.Xnoppo_AVR import av_config
from lib.Xnoppo_AVR import av_test

import shutil

def restart():
        import sys
        #print("argv was",sys.argv)
        #print("sys.executable was", sys.executable)
       
        import os
        #os.execv(sys.executable,sys.argv)
        cwd = os.path.dirname(os.path.abspath(config_file))
        if sys.platform.startswith('win'):
              separador="\\"
        else:
              separador="/"
        cfile=cwd + separador + "emby_xnoppo_conf.py"
        command = sys.executable + ' "' + cfile + '"'
        #print(command)
        #print("restart now")
        os.system(command)

def menu_principal():
    opcion=0
    while opcion==0:
        print("-----------------------------------------------------------")
        print("Seleccione una opcion indicando el numero de la misma")
        print("1.Iniciar asistente de configuracion")
        print("2.Configuracion Avanzada")
        print("3.Ver configuracion")
        print("4.Salir")
        print("-----------------------------------------------------------")
        try:
            opcion = int(input())
            if opcion>4:
                opcion=0
                print ("Elija una de las opciones del 1 al 4")
        except:
            print ("Elija una de las opciones del 1 al 4")
    return(opcion)

def menu_advanced():
    opcion=0
    while opcion==0:
        print("-----------------------------------------------------------")
        print("Seleccione una opcion indicando el numero de la misma")
        print("1.Cambiar configuracion de Emby")
        print("2.Cambiar configuracion de Oppo")
        print("3.Cambiar configuracion de TV")
        print("4.Cambiar configuracion de AV")
        print("5.Cambiar otros parametros")
        print("6.Configurar Librerias")
        print("7.Consultar Dispositivos Emby")
        print("8.Consultar Dispositivos Oppo")
        print("9.Realizar Tests")
        print("10.Ver configuracion")
        print("11.Salir")
        print("-----------------------------------------------------------")
        try:
            opcion = int(input())
            if opcion>11:
                opcion=0
                print ("Elija una de las opciones del 1 al 11")
        except:
            print ("Elija una de las opciones del 1 al 11")
    return(opcion)

def menu_servers():
    opcion=0
    while opcion==0:
        print("-----------------------------------------------------------")
        print("Seleccione una opcion indicando el numero de la misma")
        print("1.Editar Servidores existentes")
        print("2.Añadir un Servidor")
        print("3.Eliminar un Servidor")
        print("4.Salir")
        print("-----------------------------------------------------------")
        try:
            opcion = int(input())
            if opcion>4:
                opcion=0
                print ("Elija una de las opciones del 1 al 4")
        except:
            print ("Elija una de las opciones del 1 al 4")
    return(opcion)

def menu_libraries():
    opcion=0
    while opcion==0:
        print("-----------------------------------------------------------")
        print("Seleccione una opcion indicando el numero de la misma")
        print("1.Activar una libreria")
        print("2.Desactivar una libreria")
        print("3.Activar todas las librerias")
        print("4.Salir")
        print("-----------------------------------------------------------")
        try:
            opcion = int(input())
            if opcion>4:
                opcion=0
                print ("Elija una de las opciones del 1 al 4")
        except:
            print ("Elija una de las opciones del 1 al 4")
    return(opcion)


def save_config(config_file, config):
    with open(config_file, 'w') as fw:
        json.dump(config, fw, indent=4)
    fw.close

def get_confirmation(texto):
    valor=''
    while valor!='s' and valor!='n':
        valor = input(texto+": ")
        if valor=="s":
            return(0)
        elif valor=="n":
            return(1)
        elif valor=="S":
            return(0)
        elif valor=="N":
            return(1)
        else:
            print('Responda s,S,n o N')

def get_parametro(texto,valor_actual):
    valor = input(texto+": ")
    if valor=="":
        valor=valor_actual
    return(valor)

def get_parametro_int(texto,valor_actual):
    valor=''
    while valor=='':
        valor = input(texto+": ")
        if valor=="":
            result=valor_actual
            valor='0'
        else:
            try:
                result=int(valor)
            except:
                valor=''
                print('Introduzca un numero entero')
    return(result)

def conf_assistant(config):
    config["actual_menu"]='AS'
    if config["resume_on"]=='':
        print("-----------------------------------------------------------")
        print("               Asistente de configuracion                  ")
        print("-----------------------------------------------------------")
        a=input("Inicio del asistente de configuracion, encienda su TV, OPPO, app Emby en el TV y AV presione ENTER para continuar")
        print("-----------------------------------------------------------")
        print("               Configuracion Conexion Emby                 ")
        print("-----------------------------------------------------------")
        result=''
        while result!='OK':
            config_emby(config)
            save_config(config_file, config)
            result=test_emby(config)
        print("-----------------------------------------------------------")
        print("               Configuracion Conexion OPPO                 ")
        print("-----------------------------------------------------------")
        result=''
        while result!='OK':
            config_oppo(config)
            save_config(config_file, config)
            result=test_oppo(config)
        print("-----------------------------------------------------------")
        print("               Configuracion Librerias EMBY                ")
        print("-----------------------------------------------------------")
        config_libraries_assist(config)
        save_config(config_file, config)
        print("-----------------------------------------------------------")
        print("Configuracion Servers (Transformacion de Rutas Emby->Xnoppo")
        print("-----------------------------------------------------------")
        print("Las rutas donde estan los archivos que ve el Xnoppo pueden no ser las mismas que las que estan disponibles en Emby.")
        print("Por eso es necesario transformar esas rutas de como estan en EMBY a como las ve el OPPO.")
        print("Para ello se precargaran las rutas disponibles en EMBY y se dará la opcion de condigurar cada una de ellas.")
        print("Tambien se conectara al OPPO para obtener un listado de los dispositivos/rutas disponibles en el OPPO")
        get_selectableFolders(config)
        servers=[]
        oppo_paths=get_oppo_devices_str(config)
        for server in config["servers"]:
            print("-----------------------------------------------------------")
            server_new=edit_server(server,oppo_paths,config)
            servers.append(server_new)
        config["servers"]=servers
        save_config(config_file, config)
        print("-----------------------------------------------------------")
        print("               Configuracion TV                            ")
        print("-----------------------------------------------------------")
    if config["resume_on"]=='' or config["resume_on"]=='TV_AS':
        config_TV(config)
        save_config(config_file, config)
        if config["TV"]=="True":
            result=tv_test(config)
            print(result)
    print("-----------------------------------------------------------")
    print("               Configuracion AV                            ")
    print("-----------------------------------------------------------")
    config_AV(config)
    save_config(config_file, config)
    if config["AV"]=="True":
        result=av_test(config)
        print(result)
    print("-----------------------------------------------------------")
    print("               Configuracion Otros Parametros              ")
    print("-----------------------------------------------------------")
    config_others(config)
    save_config(config_file, config)
    print("El asistente de configuracion ha terminado")
    print("-----------------------------------------------------------")
    print("            Fin Asistente de configuracion                 ")
    print("-----------------------------------------------------------")

def advanced_config(config):
    config["actual_menu"]='ADV'
    if config["resume_on"]=='TV_ADV':
        config_TV(config)
        save_config(config_file, config)
    elif config["resume_on"]=='AV_ADV':
        config_AV(config)
        save_config(config_file, config)
    result=0
    while result!=11:
        result=menu_advanced()
        if result==1:
            config_emby(config)
            save_config(config_file, config)
            test_emby(config)
        elif result==2:
            config_oppo(config)
            config_servers(config)
            save_config(config_file, config)
        elif result==3:
            config_TV(config)
            save_config(config_file, config)
        elif result==4:
            config_AV(config)
            save_config(config_file, config)
        elif result==5:
            config_others(config)
            save_config(config_file, config)        
        elif result==6:
            config_libraries(config)
            save_config(config_file, config)
        elif result==7:
            a=input("A continuación se mostraran las sesiones y dispositivos abiertos en Emby, si quiere conectar alguno como el Emby de la TV hagalo ahora. Presiene ENTER para continuar")
            get_devices(config)
        elif result==8:
            get_oppo_devices(config)
        elif result==9:
            test_emby(config)
            test_oppo(config)
            test_mounts(config)
            tv_test(config)
            av_test(config)
        elif result==10:
            ver_configuracion(config)

def config_emby(config):
    print("A continuacion se solicitaran los parametros relativos a Emby, dejarlo en blanco y pulsar ENTER deja el parametro al valor actual")
    es_correcto=False
    while es_correcto==False:
        emby_server=get_parametro("Introduzca el valor para Emby Server, formato http://YOUR_EMBY_SERVER:8096, valor actual " + config["emby_server"],config["emby_server"])
        user_name=get_parametro("Introduzca el valor para User Name, valor actual " + config["user_name"],config["user_name"])
        user_password=get_parametro("Introduzca el valor para User Password, valor actual " + config["user_password"],config["user_password"])
        print ("Emby Server            : %s" % emby_server)
        print ("User Name              : %s" % user_name)
        print ("User Pass              : %s" % user_password)
        result=get_confirmation('Esta es la nueva configuracion, es correcta? (s/n)')
        if result==0:
            es_correcto=True
            config["emby_server"]=emby_server
            config["user_name"]=user_name
            config["user_password"]=user_password
        else:
            es_correcto=False

def config_oppo(config):
    print("A continuacion se solicitaran los parametros relativos al OPPO, dejarlo en blanco y pulsar ENTER deja el parametro al valor actual")
    es_correcto=False
    while es_correcto==False:
        oppo_server=get_parametro("Introduzca el valor para el Oppo IP, valor actual " + config["Oppo_IP"],config["Oppo_IP"])
##        user_name=get_parametro("Introduzca el valor para Oppo User Name, valor actual " + config["oppo_smb_user"],config["oppo_smb_user"])
##        user_password=get_parametro("Introduzca el valor para Oppo User Password, valor actual " + config["oppo_smb_pwd"],config["oppo_smb_pwd"])
        Timeout_oppo_conection=get_parametro_int("Introduzca el valor para Timeout_oppo_conection, valor actual " + str(config["timeout_oppo_conection"]),config["timeout_oppo_conection"])
        Timeout_oppo_playitem=get_parametro_int("Introduzca el valor para Timeout_oppo_playitem, valor actual " + str(config["timeout_oppo_playitem"]),config["timeout_oppo_playitem"])
        Always_on_r=get_confirmation('El OPPO va a estar siempre encendido al iniciar la reproduccion (no en suspensión)? (s/n)')
        if Always_on_r ==0:
            Always_on=True
        else:
            Always_on=False
        Autoscript_r=get_confirmation('El OPPO tiene instalado el Autoscript? (s/n)')
        if Autoscript_r ==0:
            Autoscript=True
        else:
            Autoscript=False
        print ("Oppo IP                     : %s" % oppo_server)
##        print ("Oppo User Name              : %s" % user_name)
##        print ("Oppo User Pass              : %s" % user_password)
        print ("Timeout_oppo_conection      : %s" % Timeout_oppo_conection)
        print ("Timeout_oppo_playitem       : %s" % Timeout_oppo_playitem)
        print ("Always ON                   : %s" % Always_on)
        print ("Autoscript                  : %s" % Autoscript)
        result=get_confirmation('Esta es la nueva configuracion, es correcta? (s/n)')
        if result==0:
            es_correcto=True
            config["Oppo_IP"]=oppo_server
##            config["oppo_smb_user"]=user_name
##            config["oppo_smb_pwd"]=user_password
            config["timeout_oppo_conection"]=Timeout_oppo_conection
            config["timeout_oppo_playitem"]=Timeout_oppo_playitem
            config["Always_ON"]=Always_on
            config["Autoscript"]=Autoscript
        else:
            es_correcto=False

def edit_servers(config):
    print("Introduzca el server a Editar")
    print("-----------------------------------------------------------")
    server_list=config["servers"]
    encontrado=False
    while encontrado==False:
        for server in server_list:
                print("Server Name            : %s " % server["name"])
                print("Emby Path              : %s " % server["Emby_Path"])
                print("Oppo Path              : %s " % server["Oppo_Path"])
                print("-----------------------------------------------------------")
        server_name=input()
        index=0
        for server in server_list:
            if server["name"]==server_name:
                edit_server=index
                encontrado=True
            index=index+1
            
        if encontrado==False:
            print("Nombre del servidor incorrecto")
    print("A continuacion se solicitaran los parametros relativos al server, dejarlo en blanco y pulsar ENTER deja el parametro al valor actual")
    es_correcto=False
    while es_correcto==False:
        name_server=get_parametro("Introduzca el valor para el Server Name, valor actual " + server_list[edit_server]["name"],server_list[edit_server]["name"])
        emby_path=get_parametro("Introduzca el valor para Emby Path, valor actual " + server_list[edit_server]["Emby_Path"],server_list[edit_server]["Emby_Path"])
        oppo_path=get_parametro("Introduzca el valor para Oppo Path, valor actual " + server_list[edit_server]["Oppo_Path"],server_list[edit_server]["Oppo_Path"])
        print ("Server Name                 : %s" % name_server)
        print ("Emby Path                   : %s" % emby_path)
        print ("Oppo Path                   : %s" % oppo_path)
        result=get_confirmation('Esta es la nueva configuracion, es correcta? (s/n)')
        if result==0:
            es_correcto=True
            server_list[edit_server]["name"]=name_server
            server_list[edit_server]["Emby_Path"]=emby_path
            server_list[edit_server]["Oppo_Path"]=oppo_path
            config["servers"]=server_list
        else:
            es_correcto=False

def edit_server(server,oppo_path,config):
    es_correcto=False
    server_test={}
    while es_correcto==False:
        print("Configuracion de rutas, esto son las rutas disponibles en el OPPO: ")
        print(oppo_path)
        print("A continuacion se solicitara el valor correspondiente a la ruta del OPPO, dejarlo en blanco y pulsar ENTER deja el parametro al valor actual")
        name_server=server["name"]
        emby_path=server["Emby_Path"]
        print ("Server Name                 : %s" % name_server)
        print ("Emby Path                   : %s" % emby_path)
        oppo_path=get_parametro("Introduzca el valor para Oppo Path, valor actual " + server["Oppo_Path"],server["Oppo_Path"])
        #print ("Server Name                 : %s" % name_server)
        #print ("Emby Path                   : %s" % emby_path)
        print ("Oppo Path                   : %s" % oppo_path)
        server_test["name"]=name_server
        server_test["Emby_Path"]=emby_path
        server_test["Oppo_Path"]=oppo_path
        rutas = get_mount_path(emby_path + "/test.mkv",server_test)
        ruta_oppo='Red/' + rutas["Servidor"] + '/video/' + rutas["Carpeta"]
        ruta_oppo = ruta_oppo.replace('/','->')
        print ("Para reproducir en el oppo elementos de esta ruta seria necesario ir navegando por :")
        print (ruta_oppo)
        result=get_confirmation('Esta es la nueva configuracion, es correcta? (s/n)')
        if result==0:
            print ('Comprobando montaje de ruta en el OPPO..')
            result2 = test_mount_path(config,rutas["Servidor"],rutas["Carpeta"])
            if result2 == "OK":
                print ("Prueba de montaje CORRECTA!")
                es_correcto=True
                server["name"]=name_server
                server["Emby_Path"]=emby_path
                server["Oppo_Path"]=oppo_path
                return(server)
            else:
                result3=get_confirmation('Prueba de montaje FALLIDA, continuar de todas formas? (s/n)')
                if result3==0:
                    es_correcto=True
                    server["name"]=name_server
                    server["Emby_Path"]=emby_path
                    server["Oppo_Path"]=oppo_path
                    return(server)
                else:
                    es_correcto=False
        else:
            es_correcto=False

def add_server(config):
    server_list=config["servers"]
    print("A continuacion se solicitaran los parametros relativos al nuevo server")
    es_correcto=False
    while es_correcto==False:
        name_server=get_parametro("Introduzca el valor para el Server Name","")
        emby_path=get_parametro("Introduzca el valor para el Emby Path","")
        oppo_path=get_parametro("Introduzca el valor para Oppo Path","")
        print ("Server Name                 : %s" % name_server)
        print ("Emby Path                   : %s" % emby_path)
        print ("Oppo Path                   : %s" % oppo_path)
        result=get_confirmation('Esta es la nueva configuracion, es correcta? (s/n)')
        if result==0:
            es_correcto=True
            server = {}
            server["name"]=name_server
            server["Emby_Path"]=emby_path
            server["Oppo_Path"]=oppo_path
            server_list.append(server)
            config["servers"]=server_list
        else:
            es_correcto=False

def delete_server(config):
    print("Introduzca el server a Eliminar")
    print("-----------------------------------------------------------")
    server_list=config["servers"]
    encontrado=False
    while encontrado==False:
        for server in server_list:
                print("Server Name            : %s " % server["name"])
                print("Emby Path              : %s " % server["Emby_Path"])
                print("Oppo Path              : %s " % server["Oppo_Path"])
                print("-----------------------------------------------------------")
        server_name=input()
        index=0
        for server in server_list:
            if server["name"]==server_name:
                edit_server=index
                encontrado=True
            index=index+1
            
        if encontrado==False:
            print("Nombre del servidor incorrecto")
    #print("A continuacion se solicitaran los parametros relativos al server, dejarlo en blanco y pulsar ENTER deja el parametro al valor actual")
    server_list.pop(edit_server)
    config["servers"]=server_list

def edit_library(config,estado):
    print("Seleccione la libreria a modificar o salir para volver al menu anterior")
    print("-----------------------------------------------------------")
    lib_list=config["Libraries"]
    encontrado=False
    while encontrado==False:
        index=0
        for lib in lib_list:
            if lib["Active"]==True:
                print(str(index) + " - " + lib["Name"] + " - Activada")
            else:
                print(str(index) + " - " + lib["Name"] + " - Desactivada")
            index=index+1
        print(str(index) + " Salir ")
        print("-----------------------------------------------------------")
        lib_index=input("Numero de la libreria: ")
        edit_index=index
        try:
            edit_index=int(lib_index)
        except:
            print("Introduzca el numero de Index d la libreria a modificar")
        if edit_index>index+1:
            print("Introduzca el numero de Index d la libreria a modificar")
        else:
            if edit_index!=index:
                lib_list[edit_index]["Active"]=estado
            else:
                encontrado=True        
    config["Libraries"]=lib_list

def all_library(config,estado):
    print("Marcando todas las librerias como activas")
    lib_list=config["Libraries"]
    index=0
    for lib in lib_list:
        lib["Active"]=estado
        print(str(index) + " - " + lib["Name"] + " - Activada")
    config["Libraries"]=lib_list

def config_servers(config):
    print("Configuracion de Servers (Transformacion de Rutas Emby->Xnoppo). Elige una opcion")
    result=0
    while result!=4:
        result = menu_servers()
        if result==1:
            edit_servers(config)
        elif result==2:
            add_server(config)
        elif result==3:
            delete_server(config)           

def carga_libraries(config):
    try:
        EmbySession=EmbyHttp(config)
        views_list=EmbySession.get_user_views(EmbySession.user_info["User"]["Id"])
        libraries = []
        for view in views_list:
            library= {}
            library["Name"]=view["Name"]
            library["Id"]=view["Id"]
            library["Active"]=False
            try:
                lib_list=config["Libraries"]
            except:
                lib_list={}
            for lib in lib_list:
                if lib["Id"]==view["Id"]:
                     library["Active"]=lib["Active"]
            libraries.append(library)
        config["Libraries"]=libraries
        return(0)
    except:
         return(1)

def config_libraries(config):
    result=carga_libraries(config)
    if result==0:
        print("Configuracion de Librerias (Cuales reproducen en el Xnoppo). Elige una opcion")
        result=0
        while result!=4:
            result = menu_libraries()
            if result==1:
                edit_library(config,True)
            elif result==2:
                edit_library(config,False)
            elif result==3:
                all_library(config,True)
    else:
        print("Hay alguún problema con la configuracion de Emby, revisela")

def config_libraries_assist(config):
    config["Libraries"]=[]
    result=carga_libraries(config)
    libraries=[]
    result0=get_confirmation('Desea activar todas las librerias para su reproduccion en el OPPO? elija N para selecccionar cuales (s/n)')
    if result0 == 0:
        for library in config["Libraries"]:
            library["Active"]=True
            libraries.append(library)
        config["Libraries"]=libraries                     
    else:
        for library in config["Libraries"]:
            result=get_confirmation('Desea activar la libreria ' + library["Name"] + ' (s/n)')
            if result==0:
                library["Active"]=True
            else:
                library["Active"]=False
            libraries.append(library)
        config["Libraries"]=libraries

def get_devices(config):
    try:
        EmbySession=EmbyHttp(config)
        devices = EmbySession.get_emby_devices()
        index=0
        print("-----------------------------------------------------------")
        for device in devices:
                try:
                    if device["Client"]!='DLNA':
                            print("ID                     : %s " % index)
                            print("Session ID             : %s " % device["Id"])
                            print("Client                 : %s " % device["Client"])
                            print("DeviceName             : %s " % device["DeviceName"])
                            print("DeviceID               : %s " % device["DeviceId"])
                            print("-----------------------------------------------------------")
                            index=index+1
                except:
                    pass
        return(devices)
    except:
        print('Revise la configuracion de Emby, no se ha podido conectar')

def is_library_active(config,libraryname):
    for library in config["Libraries"]:
        if library["Name"]==libraryname:
            return(library["Active"])
    return(False)

def get_selectableFolders(config):
        EmbySession=EmbyHttp(config)
        MediaFolders = EmbySession.get_emby_selectablefolders()
        servers=[]
        for Folder in MediaFolders:
            index=1
            active=is_library_active(config,Folder["Name"])
            if active==True:
                for SubFolder in Folder["SubFolders"]:         
                    server={}
                    server["Id"]=SubFolder["Id"]
                    if index>1:
                        server["name"]=Folder["Name"]+"("+str(index)+")"
                    else:
                        server["name"]=Folder["Name"]
                    server["Emby_Path"]=SubFolder["Path"]
                    server["Oppo_Path"]=SubFolder["Path"]
                    servers.append(server)
                    index=index+1
        config["servers"]=servers

def select_device(config):
    devices=get_devices(config)
    max_dev=len(devices)
    device_index=max_dev+1
    while device_index>max_dev:
        device_index = get_parametro_int("Indica el ID del dispositivo",0)
        if device_index>max_dev:
            print("Elija un ID valido")
    device=devices[device_index]
    return(device)

def get_oppo_devices(config):
    sendnotifyremote(config["Oppo_IP"])
    print("Conectando con el OPPO")
    result=check_socket(config)
    if result==0:
        response_data6a = getmainfirmwareversion(config)
        response_data6c = getdevicelist(config)
        response_data6b = getsetupmenu(config)
        response_data6c = OppoSignin(config)
        response_data6d = getdevicelist(config)
        response_data6e = getglobalinfo(config)
        response_data6f = getdevicelist(config)
        response_data_on = sendremotekey("EJT",config)
        time.sleep(1)
        print("Solicitando dispositivos al OPPO")
        response_data6b = getsetupmenu(config)
        while response_data6f.find('devicelist":[]') > 0:
              time.sleep(1)
              response_data6f = getdevicelist(config)
              response_data_on = sendremotekey("QPW",config)
        time.sleep(5)
        response_data6b = getsetupmenu(config)
        device_list=json.loads(response_data6f)
        print("-----------------------------------------------------------")
        for item in device_list["devicelist"]:
            
            print("Type                 : %s " % item["sub_type"])
            print("Name                 : %s " % item["name"])
            print("Path                 : %s " % item["path"])
            print("-----------------------------------------------------------")
        #response_data_off = sendremotekey("POF",config)
    else:
        print("No se puede conectar, revisa las configuraciones o que el OPPO este encendido o en reposo")

def get_oppo_devices_str(config):
    sendnotifyremote(config["Oppo_IP"])
    print("Conectando con el OPPO")
    result=check_socket(config)
    if result==0:
        response_data6a = getmainfirmwareversion(config)
        response_data6c = getdevicelist(config)
        response_data6b = getsetupmenu(config)
        response_data6c = OppoSignin(config)
        response_data6d = getdevicelist(config)
        response_data6e = getglobalinfo(config)
        response_data6f = getdevicelist(config)
        response_data_on = sendremotekey("EJT",config)
        time.sleep(1)
        print("Solicitando dispositivos al OPPO")
        response_data6b = getsetupmenu(config)
        while response_data6f.find('devicelist":[]') > 0:
              time.sleep(1)
              response_data6f = getdevicelist(config)
              response_data_on = sendremotekey("QPW",config)
        time.sleep(5)
        response_data6b = getsetupmenu(config)
        device_list=json.loads(response_data6f)
        print("-----------------------------------------------------------")
        a = "-----------------------------------------------------------\n"
        a = a + "| "
        for item in device_list["devicelist"]:
            
            #print("Type                 : %s " % item["sub_type"])
            #print("Name                 : %s " % item["name"])
            #print("Path                 : %s " % item["path"])
            #print("-----------------------------------------------------------")
            if item["sub_type"]=='cifs':
                a = a + item["path"] + "("+item["sub_type"]+") | "
        #response_data_off = sendremotekey("POF",config)
        a = a + "\n-----------------------------------------------------------"
        return(a)
    else:
        print("No se puede conectar, revisa las configuraciones o que el OPPO este encendido o en reposo")
        sys.exit()

def get_mount_path(movie,server_data):

        movie = movie.replace(server_data["Emby_Path"],server_data["Oppo_Path"])
        movie = movie.replace('\\\\','\\')
        movie = movie.replace('\\','/')
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
        resultado={}
        resultado["Servidor"]=servidor
        resultado["Carpeta"]=carpeta
        resultado["Fichero"]=fichero
        return(resultado)
 
def test_mount_path(config,servidor,carpeta):
    sendnotifyremote(config["Oppo_IP"])
    #print("Conectando con el OPPO")
    result=check_socket(config)
    if result==0:
        response_data6a = getmainfirmwareversion(config)
        response_data6c = getdevicelist(config)
        response_data6b = getsetupmenu(config)
        response_data6c = OppoSignin(config)
        response_data6d = getdevicelist(config)
        response_data6e = getglobalinfo(config)
        response_data6f = getdevicelist(config)
        response_data_on = sendremotekey("EJT",config)
        time.sleep(1)
        #print("Solicitando montar ruta al OPPO")
        response_data6b = getsetupmenu(config)
        while response_data6f.find('devicelist":[]') > 0:
              time.sleep(1)
              response_data6f = getdevicelist(config)
              response_data_on = sendremotekey("QPW",config)
        response_login = LoginSambaWithOutID(config,servidor)
        time.sleep(5)
        #print(servidor)
        #print(carpeta)
        response_mount = mountSharedFolder(servidor,carpeta,'','',config)
        response=json.loads(response_mount)
        #print(response)
        if config["Autoscript"]==True:
            result=umountSharedFolder(config)
        if response["success"]==True:
            a = "OK"
        else:
            a = "FAILURE"
            
        return(a)
    else:
        print("No se puede conectar, revisa las configuraciones o que el OPPO este encendido o en reposo")
        sys.exit()
def set_mediafiles(config,mediafolder):
        #copyfile(src, dst)
        cwd = os.path.dirname(os.path.abspath(__file__))
        if sys.platform.startswith('win'):
            separador="\\"
        else:
            separador="/"
        directory=cwd + separador + "ejemplos" + separador + mediafolder + separador
        os.chdir(directory)
        if config["DebugLevel"]==2:
                print (directory)
        dirs = os.listdir(".")
        encontrado=False
        while encontrado==False:
            index=0
            for x in dirs:
                if os.path.isdir(x):
                    index=index+1
                    print (str(index) + ". " + x)
            index = index +1
            print(str(index) + ". Salir ")
            print("-----------------------------------------------------------")
            sel_index=input("Indique el numero que corresponde con el modelo de " + mediafolder +": ")
            edit_index=index
            try:
                edit_index=int(sel_index)
            except:
                print("Introduzca el numero de Index")
            if edit_index>index+1:
                print("Introduzca el numero de Index")
            else:
                if edit_index!=index:
                    index2=0
                    for x in dirs:
                        if os.path.isdir(x):
                            index2=index2+1
                            if index2==edit_index:
                                sel_dir=x
                    result=get_confirmation('Ha seleccionado ' + sel_dir + ' es correcta? (s/n)')
                    if result==0:
                        encontrado=True
                        src=directory + separador + sel_dir + separador
                        dest=cwd + separador + 'lib' + separador
                        os.chdir(src)
                        #copyfile(src, dst)
                        src_files = os.listdir('.')
                        for file_name in src_files:
                            full_file_name = os.path.join(src, file_name)
                            if os.path.isfile(full_file_name):
                                if config["DebugLevel"]==2:
                                        print ('Copiando ' + full_file_name + ' a ' + dest)
                                shutil.copy(full_file_name, dest)
                        return(0)
                    else:
                        encontrado=False
                else:
                    encontrado=True
                    return(1)
        
def config_TV(config):
    if config["resume_on"]!='TV_AS' and config["resume_on"]!='TV_ADV':
        print("-----------------------------------------------------------")
        tv_int=get_confirmation("Desea activar la integracion con la TV? (s/n)")
        if tv_int==0:
            config["TV"]="True"
            res=set_mediafiles(config,'TV')
            if res==0:
                    config["resume_on"]='TV_'+config["actual_menu"]
                    save_config(config_file, config)
                    restart()
                    exit()
            else:
                    config["TV"]="False"
                    config["resume_on"]=''
        else:
            config["TV"]="False"
            config["resume_on"]=''
    else:
        config["TV"]="True"
        tv_config(config)
        config["resume_on"]=''
        save_config(config_file, config)
        
def config_AV(config):
    if config["resume_on"]!='AV_AS' and config["resume_on"]!='AV_ADV':
        print("-----------------------------------------------------------")
        av_int=get_confirmation("Desea activar la integracion con la AV? (s/n)")
        if av_int==0:
            config["AV"]="True"
            res=set_mediafiles(config,'AV')
            if res==0:         
                    config["resume_on"]='AV_'+config["actual_menu"]
                    save_config(config_file, config)
                    restart()
                    exit()
            else:
                    config["AV"]="False"     
        else:
            config["AV"]="False"
    else:
        config["AV"]="True"
        av_config(config)
        av_always_on=get_confirmation("Desea apagar/suspender el AV al terminar la reproduccion? (s/n)")
        if av_always_on==0:
           config["AV_Always_ON"]=False
        else:
           config["AV_Always_ON"]=True
        config["resume_on"]=''
        save_config(config_file, config)

def config_others(config):
    print("-----------------------------------------------------------")
    print("A continuacion se solicitaran los parametros extra, dejarlo en blanco y pulsar ENTER deja el parametro al valor actual")
    es_correcto=False
    while es_correcto==False:
        debuglevel=get_parametro_int("Introduzca el valor para DebugLevel, valor actual " + str(config["DebugLevel"]),config["DebugLevel"])
        if debuglevel>2:
            print('Elija un valor 0,1,2')
        else:
            a=input("Abra Emby en el dispositivo a monitorizar, presiene ENTER para continuar")
            device=select_device(config)
            monitoreddev=device["DeviceId"]
            print ("DebugLevel             : %s" % debuglevel)
            print ("MonitoredDevice        : %s" % monitoreddev)
            result=get_confirmation('Esta es la nueva configuracion, es correcta? (s/n)')
            if result==0:
                es_correcto=True
                config["MonitoredDevice"]=monitoreddev
                config["DebugLevel"]=debuglevel
            else:
                es_correcto=False
                
def test_emby(config):
    try:
        EmbySession=EmbyHttp(config)
        user_info = EmbySession.user_info
        if user_info["SessionInfo"]["Id"]!="":
            print("-----------------------------------------------------------")
            print("               Test Conexion Emby OK                  ")
            print("-----------------------------------------------------------")
            return("OK")
        else:
            print("-----------------------------------------------------------")
            print("               Test Conexion Emby NO OK               ")
            print("-----------------------------------------------------------")
            return("FAILED")
    except:
            print("-----------------------------------------------------------")
            print("               Test Conexion Emby NO OK               ")
            print("-----------------------------------------------------------")
            return("FAILED")

def test_oppo(config):
    result=check_socket(config)
    if result==0:
            print("-----------------------------------------------------------")
            print("               Test Conexion OPPO OK                  ")
            print("-----------------------------------------------------------")
            return("OK")
    else:
            print("-----------------------------------------------------------")
            print("               Test Conexion OPPO NO OK               ")
            print("-----------------------------------------------------------")
            return("FAILED")

def test_mounts(config):
    print("-----------------------------------------------------------")
    print("               Test Montaje Rutas                          ")
    print("-----------------------------------------------------------")
    for server in config["servers"]:
        rutas = get_mount_path(server["Emby_Path"] + "/test.mkv",server)
        result2 = test_mount_path(config,rutas["Servidor"],rutas["Carpeta"])
        print(' Montaje ruta ' + server["name"] + ' ' + result2 + ' - ' + server["Emby_Path"])    
        print("-----------------------------------------------------------")

def ver_configuracion(config):
        version=('Xnoppo Device Config Script V1.4')
        print (version)
        print ("Config File            : %s" % config_file)
        print ("Emby Server            : %s" % config["emby_server"])
        print ("User Name              : %s" % config["user_name"])
        print ("User Pass              : %s" % config["user_password"])
##        print ("Oppo User Name         : %s" % config["oppo_smb_user"])
##        print ("Oppo User Pass         : %s" % config["oppo_smb_pwd"])
        print ("Oppo IP                : %s" % config["Oppo_IP"])
        print ("Timeout_oppo_conection : %s" % config["timeout_oppo_conection"])
        print ("Timeout_oppo_playitem  : %s" % config["timeout_oppo_playitem"])
        print ("Oppo Always on         : %s" % config["Always_ON"])
        print ("Autostript             : %s" % config["Autoscript"])        
        server_list=config["servers"]
        print("Servers OPPO           :")
        print("-----------------------------------------------------------")
        for server in server_list:
            server_data = {}
            server_data["name"] = server["name"]
            server_data["Emby_Path"] = server["Emby_Path"]
            server_data["Oppo_Path"] = server["Oppo_Path"]
            print(" Server Name           : %s " % server_data["name"])
            print(" Emby Path             : %s " % server_data["Emby_Path"])
            print(" Oppo Path             : %s " % server_data["Oppo_Path"])
            print("-----------------------------------------------------------")
        print ("TV                     : %s" % config["TV"])
        print ("TV IP                  : %s" % config["TV_IP"])
        print ("TV KEY                 : %s" % config["TV_KEY"])
        print ("TV Device Name         : %s" % config["TV_DeviceName"])
        print ("Source                 : %s" % config["Source"])
        print ("AV                     : %s" % config["AV"])
        print ("AV_Ip                  : %s" % config["AV_Ip"])
        print ("AV_Input               : %s" % config["AV_Input"])
        print ("AV_Always_on           : %s" % config["AV_Always_ON"])
        print ("DebugLevel             : %s" % config["DebugLevel"])
        print ("MonitoredDevice        : %s" % config["MonitoredDevice"])
        print("-----------------------------------------------------------")
        print("Librerias              :")
        lib_list=config["Libraries"]
        index=0
        l1=0
        l2=0
        for lib in lib_list:
            l1=len(lib["Name"])
            if l1>l2:
                l2=l1
        for lib in lib_list:
            cadena = '{:2d} - {:' + str(l2) + 's}  {:12s}'
            if lib["Active"]==True:
                #print(str(index) + " - " + lib["Name"] + " - Activada")
                cadena = '{:2d} - {:' + str(l2) + 's}  {:12s}'
                print(cadena.format(index,lib["Name"],' - Activada'))
            else:
                #print(str(index) + " - " + lib["Name"] + " - Desactivada")
                #print('{:2d} - {:' + str(l2) + 's}  {:12s}'.format(index,lib["Name"],' - Desactivada'))
                print(cadena.format(index,lib["Name"],' - Desactivada'))
            index=index+1
        print("-----------------------------------------------------------")

def cargar_config(config_file):

        with open(config_file, 'r') as f:    
                config = json.load(f)
                #ver_configuracion(config)
        f.close
        ## new options default config values
        default = config.get("Autoscript", False)
        config["Autoscript"]=default
        ##
        return(config)

cwd = os.path.dirname(os.path.abspath(__file__))
if sys.platform.startswith('win'):
      separador="\\"
else:
      separador="/"
config_file=cwd + separador + "config.json"
config=cargar_config(config_file)
#config["reboot"]=True
salir=True
#try:
if salir:
    if config["resume_on"]=='TV_ADV':
        advanced_config(config)
        #exit()
    elif config["resume_on"]=='TV_AS':
        conf_assistant(config)
        #exit()
    elif config["resume_on"]=='AV_ADV':
        advanced_config(config)
        #exit()
    elif config["resume_on"]=='AV_AS':
        conf_assistant(config)
        #exit()
    else:
        #config["reboot"]=False
        salir=False
#except:
else:
    config["resume_on"]=''
result=0
while result!=4:
    config["actual_menu"]=""
    result=menu_principal()
    if result==1:
        conf_assistant(config)
    elif result==2:
        advanced_config(config)
    elif result==3:
        ver_configuracion(config)
    #config=cargar_config(config_file)

 

# FILE FOR WEBOS LG
# thanks to Srivatsan Iyer for library PyWebOSTV
# to use it install PyWebOSTV, instructions, license usage and so are here https://github.com/supersaiyanmode/PyWebOSTV
# Gracias a Srivatsan Iyer por la libreria PyWebOSTV
# para usarlo instalar PyWebOSTV, instrucciones, licencia de uso y demas estan en https://github.com/supersaiyanmode/PyWebOSTV
#
# Onkyo eISCP Control License
# The MIT License
#
# Copyright (c) 2010 Will Nowak
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from pywebostv.connection import *
from pywebostv.controls import *
import logging

def get_parametro2(texto,valor_actual):
    valor = input(texto+": ")
    if valor=="":
        valor=valor_actual
    return(valor)

def get_parametro_int2(texto,valor_actual):
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
                print('Introduzca un numero entero')
    return(result)

def get_confirmation2(texto):
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

def tv_config(config):

    es_correcto=False
    while es_correcto==False:
        print("A continuacion se solicitaran los parametros relativos al TV, dejarlo en blanco y pulsar ENTER deja el parametro al valor actual")
        tv_ip=get_parametro2("Introduzca el valor para la ip, valor actual " + config["TV_IP"],config["TV_IP"])
        print ("TV IP                     : %s" % tv_ip)
        result=get_confirmation2('Esta es la nueva configuracion, es correcta? (s/n)')
        if result==0:
            es_correcto=True
            config["TV_IP"]=tv_ip
    result=get_confirmation2('Desea obtener el KEY AUTH de su televisor? (s/n)')
    if result==0:
        a=input("Encienda su TV, presiene ENTER para continuar")
        store = {}
        client = WebOSClient(config["TV_IP"])
        try:
           client.connect()         
           for status in client.register(store):
               if status == WebOSClient.PROMPTED:
                   print("Por favor acepta la conexion en la TV")           
               elif status == WebOSClient.REGISTERED:
                  print("Registro correcto!")
           config["TV_KEY"]=store["client_key"]
        except:
           print("Error conexion")
    result3=get_confirmation2('Desea configurar la fuente de video para el xnoppo? (s/n)')
    if result3==0:
        if result==1:
            if config["TV_KEY"]=='':
                store = {}
            else :
                store = {'client_key': config["TV_KEY"] }
            client = WebOSClient(config["TV_IP"])
            try:
               client.connect()         
               for status in client.register(store):
                   if status == WebOSClient.PROMPTED:
                       print("Por favor acepta la conexion en la TV")           
                   elif status == WebOSClient.REGISTERED:
                      print("-----------------------------------------------------------")
                      config["TV_KEY"]=store["client_key"] 
            except:
               print("Error conexion")
        try:
                source_control = SourceControl(client)
                sources = source_control.list_sources()
                source_control.set_source(sources[config["Source"]])
                index=0
                print('Listado de las entradas disponibles:')
                for source in sources:
                    print ('Fuente indice: '+ str(index) + ' - Entrada: '+ str(source))
                    index=index+1
                source=index+1
                while source>index:
                    source=get_parametro_int2("Introduzca el valor para source, valor actual " + str(config["Source"]),config["Source"])
                    if source>index:
                        print("Elija una entrada valida")
                config["Source"]=source
        except:
                print("Error consultando el TV")

def tv_test(config):
    if config["TV_KEY"]=='':
        store = {}
    else :
        store = {'client_key': config["TV_KEY"] }
    #print(store)
    client = WebOSClient(config["TV_IP"])
    try:
       client.connect()
    except:
       print("-----------------------------------------------------------")
       print("               Test Conexion TV NO OK               ")
       print("-----------------------------------------------------------")
       return("Error conexion")
    for status in client.register(store):
        if status == WebOSClient.PROMPTED:
          print("Por favor acepta la conexion en la TV")
        elif status == WebOSClient.REGISTERED:
          print("Registro correcto!")
    source_control = SourceControl(client)
    sources = source_control.list_sources()
    #source_control.set_source(sources[config["Source"]])
    index=0
    for source in sources:
        if index==config["Source"]:
            print ('Fuente indice: '+ str(index) + ' Encontrada para la Entrada: '+ str(source))
        index=index+1
    print("-----------------------------------------------------------")
    print("               Test Conexion TV OK               ")
    print("-----------------------------------------------------------")
    return("OK")

def tv_change_hdmi(config):
    print(config["TV_KEY"])
    if config["TV_KEY"]=='':
        store = {}
    else :
        store = {'client_key': config["TV_KEY"] }
    print(store)
    client = WebOSClient(config["TV_IP"])
    try:
       client.connect()
    except:
       print("Error conexion")
       return("Error conexion")
    for status in client.register(store):
        if status == WebOSClient.PROMPTED:
          print("Por favor acepta la conexion en la TV")
          logging.info ("Por favor acepta la conexion en la TV")
        elif status == WebOSClient.REGISTERED:
          print("Registro correcto!")
          logging.info ("Registro correcto!")
    print(store)
    logging.info ('Copia la siguiente linea en el config.json, propiedad TV_KEY')
    logging.info (store["client_key"])
    source_control = SourceControl(client)
    sources = source_control.list_sources()
    app = ApplicationControl(client)
    currentapp=app.get_current()
    config["current_LG"]=currentapp
    source_control.set_source(sources[config["Source"]])
    index=0
    logging.info ('Listado de las entradas disponibles:')
    for source in sources:
        print ('Fuente indice: '+ str(index) + ' - Entrada: '+ str(source))
        logging.info ('Fuente indice: %s - Entrada: %s',str(index),str(source))
        index=index+1
    return("OK")

def tv_set_prev(config):
    print(config["TV_KEY"])
    if config["TV_KEY"]=='':
        store = {}
    else :
        store = {'client_key': config["TV_KEY"] }
    print(store)
    client = WebOSClient(config["TV_IP"])
    try:
        client.connect()
        for status in client.register(store):
            if status == WebOSClient.PROMPTED:
               print("Por favor acepta la conexion en la TV")
               logging.info ("Por favor acepta la conexion en la TV")
            elif status == WebOSClient.REGISTERED:
               print("Registro correcto!")
               logging.info ("Registro correcto!")
    except:
        print("Error conexion")
        return("Error conexion")
    app = ApplicationControl(client)
    apps = app.list_apps()                            # Returns a list of `Application` instances.
    for ap in apps:
         if ap["id"]==config["current_LG"]:
            print('Lanzamos ' + config["current_LG"])
            logging.info('Lanzamos %s',config["current_LG"])
            launch_info = app.launch(ap)
    return("OK")

def tv_test_conn(config):
    if config["TV_KEY"]=='':
        store = {}
    else :
        store = {'client_key': config["TV_KEY"] }
    client = WebOSClient(config["TV_IP"])
    try:
        client.connect()
        return('OK')
    except:
        return("FAILURE")

def get_tv_key(config):
    store = {}
    client = WebOSClient(config["TV_IP"])
    try:
        client.connect()
        for status in client.register(store):
            if status == WebOSClient.PROMPTED:
               print("Por favor acepta la conexion en la TV")
               logging.info ("Por favor acepta la conexion en la TV")
            elif status == WebOSClient.REGISTERED:
               print("Registro correcto!")
               logging.info ("Registro correcto!")
        config["TV_KEY"]=store["client_key"]
        return("OK")
    except:
        return("FAILURE")

def get_tv_sources(config):
    if config["TV_KEY"]=='':
        store = {}
    else :
        store = {'client_key': config["TV_KEY"] }
    client = WebOSClient(config["TV_IP"])
    try:
        client.connect()
        for status in client.register(store):
            if status == WebOSClient.PROMPTED:
               print("Por favor acepta la conexion en la TV")
               logging.info ("Por favor acepta la conexion en la TV")
            elif status == WebOSClient.REGISTERED:
               print("Registro correcto!")
               logging.info ("Registro correcto!")
    except:
            return("FAILURE")
            print("Error conexion")
    #try:
    if True:
            source_control = SourceControl(client)
            sources = source_control.list_sources()
            index=0
            source_list=[]
            for source in sources:
                tv_source={}
                tv_source["index"]=index
                tv_source["nombre"]=str(source)
                source_list.append(tv_source)
                print ('Fuente indice: '+ str(index) + ' - Entrada: '+ str(source))
                index=index+1
            config["TV_SOURCES"]=source_list
            return("OK")
    #except:
    else:
                print("Error consultando el TV")
                return("FAILURE")

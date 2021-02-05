# FILE FOR ONKYO
# thanks to miracle2k library onkyo-eiscp
# to use it install Onkyo eISCP Control, instructions, license usage and so are here https://github.com/miracle2k/onkyo-eiscp
# Gracias a miracle2k por la libreria onkyo-eiscp
# para usarlo instalar Onkyo eISCP Control, instrucciones, licencia de uso y demas estan en https://github.com/miracle2k/onkyo-eiscp
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

import eiscp
import logging
import time

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

def add_hdmi(id, name, param, hdmi_list):
    hdmi_list_tmp=hdmi_list
    hdmi_input={}
    hdmi_input["Id"]=id
    hdmi_input["Name"]=name
    hdmi_input["Param"]=param
    hdmi_list_tmp.append(hdmi_input)
    return(hdmi_list_tmp)

def get_hdmi_list(config):
    hdmi_intput_list=[]
    hdmi_intput_list=add_hdmi(1,"VIDEO1 VCR/DVR STB/DVR","SLI00",hdmi_intput_list)
    hdmi_intput_list=add_hdmi(2,"VIDEO2 CBL/SAT","SLI01",hdmi_intput_list)
    hdmi_intput_list=add_hdmi(3,"VIDEO3 GAME/TV GAME GAME1","SLI02",hdmi_intput_list)
    hdmi_intput_list=add_hdmi(4,"VIDEO4 AUX1(AUX)","SLI03",hdmi_intput_list)
    hdmi_intput_list=add_hdmi(5,"VIDEO5 AUX2","SLI04",hdmi_intput_list)
    hdmi_intput_list=add_hdmi(6,"VIDEO6 PC","SLI05",hdmi_intput_list)
    hdmi_intput_list=add_hdmi(7,"VIDEO7 ","SLI06",hdmi_intput_list)
##    hdmi_intput_list=add_hdmi(8,"EXTRA1","SLI07",hdmi_intput_list)
##    hdmi_intput_list=add_hdmi(9,"EXTRA2","SLI08",hdmi_intput_list)
##    hdmi_intput_list=add_hdmi(10,"EXTRA3","SLI09",hdmi_intput_list)
    hdmi_intput_list=add_hdmi(11,"DVD BD/DVD","SLI10",hdmi_intput_list)
    return(hdmi_intput_list)


def av_config(config):

    es_correcto=False
    while es_correcto==False:
        config['AV_Port']=23
        print("A continuacion se solicitaran los parametros relativos al AV, dejarlo en blanco y pulsar ENTER deja el parametro al valor actual")
        av_ip=get_parametro2("Introduzca el valor para la ip, valor actual " + config["AV_Ip"],config["AV_Ip"])
        hdmi_list=get_hdmi_list(config)
        encontrado=False
        param_hdmi=""
        param_name=""
        while encontrado==False:
            index=0
            print("Introduzca el numero de la entrada a seleccionar al repdroducir en el OPPO:")
            for hdmi in hdmi_list:
                print(str(index) + " - " + hdmi["Name"])
                index=index+1
            print(str(index) + " Salir ")
            print("-----------------------------------------------------------")
            lib_index=input("Numero de la entrada: ")
            edit_index=index
            try:
                edit_index=int(lib_index)
            except:
                print("Introduzca el numero de Index de la entrada hdmi")
            if edit_index>index+1:
                print("Introduzca el numero de Index de la entrada hdmi")
            else:
                if edit_index!=index:
                    param_hdmi=hdmi_list[edit_index]["Param"]
                    param_name=hdmi_list[edit_index]["Name"]
                    encontrado=True
                else:
                    encontrado=True
        print ("AV IP                     : %s" % av_ip)
        print ("AV HDMI                   : %s" % param_name)
        result=get_confirmation2('Esta es la nueva configuracion, es correcta? (s/n)')
        if result==0:
            es_correcto=True
            config["AV_Ip"]=av_ip
            config["AV_Input"]=param_hdmi
    
def av_test(config):
    try:
        receiver = eiscp.eISCP(config["AV_Ip"])
        onk_status = receiver.command('power query')
        print("-----------------------------------------------------------")
        print("               Test Conexion AV Onkyo OK               ")
        print("-----------------------------------------------------------")
        return("OK")
    except:
        print("-----------------------------------------------------------")
        print("               Test Conexion AV Onkyo NO OK               ")
        print("-----------------------------------------------------------")
        return("Error")
    
def av_check_power(config):
    logging.info('Onkyo Check AV POWER')
    try:
        receiver = eiscp.eISCP(config["AV_Ip"])
        onk_status = receiver.command('power query')
        logging.info('Onkyo Power Status: %s',onk_status[1])
        if onk_status[1]==('standby', 'off'):
           logging.info('Cambiamos a on')
           receiver.command('power on')
        receiver.disconnect()
        return("OK")
    except:
        return("Error")
   
def av_change_hdmi(config):
    logging.info('Onkyo change HDMI Input')
    try:
        receiver = eiscp.eISCP(config["AV_Ip"])
        receiver.raw(config["AV_Input"])
        receiver.disconnect()
        return("OK")
    except:
        return("Error en el cambio")

def av_power_off(config):
    logging.info('Llamada a av_power_off')
    try:
        receiver = eiscp.eISCP(config["AV_Ip"])
        onk_status = receiver.command('power query')
        logging.info('Onkyo Power Status: %s',onk_status[1])
        receiver.raw('PWR00')
        receiver.disconnect()
        return("OK")
    except:
        return("Error")
    return("OK")


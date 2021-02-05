# FILE FOR DENON
import logging
import subprocess
import telnetlib

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
    hdmi_intput_list=add_hdmi(1,"CD",'SICD\n',hdmi_intput_list)
    hdmi_intput_list=add_hdmi(2,"DVD",'SIDVD\n',hdmi_intput_list)
    hdmi_intput_list=add_hdmi(3,"Blu-ray (BD)",'SIBD\n',hdmi_intput_list)
    hdmi_intput_list=add_hdmi(4,"TV AUDIO(TV)",'SITV\n',hdmi_intput_list)
    hdmi_intput_list=add_hdmi(5,"CBL/SAT",'SISAT/CBL\n',hdmi_intput_list)
    hdmi_intput_list=add_hdmi(6,"MEDIA PLAYER",'SIMPLAY\n',hdmi_intput_list)
    hdmi_intput_list=add_hdmi(7,"GAME",'GAME\n',hdmi_intput_list)
    
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
    print("-----------------------------------------------------------")
    print("               Test AV Dummy OK               ")
    print("-----------------------------------------------------------")

def av_check_power(config):
    logging.info('Llamada a av_check_power')
    host = config["AV_Ip"]
    port = config['AV_Port']

    with telnetlib.Telnet(host, port) as session:
        session.write(b"ZMON\n")
        session.write(b"ls\n")
        session.write(b"exit\n")
    return("OK")
    
def av_change_hdmi(config):
    logging.info('Llamada a av_change_hdmi')
    host = config["AV_Ip"]
    port = config['AV_Port']
    bsend = config["AV_Input"].encode()
    with telnetlib.Telnet(host, port) as session:
        session.write(bsend)
        session.write(b"ls\n")
        session.write(b"exit\n")
    return("OK")

def av_power_off(config):

    logging.info('Llamada a av_power_off')
    host = config["AV_Ip"]
    port = config['AV_Port']
    with telnetlib.Telnet(host, port) as session:
        session.write(b"ZMOFF\n")
        session.write(b"ls\n")
        session.write(b"exit\n")
    return("OK")

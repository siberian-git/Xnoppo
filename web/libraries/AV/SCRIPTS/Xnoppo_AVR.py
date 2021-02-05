# FILE FOR AV
import logging
import subprocess

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



def av_config(config):
    print('Configurador de para ejecucion de comamdos sh al AV')
    es_correcto=False
    try:
        av_cmd_pow_on=config["AV_CMD_POW_ON"]
    except:
        av_cmd_pow_on=""
    try:
        av_cmd_change_hdmi=config["AV_CMD_CHANGE_HDMI"]
    except:
        av_cmd_change_hdmi=""
    try:
        av_cmd_pow_off=config["AV_CMD_POW_OFF"]
    except:
        av_cmd_pow_off=""
    while es_correcto==False:
        print("Configurador de para ejecucion de comamdos sh al AV, dejarlo en blanco y pulsar ENTER deja el parametro al valor actual")
        av_cmd_pow_on=get_parametro2("Introduzca el comando para encender el AV" + av_cmd_pow_on,av_cmd_pow_on)
        av_cmd_change_hdmi=get_parametro2("Introduzca el comando para cambiar de hdmi" + av_cmd_change_hdmi,av_cmd_change_hdmi)
        av_cmd_pow_off=get_parametro2("Introduzca el comando para apagar/suspender el AV " + av_cmd_pow_off,av_cmd_pow_off)
        print ("AV_CMD_POW_ON               : %s" % av_cmd_pow_on)
        print ("AV_CMD_CHANGE_HDMI          : %s" % av_cmd_change_hdmi)
        print ("AV_CMD_POW_OFF              : %s" % av_cmd_pow_off)
        result=get_confirmation2('Esta es la nueva configuracion, es correcta? (s/n)')
        if result==0:
            es_correcto=True
            config["AV_CMD_POW_ON"]=av_cmd_pow_on
            config["AV_CMD_CHANGE_HDMI"]=av_cmd_change_hdmi
            config["AV_CMD_POW_OFF"]=av_cmd_pow_off

def av_test(config):
    print("-----------------------------------------------------------")
    print("               Test AV Dummy OK               ")
    print("-----------------------------------------------------------")

def av_check_power(config):
    logging.info('Llamada a av_check_power')
    result = subprocess.Popen(config["AV_CMD_POW_ON"])
#    result = subprocess.call(config["AV_CMD_POW_ON"])
    return("OK")
    
def av_change_hdmi(config):
    logging.info('Llamada a av_change_hdmi')
    result = subprocess.Popen(config["AV_CMD_CHANGE_HDMI"])
#    result = subprocess.call(config["AV_CMD_CHANGE_HDMI"])
    return("OK")

def av_power_off(config):
    logging.info('Llamada a av_power_off')
    result = subprocess.Popen(config["AV_CMD_POW_OFF"])
#    result = subprocess.call(config["AV_CMD_POW_OFF"])
    return("OK")

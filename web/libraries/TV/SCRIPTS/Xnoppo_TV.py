# FILE FOR TV
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



def tv_config(config):
    print('Configurador de para ejecucion de comamdos sh al TV')


def tv_test(config):
    print("-----------------------------------------------------------")
    print("               Test TV Dummy OK               ")
    print("-----------------------------------------------------------")

def tv_change_hdmi(config):
    logging.info('Llamada a tv_change_hdmi')
    try:
        result = subprocess.Popen(config["TV_script_init"])
#    result = subprocess.call(config["AV_CMD_POW_ON"])
        return("OK")
    except:
        return("FAILURE")
def tv_set_prev(config):
    logging.info('Llamada a tv_set_prev')
    try:
        result = subprocess.Popen(config["TV_script_end"])
#    result = subprocess.call(config["AV_CMD_CHANGE_HDMI"])
        return("OK")
    except:
        return("FAILURE")


# FILE FOR AV
import logging

def av_config(config):
    print('Este es el fichero estandar de AV, si dispone de uno para su AV copielo en lib con el nombre Xnoppo_AVR.py')

def av_test(config):
    print("-----------------------------------------------------------")
    print("               Test AV Dummy OK               ")
    print("-----------------------------------------------------------")

def av_check_power(config):
    logging.info('Llamada a av_check_power')
    return("OK")
    
def av_change_hdmi(config):
    logging.info('Llamada a av_change_hdmi')
    return("OK")

def av_power_off(config):
    logging.info('Llamada a av_power_off')
    return("OK")

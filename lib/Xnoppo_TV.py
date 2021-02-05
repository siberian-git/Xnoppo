# FILE FOR TV

import logging


def tv_config(config):
    print('Este es el fichero estandar de TV, si dispone de uno para su TV copielo en lib con el nombre Xnoppo_TV.py')

def tv_test(config):

    print("-----------------------------------------------------------")
    print("               Test TV DUMMY OK               ")
    print("-----------------------------------------------------------")
    
def tv_change_hdmi(config):
    logging.info ('Llamada a tv_change_hdmi')
    return("OK")

def tv_set_emby(config):
    logging.info('Llamada a tv_set_emby')
    return("OK")


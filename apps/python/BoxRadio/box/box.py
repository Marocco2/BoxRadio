import ac
import traceback
import os

try:
    import ctypes.wintypes
except:
    ac.log('BoxRadio: error loading ctypes.wintypes: ' + traceback.format_exc())
    raise

from ctypes.wintypes import MAX_PATH

# TODO: read from config file for filters | IMPORTS
from os.path import dirname, realpath
# import configparser

import functools
import threading


def async(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
        return t

    return wrapper


try:
    from box_lib import requests
except Exception as e:
    ac.log('BoxRadio: error loading requests: ' + traceback.format_exc())
    raise


# A useful push notification if I need send some news
def getNotificationFrom(telegram_api_getUpdates):
    r = requests.get(telegram_api_getUpdates)
    message = r.json()
    var_notify = message["result"][-1]["message"]["text"]
    #ac.log('BoxRadio: Notification from Telegram:' + var_notify)
    return var_notify

# @async
# def getNewUpdate(check_link, download_link):
#    try:
#
#    except:

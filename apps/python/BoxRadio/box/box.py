import ac
import traceback
import os

try:
    import ctypes.wintypes
except:
    ac.log('BOX: error loading ctypes.wintypes: ' + traceback.format_exc())
    raise

from ctypes.wintypes import MAX_PATH

# TODO: read from config file for filters | IMPORTS
from os.path import dirname, realpath
# import configparser

import functools
import threading
import zipfile

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
    ac.log('BOX: error loading requests: ' + traceback.format_exc())
    raise


# A useful push notification via Telegram if I need send some news
def getNotificationFrom(telegram_api_getUpdates):
    r = requests.get(telegram_api_getUpdates)
    message = r.json()
    var_notify = message["result"][-1]["message"]["text"]
    ac.log('BOX: Notification from Telegram: ' + var_notify)
    return var_notify

#A new functions to automatize app updates for AC 
def getNewUpdate(check_link, download_link):
    try:
        r = requests.get(check_link)
        with open('version.txt', 'r') as g:
            version = g.read()
            g.close()
        if r.json() != version:  # Check if server version and client version is the same
            try:
                local_filename = download_link.split('/')[-1]
                # NOTE the stream=True parameter
                r = requests.get(download_link, stream=True)
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
                            # f.flush() commented by recommendation from J.F.Sebastian
                try:
                    with zipfile.ZipFile(local_filename, "r") as z:
                        z.extractall(os.path.join(os.path.dirname(__file__), "temp"))  # Extracting files
                    Update_Status = "New update is installed. Restart AC"
                    return Update_Status
                except:
                    Update_Status = "Error extracting files"
                    return Update_Status
            except:
                Update_Status = "Error downloading new update"
                ac.log('BOX: error downloading new update: ' + traceback.format_exc())
                return Update_Status
        else:
            Update_Status = "No new update"
            ac.log('BOX: ' + Update_Status)
            return Update_Status
    except:
        Update_Status = "Error checking new update"
        ac.log('BOX: error checking new update: ' + traceback.format_exc())
        return Update_Status

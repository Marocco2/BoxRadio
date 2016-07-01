##############################################################
# BoxRadio Ver. 1.0
#
#
#
# Thanks to Paolo Wallner, NAGP MadMac and AdderSwim
#
#
# To activate create a folder with the same name as this file
# in apps/python. Ex apps/python/BoxRadio
# Then copy this file inside it and launch AC
#############################################################
import sys
import os
import platform

if platform.architecture()[0] == "64bit":
    sysdir = "stdlib64"
else:
    sysdir = "stdlib"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "box", sysdir))
os.environ['PATH'] = os.environ['PATH'] + ";."

import ac
import acsys
import datetime
import configparser
import subprocess
import shutil
import codecs
import traceback
import ctypes
import threading

importError = False

try:
    from box import box
except:
    ac.log('BoxRadio: error loading box module: ' + traceback.format_exc())
    importError = True
try:
    from box import sim_info
except:
    ac.log('BoxRadio: error loading sim_info module: ' + traceback.format_exc())
    importError = True

try:
    from box import win32con
except:
    ac.log('BoxRadio: error loading win32con module: ' + traceback.format_exc())
    importError = True

SetCursorPos = ctypes.windll.user32.SetCursorPos
mouse_event = ctypes.windll.user32.mouse_event

# Check My Documments location
from ctypes import wintypes

CSIDL_PERSONAL = 5  # My Documents
SHGFP_TYPE_CURRENT = 0  # Get default value
buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
ac.log('BoxRadio: Log path: ' + buf.value)

# Check AC Resolution
if os.path.isfile(buf.value + '/Assetto Corsa/cfg/video.ini'):
    videoconfig = configparser.ConfigParser()
    videoconfig.read(buf.value + '/Assetto Corsa/cfg/video.ini')
    Resolution = int(videoconfig['VIDEO']['WIDTH'])
    ResolutionHeight = int(videoconfig['VIDEO']['HEIGHT'])
    FullScreen = videoconfig.getboolean('VIDEO', 'FULLSCREEN')
    ac.log('BoxRadio: Resolution on video.ini: ' + str(Resolution))
    ac.log('BoxRadio: FullScreen on video.ini: ' + str(FullScreen))
else:
    Resolution = ctypes.windll.user32.GetSystemMetrics(0)
    ResolutionHeight = ctypes.windll.user32.GetSystemMetrics(1)
    ac.log('BoxRadio: Resolution on SystemMetrics: ' + str(Resolution))
    FullScreen = True

# Read Tyre Compounds
OptionLabel = ['', '', '', '', '', '']
i = 1

superhot = subprocess.Popen(["apps\python\BoxRadio\JoyToKey.exe"])

now = (datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() - 120
ac.log('BoxRadio: Current time: ' + str(now))

filetime = 0
logfound = 'No'

if os.path.isfile(buf.value + '\Assetto Corsa\logs\log.txt'):
    filetime = os.path.getmtime(buf.value + '\Assetto Corsa\logs\log.txt')
    logfound = 'Date'
    ac.log('BoxRadio: Log file time: ' + str(filetime))

if filetime >= now:
    shutil.copyfile(buf.value + '\Assetto Corsa\logs\log.txt', 'apps\python\BoxRadio\AClog.txt')
    ac.log('BoxRadio: Log file copy Ok')
    log = codecs.open('apps\python\BoxRadio\AClog.txt', 'r', encoding='ascii', errors='ignore')
    ac.log('BoxRadio: Log file Decode Ok')
    logfound = 'Ok'

    for TyreLine in log:
        if TyreLine[:14] == 'TYRE COMPOUND:':
            TyreShort = TyreLine[-5:-3]
            OptionLabel[i] = TyreShort.strip('(')
            ac.log('BoxRadio: ' + TyreLine[:-1])
            i = i + 1

        elif TyreLine[:19] == 'Loading engine file':
            break

    ac.log('BoxRadio: End of tyre search on log file')
    log.close()
    os.remove('apps\python\BoxRadio\AClog.txt')
else:
    ac.log('BoxRadio: ks_tyres.ini method')
    with open('server\manager\ks_tyres.ini', 'r') as g:
        content = g.read()
        g.close()

    with open('apps\python\BoxRadio\ks_tyres_adj.ini', 'w') as j:
        j.write(';')
        j.write(content)
        j.close()

    config = configparser.ConfigParser()
    config.read('apps\python\BoxRadio\ks_tyres_adj.ini')

    if ac.getCarName(0) in config:
        for key in config[ac.getCarName(0)]:
            OptionLabel[i] = key
            ac.log('BoxRadio: Tyre short: ' + key)
            i = i + 1
        ac.log('BoxRadio: Tyres obtained from ks_tyres.ini')
    else:
        OptionLabel = ['', 'T1', 'T2', 'T3', 'T4', 'T5']
        ac.log('BoxRadio: Mod tyres not found on ks_tyres.ini')

    os.remove('apps\python\BoxRadio\ks_tyres_adj.ini')

ac.log('BoxRadio: Found AC log location: ' + logfound)

# Read Config File
configini = configparser.ConfigParser()
configini.read('apps\python\BoxRadio\BoxRadio.ini')
FuelOption = configini.getboolean('FUEL', 'ADD')
UiSize = float(configini['UI']['sizemultiplier'])
if UiSize < 1:
    UiSize = 1
elif UiSize > 3:
    UiSize = 3
if Resolution == ctypes.windll.user32.GetSystemMetrics(0) or ResolutionHeight == ctypes.windll.user32.GetSystemMetrics(
        1):
    leftbordersize = 0
    topbordersize = 0
else:
    leftbordersize = float(configini['WINDOWMODE']['leftbordersize'])
    topbordersize = float(configini['WINDOWMODE']['topbordersize'])

FullScreenOverhide = configini.getboolean('WINDOWMODE', 'fullscreenoverhide')
if FullScreenOverhide == 1:
    FullScreen = True
    ac.log('BoxRadio: Full Screen Overhide')

# Variables initial value
Notify = ""
Status = "Checking internet connection..."
Tirecoord = int(Resolution / 2 - 247)
Fuelcoord = int(Resolution / 2 + 100)
FuelAdd = 0
FuelMax = 0
FuelIn = 0
u = 0
Suspensioncoord = int(Resolution / 2 + 140)
Bodycoord = int(Resolution / 2 + 140)
Enginecoord = int(Resolution / 2 + 140)
Car = "lotus_exos_125_s1"
Tires = "NoChange"
Gas = "0"
FixBody = "no"
FixEngine = "no"
FixSuspen = "no"
DoPit = 1
InPit = 0
Preset = 1
adjust_x = 0
adjust_y = 0
PitX, PitY, PitZ = 0, 0, 0  # Pitbox co-ords
AppInitialised = False  # bool so can set app info on first run
listen_active = True


def acMain(ac_version):
    global Status
    global appWindow, FuelSelection, FuelLabel, NoChange, Option1
    global Option2, Option3, Option4, Option5, Body, Engine, Suspension, Fill, FuelOption, NotificationLabel, StatusLabel, Status
    global Preset1, Preset2, Preset3, Preset4
    #
    appWindow = ac.newApp("BoxRadio")
    ac.setSize(appWindow, 180 * UiSize, 220 * UiSize)
    ac.setTitle(appWindow, "BoxRadio")
    ac.setBackgroundOpacity(appWindow, 0.5)
    ac.drawBorder(appWindow, 0)
    #
    FuelSelection = ac.addSpinner(appWindow, "")
    ac.setPosition(FuelSelection, 10 * UiSize, 99 * UiSize)
    ac.setSize(FuelSelection, 80 * UiSize, 18 * UiSize)
    ac.setFontColor(FuelSelection, 1, 1, 1, 1)
    ac.setFontSize(FuelSelection, 12 * UiSize)
    ac.setRange(FuelSelection, 0, int(FuelMax))
    ac.setStep(FuelSelection, 1)
    ac.addOnValueChangeListener(FuelSelection, FuelEvent)
    #
    if FuelOption == True:
        FuelLabel = ac.addLabel(appWindow, "Fuel Add")
        ac.setPosition(FuelLabel, 10 * UiSize, 80 * UiSize)
        ac.setFontColor(FuelLabel, 1, 1, 1, 1)
        ac.setFontSize(FuelLabel, 13 * UiSize)
    else:
        FuelLabel = ac.addLabel(appWindow, "Fuel Total")
        ac.setPosition(FuelLabel, 10 * UiSize, 80 * UiSize)
        ac.setFontColor(FuelLabel, 1, 1, 1, 1)
        ac.setFontSize(FuelLabel, 13 * UiSize)
    #
    Fill = ac.addButton(appWindow, "")
    ac.setBackgroundOpacity(Fill, 0)
    ac.drawBorder(Fill, 0)
    ac.setSize(Fill, 20 * UiSize, 20 * UiSize)
    ac.setPosition(Fill, 95 * UiSize, 98 * UiSize)
    ac.setBackgroundTexture(Fill, "apps/python/BoxRadio/img/fuel_fill_OFF.png")
    ac.addOnClickedListener(Fill, FillEvent)
    #
    NoChange = ac.addButton(appWindow, "")
    ac.setBackgroundOpacity(NoChange, 0)
    ac.drawBorder(NoChange, 0)
    ac.setSize(NoChange, 25 * UiSize, 25 * UiSize)
    ac.setPosition(NoChange, 125 * UiSize, 27 * UiSize)
    ac.setBackgroundTexture(NoChange, "content/gui/pitstop/tyre_no_change_ON.png")
    ac.addOnClickedListener(NoChange, NoChangeEvent)
    #
    Nochangelabel = ac.addLabel(appWindow, "No")
    ac.setPosition(Nochangelabel, 153 * UiSize, 31 * UiSize)
    ac.setFontColor(Nochangelabel, 1, 1, 1, 1)
    ac.setFontSize(Nochangelabel, 12 * UiSize)
    #
    Option1 = ac.addButton(appWindow, "")
    ac.setBackgroundOpacity(Option1, 0)
    ac.drawBorder(Option1, 0)
    ac.setSize(Option1, 25 * UiSize, 25 * UiSize)
    ac.setPosition(Option1, 125 * UiSize, 52 * UiSize)
    ac.setBackgroundTexture(Option1, "content/gui/pitstop/tyre_1_OFF.png")
    ac.addOnClickedListener(Option1, Option1Event)
    if OptionLabel[1] == '':
        ac.setVisible(Option1, 0)
    #
    Option1label = ac.addLabel(appWindow, OptionLabel[1].upper())
    ac.setPosition(Option1label, 153 * UiSize, 56 * UiSize)
    ac.setFontColor(Option1label, 1, 1, 1, 1)
    ac.setFontSize(Option1label, 13 * UiSize)
    #
    Option2 = ac.addButton(appWindow, "")
    ac.setBackgroundOpacity(Option2, 0)
    ac.drawBorder(Option2, 0)
    ac.setSize(Option2, 25 * UiSize, 25 * UiSize)
    ac.setPosition(Option2, 125 * UiSize, 77 * UiSize)
    ac.setBackgroundTexture(Option2, "content/gui/pitstop/tyre_2_OFF.png")
    ac.addOnClickedListener(Option2, Option2Event)
    if OptionLabel[2] == '':
        ac.setVisible(Option2, 0)
    #
    Option2label = ac.addLabel(appWindow, OptionLabel[2].upper())
    ac.setPosition(Option2label, 153 * UiSize, 81 * UiSize)
    ac.setFontColor(Option2label, 1, 1, 1, 1)
    ac.setFontSize(Option2label, 13 * UiSize)
    #
    Option3 = ac.addButton(appWindow, "")
    ac.setBackgroundOpacity(Option3, 0)
    ac.drawBorder(Option3, 0)
    ac.setSize(Option3, 25 * UiSize, 25 * UiSize)
    ac.setPosition(Option3, 125 * UiSize, 102 * UiSize)
    ac.setBackgroundTexture(Option3, "content/gui/pitstop/tyre_3_OFF.png")
    ac.addOnClickedListener(Option3, Option3Event)
    if OptionLabel[3] == '':
        ac.setVisible(Option3, 0)
    #
    Option3label = ac.addLabel(appWindow, OptionLabel[3].upper())
    ac.setPosition(Option3label, 153 * UiSize, 106 * UiSize)
    ac.setFontColor(Option3label, 1, 1, 1, 1)
    ac.setFontSize(Option3label, 13 * UiSize)
    #
    Option4 = ac.addButton(appWindow, "")
    ac.setBackgroundOpacity(Option4, 0)
    ac.drawBorder(Option4, 0)
    ac.setSize(Option4, 25 * UiSize, 25 * UiSize)
    ac.setPosition(Option4, 125 * UiSize, 127 * UiSize)
    ac.setBackgroundTexture(Option4, "content/gui/pitstop/tyre_4_OFF.png")
    ac.addOnClickedListener(Option4, Option4Event)
    if OptionLabel[4] == '':
        ac.setVisible(Option4, 0)
    #
    Option4label = ac.addLabel(appWindow, OptionLabel[4].upper())
    ac.setPosition(Option4label, 153 * UiSize, 131 * UiSize)
    ac.setFontColor(Option4label, 1, 1, 1, 1)
    ac.setFontSize(Option4label, 13 * UiSize)
    #
    Option5 = ac.addButton(appWindow, "")
    ac.setBackgroundOpacity(Option5, 0)
    ac.drawBorder(Option5, 0)
    ac.setSize(Option5, 25 * UiSize, 25 * UiSize)
    ac.setPosition(Option5, 125 * UiSize, 152 * UiSize)
    ac.setBackgroundTexture(Option5, "content/gui/pitstop/tyre_5_OFF.png")
    ac.addOnClickedListener(Option5, Option5Event)
    if OptionLabel[5] == '':
        ac.setVisible(Option5, 0)
    #
    Option5label = ac.addLabel(appWindow, OptionLabel[5].upper())
    ac.setPosition(Option5label, 153 * UiSize, 156 * UiSize)
    ac.setFontColor(Option5label, 1, 1, 1, 1)
    ac.setFontSize(Option5label, 13 * UiSize)
    #
    Suspension = ac.addButton(appWindow, "")
    ac.setBackgroundOpacity(Suspension, 0)
    ac.drawBorder(Suspension, 0)
    ac.setSize(Suspension, 30 * UiSize, 30 * UiSize)
    ac.setPosition(Suspension, 10 * UiSize, 136 * UiSize)
    ac.setBackgroundTexture(Suspension, "content/gui/pitstop/repair_sus_OFF.png")
    ac.addOnClickedListener(Suspension, SuspensionEvent)
    #
    Body = ac.addButton(appWindow, "")
    ac.setBackgroundOpacity(Body, 0)
    ac.drawBorder(Body, 0)
    ac.setSize(Body, 30 * UiSize, 30 * UiSize)
    ac.setPosition(Body, 48 * UiSize, 136 * UiSize)
    ac.setBackgroundTexture(Body, "content/gui/pitstop/repair_body_OFF.png")
    ac.addOnClickedListener(Body, BodyEvent)
    #
    Engine = ac.addButton(appWindow, "")
    ac.setBackgroundOpacity(Engine, 0)
    ac.drawBorder(Engine, 0)
    ac.setSize(Engine, 30 * UiSize, 30 * UiSize)
    ac.setPosition(Engine, 85 * UiSize, 136 * UiSize)
    ac.setBackgroundTexture(Engine, "content/gui/pitstop/repair_engine_OFF.png")
    ac.addOnClickedListener(Engine, EngineEvent)
    #
    Preset1 = ac.addCheckBox(appWindow, "")
    ac.setPosition(Preset1, 10 * UiSize, 50 * UiSize)
    ac.setSize(Preset1, 20 * UiSize, 20 * UiSize)
    ac.drawBorder(Preset1, 1)
    ac.addOnCheckBoxChanged(Preset1, Preset1Event)
    #
    Preset2 = ac.addCheckBox(appWindow, "")
    ac.setPosition(Preset2, 37 * UiSize, 50 * UiSize)
    ac.setSize(Preset2, 20 * UiSize, 20 * UiSize)
    ac.drawBorder(Preset2, 1)
    ac.addOnCheckBoxChanged(Preset2, Preset2Event)
    #
    Preset3 = ac.addCheckBox(appWindow, "")
    ac.setPosition(Preset3, 65 * UiSize, 50 * UiSize)
    ac.setSize(Preset3, 20 * UiSize, 20 * UiSize)
    ac.drawBorder(Preset3, 1)
    ac.addOnCheckBoxChanged(Preset3, Preset3Event)
    #
    Preset4 = ac.addCheckBox(appWindow, "")
    ac.setPosition(Preset4, 93 * UiSize, 50 * UiSize)
    ac.setSize(Preset4, 20 * UiSize, 20 * UiSize)
    ac.drawBorder(Preset4, 1)
    ac.addOnCheckBoxChanged(Preset4, Preset4Event)
    #
    PresetLabel = ac.addLabel(appWindow, "Preset")
    ac.setPosition(PresetLabel, 10 * UiSize, 30 * UiSize)
    ac.setFontColor(PresetLabel, 1, 1, 1, 1)
    ac.setFontSize(PresetLabel, 13 * UiSize)
    #
    Preset1Label = ac.addLabel(appWindow, "1")
    ac.setPosition(Preset1Label, 16 * UiSize, 50 * UiSize)
    ac.setFontColor(Preset1Label, 0, 0, 0, 1)
    ac.setFontSize(Preset1Label, 15 * UiSize)
    #
    Preset2Label = ac.addLabel(appWindow, "2")
    ac.setPosition(Preset2Label, 43 * UiSize, 50 * UiSize)
    ac.setFontColor(Preset2Label, 0, 0, 0, 1)
    ac.setFontSize(Preset2Label, 15 * UiSize)
    #
    Preset3Label = ac.addLabel(appWindow, "3")
    ac.setPosition(Preset3Label, 71 * UiSize, 50 * UiSize)
    ac.setFontColor(Preset3Label, 0, 0, 0, 1)
    ac.setFontSize(Preset3Label, 15 * UiSize)
    #
    Preset4Label = ac.addLabel(appWindow, "4")
    ac.setPosition(Preset4Label, 99 * UiSize, 50 * UiSize)
    ac.setFontColor(Preset4Label, 0, 0, 0, 1)
    ac.setFontSize(Preset4Label, 15 * UiSize)
    #
    StatusLabel = ac.addLabel(appWindow, Status)
    ac.setPosition(StatusLabel, 10 * UiSize, 175 * UiSize)
    ac.setFontColor(StatusLabel, 1, 1, 1, 1)
    ac.setFontSize(StatusLabel, 10 * UiSize)
    #
    NotificationLabel = ac.addLabel(appWindow, Notify)
    ac.setPosition(NotificationLabel, 10 * UiSize, 195 * UiSize)
    ac.setFontColor(NotificationLabel, 1, 1, 1, 1)
    ac.setFontSize(NotificationLabel, 9 * UiSize)
    #
    return "BoxRadio"


def FuelEvent(x):
    global Fill, FuelSelection, Gas, FuelAdd, FuelMax, Resolution

    Gas = int(ac.getValue(FuelSelection))

    if Gas == FuelMax:
        ac.setBackgroundTexture(Fill, "apps/python/BoxRadio/img/fuel_fill_ON.png")
    else:
        ac.setBackgroundTexture(Fill, "apps/python/BoxRadio/img/fuel_fill_OFF.png")


def FillEvent(name, state):
    global FuelSelection, FuelMax

    ac.setValue(FuelSelection, int(FuelMax))
    FuelEvent(1)


def NoChangeEvent(name, state):
    global NoChange, Tires, Tirecoord, Resolution

    Tires = "NoChange"
    Tirecoord = int(Resolution / 2 - 247)
    ac.setBackgroundTexture(NoChange, "content/gui/pitstop/tyre_no_change_ON.png")
    ac.setBackgroundTexture(Option1, "content/gui/pitstop/tyre_1_OFF.png")
    ac.setBackgroundTexture(Option2, "content/gui/pitstop/tyre_2_OFF.png")
    ac.setBackgroundTexture(Option3, "content/gui/pitstop/tyre_3_OFF.png")
    ac.setBackgroundTexture(Option4, "content/gui/pitstop/tyre_4_OFF.png")
    ac.setBackgroundTexture(Option5, "content/gui/pitstop/tyre_5_OFF.png")


def Option1Event(name, state):
    global Option1, Tires, Tirecoord, Resolution

    Tires = "Option1"
    Tirecoord = int(Resolution / 2 - 97)
    ac.setBackgroundTexture(NoChange, "content/gui/pitstop/tyre_no_change_OFF.png")
    ac.setBackgroundTexture(Option1, "content/gui/pitstop/tyre_1_ON.png")
    ac.setBackgroundTexture(Option2, "content/gui/pitstop/tyre_2_OFF.png")
    ac.setBackgroundTexture(Option3, "content/gui/pitstop/tyre_3_OFF.png")
    ac.setBackgroundTexture(Option4, "content/gui/pitstop/tyre_4_OFF.png")
    ac.setBackgroundTexture(Option5, "content/gui/pitstop/tyre_5_OFF.png")


def Option2Event(name, state):
    global Option2, Tires, Tirecoord, Resolution

    Tires = "Option2"
    Tirecoord = int(Resolution / 2 + 18)
    ac.setBackgroundTexture(NoChange, "content/gui/pitstop/tyre_no_change_OFF.png")
    ac.setBackgroundTexture(Option1, "content/gui/pitstop/tyre_1_OFF.png")
    ac.setBackgroundTexture(Option2, "content/gui/pitstop/tyre_2_ON.png")
    ac.setBackgroundTexture(Option3, "content/gui/pitstop/tyre_3_OFF.png")
    ac.setBackgroundTexture(Option4, "content/gui/pitstop/tyre_4_OFF.png")
    ac.setBackgroundTexture(Option5, "content/gui/pitstop/tyre_5_OFF.png")


def Option3Event(name, state):
    global Option3, Tires, Tirecoord, Resolution

    Tires = "Option3"
    Tirecoord = int(Resolution / 2 + 126)
    ac.setBackgroundTexture(NoChange, "content/gui/pitstop/tyre_no_change_OFF.png")
    ac.setBackgroundTexture(Option1, "content/gui/pitstop/tyre_1_OFF.png")
    ac.setBackgroundTexture(Option2, "content/gui/pitstop/tyre_2_OFF.png")
    ac.setBackgroundTexture(Option3, "content/gui/pitstop/tyre_3_ON.png")
    ac.setBackgroundTexture(Option4, "content/gui/pitstop/tyre_4_OFF.png")
    ac.setBackgroundTexture(Option5, "content/gui/pitstop/tyre_5_OFF.png")


def Option4Event(name, state):
    global Option4, Tires, Tirecoord, Resolution

    Tires = "Option4"
    Tirecoord = int(Resolution / 2 + 238)
    ac.setBackgroundTexture(NoChange, "content/gui/pitstop/tyre_no_change_OFF.png")
    ac.setBackgroundTexture(Option1, "content/gui/pitstop/tyre_1_OFF.png")
    ac.setBackgroundTexture(Option2, "content/gui/pitstop/tyre_2_OFF.png")
    ac.setBackgroundTexture(Option3, "content/gui/pitstop/tyre_3_OFF.png")
    ac.setBackgroundTexture(Option4, "content/gui/pitstop/tyre_4_ON.png")
    ac.setBackgroundTexture(Option5, "content/gui/pitstop/tyre_5_OFF.png")


def Option5Event(name, state):
    global Option5, Tires, Tirecoord, Resolution

    Tires = "Option5"
    Tirecoord = int(Resolution / 2 + 353)
    ac.setBackgroundTexture(NoChange, "content/gui/pitstop/tyre_no_change_OFF.png")
    ac.setBackgroundTexture(Option1, "content/gui/pitstop/tyre_1_OFF.png")
    ac.setBackgroundTexture(Option2, "content/gui/pitstop/tyre_2_OFF.png")
    ac.setBackgroundTexture(Option3, "content/gui/pitstop/tyre_3_OFF.png")
    ac.setBackgroundTexture(Option4, "content/gui/pitstop/tyre_4_OFF.png")
    ac.setBackgroundTexture(Option5, "content/gui/pitstop/tyre_5_ON.png")


def BodyEvent(name, state):
    global Body, FixBody, Bodycoord, Resolution

    if FixBody == 'no':
        Bodycoord = int(Resolution / 2 - 2)
        FixBody = 'yes'
        ac.setBackgroundTexture(Body, "content/gui/pitstop/repair_body_ON.png")
    else:
        Bodycoord = int(Resolution / 2 + 140)
        FixBody = 'no'
        ac.setBackgroundTexture(Body, "content/gui/pitstop/repair_body_OFF.png")


def EngineEvent(name, state):
    global Engine, FixEngine, Enginecoord, Resolution

    if FixEngine == 'no':
        Enginecoord = int(Resolution / 2 + 243)
        FixEngine = 'yes'
        ac.setBackgroundTexture(Engine, "content/gui/pitstop/repair_engine_ON.png")
    else:
        Enginecoord = int(Resolution / 2 + 140)
        FixEngine = 'no'
        ac.setBackgroundTexture(Engine, "content/gui/pitstop/repair_engine_OFF.png")


def SuspensionEvent(name, state):
    global Suspension, FixSuspen, Suspensioncoord, Resolution

    if FixSuspen == 'no':
        Suspensioncoord = int(Resolution / 2 - 227)
        FixSuspen = 'yes'
        ac.setBackgroundTexture(Suspension, "content/gui/pitstop/repair_sus_ON.png")
    else:
        Suspensioncoord = int(Resolution / 2 + 140)
        FixSuspen = 'no'
        ac.setBackgroundTexture(Suspension, "content/gui/pitstop/repair_sus_OFF.png")


def PitStop():
    global Resolution, Tirecoord, FuelMax, FuelAdd, Gas, u
    global Suspensioncoord, Bodycoord, Enginecoord, FuelOption, FuelIn, adjust_x, adjust_y, FullScreen

    if FullScreen == False:
        CoordAdjust()

    left_click(Tirecoord + adjust_x, 140 + adjust_y)
    left_click(Tirecoord + adjust_x, 140 + adjust_y)
    u = 0
    FuelAdd = int(Gas)
    if FuelAdd == FuelMax:
        left_click(int(Resolution / 2 + 250) + adjust_x, 300 + adjust_y)
    else:
        if FuelOption == 1:
            while u < FuelAdd:
                left_click(Fuelcoord + adjust_x, 300 + adjust_y)
                u = u + 1
        else:
            while u < FuelAdd - FuelIn:
                left_click(Fuelcoord + adjust_x, 300 + adjust_y)
                u = u + 1

    left_click(Suspensioncoord + adjust_x, 465 + adjust_y)
    left_click(Bodycoord + adjust_x, 465 + adjust_y)
    left_click(Enginecoord + adjust_x, 465 + adjust_y)
    left_click(int(Resolution / 2 + 158) + adjust_x, 620 + adjust_y)

# def CheckUpdateBox():
#   global Status
#
#
#

def getNotification():
    global Notify, NotificationLabel, StatusLabel
    try:
        Notify = box.getNotificationFrom(
            'http://api.telegram.org/bot243075740:AAEuscXHE-VaQCwZuWpytMzmC3Iwhopub6E/getUpdates')
        ac.setText(NotificationLabel, Notify)
    except:
        ac.log('BoxRadio: No internet connection')
        Status = "No internet connection"
        ac.setText(StatusLabel, Status)


def acUpdate(deltaT):
    try:
        global Speed, DoPit, FuelMax, InPit, FuelIn, session, delta  # Position,InitialPosition  vars can be removed from the code
        global PitX, PitY, PitZ  # added global variables initiliased as 0,0,0. X,Y,Z co-ords of pit box
        global AppInitialised  # added global variable initiliased as False
        global Notify

        if not AppInitialised:  # First call to app, set variables
            # CheckUpdateBox()
            getNotification()
            InPit = sim_info.sim_info.graphics.isInPit
            FuelMax = int(sim_info.sim_info.static.maxFuel)
            ac.setRange(FuelSelection, 0, FuelMax)
            ReadPreset()
            ac.setValue(Preset1, 1)
            AppInitialised = True

        if abs(PitX) < 1e-5:  # set pit position
            InPit = sim_info.sim_info.graphics.isInPit
            if InPit:
                PitX, PitY, PitZ = ac.getCarState(0, acsys.CS.WorldPosition)
                ac.log("BoxRadio: Pit position initialized at X:" + str(PitX) + " Y:" + str(PitY) + " Z:" + str(PitZ))

        Speed = ac.getCarState(0, acsys.CS.SpeedKMH)

        if Speed < 0.1 and DoPit == 0:
            session = sim_info.sim_info.graphics.session  # session number, 2 is race
            InPit = sim_info.sim_info.graphics.isInPit
            if session == 2:
                PosX, PosY, PosZ = ac.getCarState(0, acsys.CS.WorldPosition)  # current co-ord position
                delta = ((PosX - PitX) ** 2 + (PosY - PitY) ** 2 + (
                    PosZ - PitZ) ** 2) ** 0.5  # straight line dist between pitbox and car
                FuelIn = int(sim_info.sim_info.physics.fuel)
                if delta < 8.0 or InPit == 1:  # if InPit or within 8m of pitbox, quite relaxed limit guarantees app trigger on menu appear
                    PitStop()
                    ac.log("BoxRadio: Pit performed at X:" + str(PosX) + " Y:" + str(PosY) + " Z:" + str(PosZ))
                    ac.log("BoxRadio: Delta:" + str(delta))
            DoPit = 1

        if Speed >= 0.1:
            DoPit = 0

    except Exception as e:
        ac.log("BoxRadio: Error in acUpdate: %s" % e)


def left_click(x, y):
    SetCursorPos(x, y)
    mouse_event(2, 0, 0, 0, 0)
    mouse_event(4, 0, 0, 0, 0)


def WriteSection():
    global Car, FixBody, FixEngine, FixSuspen, Preset, Tires, Gas

    PresetConfig = configparser.ConfigParser()
    PresetConfig.read('apps\python\BoxRadio\BoxRadio.ini')
    PresetConfig.add_section('PRESET' + str(Preset) + '_' + ac.getCarName(0))
    PresetConfig.set('PRESET' + str(Preset) + '_' + ac.getCarName(0), 'car', ac.getCarName(0))
    PresetConfig.set('PRESET' + str(Preset) + '_' + ac.getCarName(0), 'tyre', Tires)
    PresetConfig.set('PRESET' + str(Preset) + '_' + ac.getCarName(0), 'fuel', str(Gas))
    PresetConfig.set('PRESET' + str(Preset) + '_' + ac.getCarName(0), 'body', FixBody)
    PresetConfig.set('PRESET' + str(Preset) + '_' + ac.getCarName(0), 'engine', FixEngine)
    PresetConfig.set('PRESET' + str(Preset) + '_' + ac.getCarName(0), 'suspen', FixSuspen)
    with open('apps\python\BoxRadio\BoxRadio.ini', 'w') as configfile:
        configfile.write(
            ';Set "FUEL / add" to "1" to ADD the fuel to the amount already in the tank or set to "0" to fill the tank up to the amount selected on the app.' + '\n')
        configfile.write(
            ';UI Size example: Set "UI / sizemultiplier" to "1.2" in order to increase UI size in 20% (min: 1.0, max: 3.0)' + '\n' + '\n')
        PresetConfig.write(configfile)

    ac.log("BoxRadio: Preset section added")


def WritePreset():
    global Car, FixBody, FixEngine, FixSuspen, Preset, Tires, Gas

    PresetConfig = configparser.ConfigParser()
    PresetConfig.read('apps\python\BoxRadio\BoxRadio.ini')
    Car = PresetConfig['PRESET' + str(Preset) + '_' + ac.getCarName(0)]['car']
    if Tires != 'NoChange' or Gas != 0 or FixBody != 'no' or FixEngine != 'no' or FixSuspen != 'no' or Car != ac.getCarName(
            0):
        if Car != ac.getCarName(0):
            PresetConfig.add_section('PRESET' + str(Preset) + '_' + ac.getCarName(0))
        PresetConfig.set('PRESET' + str(Preset) + '_' + str(Car), 'car', ac.getCarName(0))
        PresetConfig.set('PRESET' + str(Preset) + '_' + str(Car), 'tyre', Tires)
        PresetConfig.set('PRESET' + str(Preset) + '_' + str(Car), 'fuel', str(Gas))
        PresetConfig.set('PRESET' + str(Preset) + '_' + str(Car), 'body', FixBody)
        PresetConfig.set('PRESET' + str(Preset) + '_' + str(Car), 'engine', FixEngine)
        PresetConfig.set('PRESET' + str(Preset) + '_' + str(Car), 'suspen', FixSuspen)
        with open('apps\python\BoxRadio\BoxRadio.ini', 'w') as configfile:
            configfile.write(
                ';Set "FUEL / add" to "1" to ADD the fuel to the amount already in the tank or set to "0" to fill the tank up to the amount selected on the app.' + '\n')
            configfile.write(
                ';UI Size example: Set "UI / sizemultiplier" to "1.2" in order to increase UI size in 20% (min: 1.0, max: 3.0)' + '\n' + '\n')
            PresetConfig.write(configfile)


def ReadPreset():
    global Car, FixBody, FixEngine, FixSuspen, Preset, Tires, Gas

    PresetConfig = configparser.ConfigParser()
    PresetConfig.read('apps\python\BoxRadio\BoxRadio.ini')

    if not 'PRESET' + str(Preset) + '_' + ac.getCarName(0) in PresetConfig:
        WriteSection()

    Car = PresetConfig['PRESET' + str(Preset) + '_' + ac.getCarName(0)]['car']

    if Car == ac.getCarName(0):
        ac.setValue(FuelSelection, int(PresetConfig['PRESET' + str(Preset) + '_' + str(Car)]['fuel']))
        if PresetConfig['PRESET' + str(Preset) + '_' + str(Car)]['body'] == 'no':
            FixBody = 'yes'
        else:
            FixBody = 'no'
        if PresetConfig['PRESET' + str(Preset) + '_' + str(Car)]['engine'] == 'no':
            FixEngine = 'yes'
        else:
            FixEngine = 'no'
        if PresetConfig['PRESET' + str(Preset) + '_' + str(Car)]['suspen'] == 'no':
            FixSuspen = 'yes'
        else:
            FixSuspen = 'no'
        if PresetConfig['PRESET' + str(Preset) + '_' + str(Car)]['tyre'] == 'NoChange':
            NoChangeEvent('name', 0)
        elif PresetConfig['PRESET' + str(Preset) + '_' + str(Car)]['tyre'] == 'Option1':
            Option1Event('name', 0)
        elif PresetConfig['PRESET' + str(Preset) + '_' + str(Car)]['tyre'] == 'Option2':
            Option2Event('name', 0)
        elif PresetConfig['PRESET' + str(Preset) + '_' + str(Car)]['tyre'] == 'Option3':
            Option3Event('name', 0)
        elif PresetConfig['PRESET' + str(Preset) + '_' + str(Car)]['tyre'] == 'Option4':
            Option4Event('name', 0)
        elif PresetConfig['PRESET' + str(Preset) + '_' + str(Car)]['tyre'] == 'Option5':
            Option5Event('name', 0)
    else:
        ac.setValue(FuelSelection, 0)
        NoChangeEvent('name', 0)
        FixBody = 'yes'
        FixEngine = 'yes'
        FixSuspen = 'yes'

    BodyEvent('name', 0)
    EngineEvent('name', 0)
    SuspensionEvent('name', 0)
    FuelEvent(0)


# def ReadSpeech():
#    global Car, FixBody, FixEngine, FixSuspen, Preset, Tires, Gas

def Preset1Event(name, state):
    global Preset

    WritePreset()

    Preset = 1
    ac.setValue(Preset1, 1)
    ac.setValue(Preset2, 0)
    ac.setValue(Preset3, 0)
    ac.setValue(Preset4, 0)

    ReadPreset()


def Preset2Event(name, state):
    global Preset

    WritePreset()

    Preset = 2
    ac.setValue(Preset2, 1)
    ac.setValue(Preset1, 0)
    ac.setValue(Preset3, 0)
    ac.setValue(Preset4, 0)

    ReadPreset()


def Preset3Event(name, state):
    global Preset

    WritePreset()

    Preset = 3
    ac.setValue(Preset3, 1)
    ac.setValue(Preset1, 0)
    ac.setValue(Preset2, 0)
    ac.setValue(Preset4, 0)

    ReadPreset()


def Preset4Event(name, state):
    global Preset

    WritePreset()

    Preset = 4
    ac.setValue(Preset4, 1)
    ac.setValue(Preset1, 0)
    ac.setValue(Preset2, 0)
    ac.setValue(Preset3, 0)

    ReadPreset()


def acShutdown():
    global superhot
    WritePreset()
    subprocess.Popen.kill(superhot)
    ctypes.windll.user32.UnregisterHotKey(None, 1)


def CoordAdjust():
    global adjust_x, adjust_y, leftbordersize, topbordersize, Resolution, FindWindow

    class RECT(ctypes.Structure):
        _fields_ = [
            ('left', ctypes.c_int),
            ('top', ctypes.c_int),
            ('right', ctypes.c_int),
            ('bottom', ctypes.c_int)
        ]

    GetWindowRect = ctypes.windll.user32.GetWindowRect
    rect = RECT()

    FindWindow = ctypes.windll.user32.FindWindowA
    ACWindow = FindWindow(b'acsW', 0)
    ac.log('BoxRadio: Handle: ' + str(ACWindow))

    # GetWindowRect(foreground_window, ctypes.byref(rect))
    GetWindowRect(ACWindow, ctypes.byref(rect))
    Resolution = int(rect.right - rect.left - 2 * leftbordersize)
    ac.log('BoxRadio: New Resolution: ' + str(Resolution))
    adjust_x = int(rect.left + leftbordersize)
    adjust_y = int(rect.top + topbordersize)
    ac.log('BoxRadio: Res: Top ' + str(adjust_y) + ' Left: ' + str(adjust_x))
    WritePreset()
    ReadPreset()


def listen_key():
    try:
        ctypes.windll.user32.RegisterHotKey(None, 1, 0, win32con.VK_F10)
        msg = ctypes.wintypes.MSG()
        while listen_active:
            if ctypes.windll.user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == win32con.WM_HOTKEY:
                    hotkey_pressed()
                ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
                ctypes.windll.user32.DispatchMessageA(ctypes.byref(msg))
    except:
        ac.log('BoxRadio: Hotkey fail')


def hotkey_pressed():
    if Preset == 1:
        Preset2Event('name', 0)
    elif Preset == 2:
        Preset3Event('name', 0)
    elif Preset == 3:
        Preset4Event('name', 0)
    elif Preset == 4:
        Preset1Event('name', 0)


key_listener = threading.Thread(target=listen_key)
key_listener.daemon = True
key_listener.start()

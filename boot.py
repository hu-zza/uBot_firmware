def initDir(dirName):
    global CONFIG
    global EXCEPTIONS

    if dirName in CONFIG.get("_rootList"):
        try:
            CONFIG["_" + dirName + "List"] = uos.listdir(dirName)
        except Exception as e:
            EXCEPTIONS.append((DT.datetime(), e))
    else:
        try:
            uos.mkdir(dirName)
            CONFIG["_" + dirName + "List"] = []
        except Exception as e:
            EXCEPTIONS.append((DT.datetime(), e))


def initFile(fileName, dirName = "", content = ""):
    global CONFIG

    if dirName != "":
        dirName += "/"

    try:
        with open(dirName + fileName, "w") as file:
            file.write(str(content) + "\n")
        CONFIG["_" + dirName[:-1] + "List"].append(fileName)
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))


def saveDateTime():
    try:
        with open("etc/.datetime", "w") as file:
            file.write(str(DT.datetime()) + "\n")
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))


def saveConfig():
    global CONFIG

    try:
        with open("etc/.config", "w") as file:
            for key, value in CONFIG.items():
                # Exclude transients
                if key[0] != "_":
                    if isinstance(value, str):
                        file.write("{} = \"{}\"\n".format(key, value))
                    else:
                        file.write("{} = {}\n".format(key, value))
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))


###########
## IMPORTS

import esp, network, gc, ujson, uos, usocket, webrepl

from machine     import I2C, Pin, PWM, RTC, Timer, UART, WDT, reset
from micropython import const
from ubinascii   import hexlify
from uio         import FileIO
from utime       import sleep, sleep_ms, sleep_us
from sys         import print_exception

try:
    configException = ""
    import config
except Exception as e:
    configException = e

try:
    feedbackException = ""
    from feedback import Feedback
except Exception as e:
    feedbackException = e


###########
## CONFIG

DT = RTC()
# fallback datetime
DT.datetime((2020, 12, 31, 0, 0, 0, 0, 0))

EXCEPTIONS = []
CONFIG     = {}

configDefaults = {

    # General settings, indicated in config.py too.

    "essid"       : "",
    "passw"       : "uBot_pwd",

    "uart"        : False,
    "webRepl"     : False,
    "webServer"   : True,

    "turtleHat"   : True,
    "beepMode"    : True,

    "pressLength" : const(5),
    "firstRepeat" : const(25),


    # These can also be configured manually (in config.py).
    # (But almost never will be necessary to do that.)

    "_apActive"  : True,
    "_wdActive"  : True,

    "_i2cActive" : True,
    "_sda"       : const(0),
    "_scl"       : const(2),
    "_freq"      : const(400000)
}

CONN  = ""
ADDR  = ""

COUNTER_POS  = 0
PRESSED_BTNS = []
COMMANDS = []
EVALS = []

try:
    CONFIG["_rootList"] = uos.listdir()
except Exception as e:
    EXCEPTIONS.append((DT.datetime(), e))


initDir("etc")

if ".datetime" in CONFIG.get("_etcList"):
    try:
        with open("etc/.datetime") as file:
            DT.datetime(eval(file.readline().strip()))
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))
else:
    initFile(".datetime", "etc", DT.datetime())


if configException != "":
    EXCEPTIONS.append((DT.datetime(), configException))

if feedbackException != "":
    EXCEPTIONS.append((DT.datetime(), feedbackException))


for key in configDefaults.keys():
    try:
        CONFIG[key] = eval("config." + key)
    except Exception as e:
        CONFIG[key] = configDefaults.get(key)


if ".config" in CONFIG.get("_etcList"):
    try:
        with open("etc/.config") as file:
            for line in file:
                sep = line.find("=")
                CONFIG[line[:sep].strip()] = eval(line[sep+1:].strip())
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))
else:
    initFile(".config", "etc")

if CONFIG.get("_i2cActive"):
    try:
        F = Feedback(CONFIG.get("_freq"), Pin(CONFIG.get("_sda")), Pin(CONFIG.get("_scl")))
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))


initDir("code")


###########
## GPIO

MSG = P15 = Pin(15, Pin.OUT)
BEE = PWM(Pin(15), freq = 262, duty = 0)
MSG.off()


if CONFIG.get("turtleHat"):
    CLK = Pin(13, Pin.OUT)  # GPIO pin. It is connected to the counter (CD4017) if physical switch CLOCK is on.
    INP = Pin(16, Pin.OUT)  # GPIO pin. Receives button presses from turtle HAT if physical switches: WAKE off, PULL down
                            # FUTURE: INP = Pin(16, Pin.IN)
    INP.off()               # DEPRECATED: New PCB design (2.1) will resolve this.
    INP.init(Pin.IN)        # DEPRECATED: New PCB design (2.1) will resolve this.
    CLK.off()
else:
    P13 = Pin(13, Pin.OUT)
    P16 = Pin(16, Pin.IN)   # MicroPython can not handle the pull-down resistor of the GPIO16: Use PULL physical switch.
    P13.off()


P12 = Pin(12, Pin.OUT)              # GPIO pin. On turtle HAT it can drive a LED if you switch physical switch on.
P14 = Pin(14, Pin.IN, Pin.PULL_UP)  # GPIO pin.
P12.off()


P4 = Pin(4, Pin.OUT)         #Connected to the 10th pin of the motor driver (SN754410). T1 terminal (M11, M14)
P5 = Pin(5, Pin.OUT)         #Connected to the 15th pin of the motor driver (SN754410). T1 terminal (M11, M14)
P4.off()
P5.off()

MOT = [[P4, P5], [P4, P5]]

if not CONFIG.get("uart"):
    MOT[0][0] = P1 = Pin(1, Pin.OUT)     #Connected to the  2nd pin of the motor driver (SN754410). T0 terminal (M3, M6)
    MOT[0][1] = P3 = Pin(3, Pin.OUT)     #Connected to the  7th pin of the motor driver (SN754410). T0 terminal (M3, M6)
    P1.off()
    P3.off()


if not CONFIG.get("_i2cActive"):
    P0 = Pin(0, Pin.IN)
    P2 = Pin(2, Pin.IN)


###########
## AP

AP = network.WLAN(network.AP_IF)

AP.active(CONFIG.get("_apActive"))
AP.ifconfig(("192.168.11.1", "255.255.255.0", "192.168.11.1", "192.168.11.1"))
AP.config(authmode = network.AUTH_WPA_WPA2_PSK)

# if ESSID is an empty string, generate the default: uBot__xx:xx:xx (MAC address' last 3 octets )
if CONFIG.get("essid") == "":
    CONFIG["essid"] = "uBot__" + hexlify(network.WLAN().config('mac'), ':').decode()[9:]

try:
    AP.config(essid = CONFIG.get("essid"))
except Exception:
    AP.config(essid = "uBot")


# if password is too short (< 8 chars), set to default
if len(CONFIG.get("passw")) < 8:
    CONFIG["passw"] = configDefaults.get("passw")

try:
    AP.config(password = CONFIG.get("passw"))
except Exception:
    AP.config(password = "uBot_pwd")


###########
## SOCKET

S = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
S.bind(("", 80))
S.listen(5)


###########
## GENERAL

gc.enable()
esp.osdebug(0)
esp.sleep_type(esp.SLEEP_NONE)

TIMER = Timer(-1)


if CONFIG.get("_wdActive"):
    WD = WDT()


# The REPL is attached by default, detach if not needed.
if not CONFIG.get("uart"):
    uos.dupterm(None, 1)

if CONFIG.get("webRepl"):
    try:
        webrepl.start()
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))

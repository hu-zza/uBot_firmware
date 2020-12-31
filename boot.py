def initDir(dirName):
    global CONFIG
    global EXCEPTIONS

    if dirName in CONFIG.get("~rootList"):
        try:
            CONFIG["~" + dirName + "List"] = uos.listdir(dirName)
        except Exception as e:
            EXCEPTIONS.append((DT.datetime(), e))
    else:
        try:
            uos.mkdir(dirName)
            CONFIG["~" + dirName + "List"] = []
        except Exception as e:
            EXCEPTIONS.append((DT.datetime(), e))


def initFile(fileName, dirName = "", content = ""):
    global CONFIG

    if dirName != "":
        dirName += "/"

    try:
        with open(dirName + fileName, "w") as file:
            file.write(str(content) + "\n")
        CONFIG["~" + dirName[:-1] + "List"].append(fileName)
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))


def saveConfig():
    global CONFIG

    try:
        with open("etc/config.txt", "w") as file:
            for key, value in CONFIG.items():
                # Exclude transients
                if (key[0] != "~"):
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

DT         = RTC()
EXCEPTIONS = []
CONFIG     = {}

configDefaults = {

    # General settings, indicated in config.py too.

    "essid"       : "",
    "passw"       : "uBot_pwd",

    "uart"        : False,
    "webRepl"     : True,
    "webServer"   : True,
    "beepMode"    : True,

    "pressLength" : const(5),
    "firstRepeat" : const(25),


    # These can also be configured.
    # (But almost never will be necessary to do that.)

    "~apActive"    : True,
    "~sda"         : const(0),
    "~scl"         : const(2),
    "~freq"        : const(400000)
}

try:
    CONFIG["~rootList"] = uos.listdir()
except Exception as e:
    EXCEPTIONS.append((DT.datetime(), e))


initDir("etc")

if "datetime.txt" in CONFIG.get("~etcList"):
    try:
        with open("etc/datetime.txt") as file:
            DT.datetime(eval(file.readline().strip()))
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))
else:
    initFile("datetime.txt", "etc", DT.datetime())


if configException != "":
    EXCEPTIONS.append((DT.datetime(), configException))

if feedbackException != "":
    EXCEPTIONS.append((DT.datetime(), feedbackException))


for key in configDefaults.keys():
    try:
        CONFIG[key] = eval("config." + key)
    except Exception as e:
        CONFIG[key] = configDefaults.get(key)


if "config.txt" in CONFIG.get("~etcList"):
    try:
        with open("etc/config.txt") as file:
            for line in file:
                sep = line.find("=")
                CONFIG[line[:sep].strip()] = eval(line[sep+1:].strip())
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))
else:
    initFile("config.txt", "etc")


try:
    F = Feedback(CONFIG.get("~freq"), Pin(CONFIG.get("~sda")), Pin(CONFIG.get("~scl")))
except Exception as e:
    EXCEPTIONS.append((DT.datetime(), e))


initDir("code")


###########
## GPIO

MSG = Pin(15, Pin.OUT)
BEE = PWM(Pin(15), freq = 262, duty = 0)
MSG.off()

CLK = Pin(13, Pin.OUT)  #GPIO pin. Advances the counter (CD4017) which maps the buttons of the turtle HAT.
INP = Pin(16, Pin.OUT)  #GPIO pin. Receives button presses from turtle HAT.
CLK.off()
INP.off()
INP.init(Pin.IN)

P12 = Pin(12, Pin.OUT)  #GPIO pin.
P14 = Pin(14, Pin.OUT)  #GPIO pin.
P12.off()
P14.off()

if not CONFIG.get("uart"):
    MOT1 = Pin(1, Pin.OUT)  #Connected to the  2nd pin of the motor driver (SN754410). Left motor.
    MOT2 = Pin(3, Pin.OUT)  #Connected to the  7th pin of the motor driver (SN754410). Left motor.
    MOT1.off()
    MOT2.off()

MOT3 = Pin(4, Pin.OUT)      #Connected to the 10th pin of the motor driver (SN754410). Right motor.
MOT4 = Pin(5, Pin.OUT)      #Connected to the 15th pin of the motor driver (SN754410). Right motor.
MOT3.off()
MOT4.off()


###########
## AP

AP = network.WLAN(network.AP_IF)

AP.active(CONFIG.get("~apActive"))
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

T    = Timer(-1)
#WD   = WDT()
CONN = ""
ADDR = ""

COUNTER_POS  = 0
PRESSED_BTNS = []
COMMANDS = []
EVALS = []

# The REPL is attached by default, deattache if not needed.
if not CONFIG.get("uart"):
    uos.dupterm(None, 1)

if CONFIG.get("webRepl"):
    try:
        webrepl.start()
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))

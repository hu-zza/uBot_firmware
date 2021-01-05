import esp, gc, network, uos, sys, webrepl

from machine   import Pin, PWM, RTC, UART
from ubinascii import hexlify


gc.enable()
esp.osdebug(None)
esp.sleep_type(esp.SLEEP_NONE)


dt = RTC()
ex = []

try:
    dt = sys.modules.get("ubot_firmware").DT
except Exception as e:
    ex.append((dt.datetime(), e))

try:
    ex =  sys.modules.get("ubot_firmware").EXCEPTIONS + ex
except Exception as e:
    ex.append((dt.datetime(), e))


try:
    feedback = PWM(Pin(15), 1, 500)
except Exception as e:
    ex.append((dt.datetime(), e))

try:
    uart = UART(0, baudrate = 115200)
except Exception as e:
    ex.append((dt.datetime(), e))

try:
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.ifconfig(("192.168.11.1", "255.255.255.0", "192.168.11.1", "8.8.8.8"))
    ap.config(authmode = network.AUTH_WPA_WPA2_PSK)
except Exception as e:
    ex.append((dt.datetime(), e))

try:
    essid = "uBot__" + hexlify(ap.config("mac"), ":").decode()[9:]
    ap.config(essid = essid)
except Exception as e:
    ex.append((dt.datetime(), e))

try:
    ap.config(password = "uBot_pwd")
except Exception as e:
    ex.append((dt.datetime(), e))

try:
    webrepl.start(password = "uBot_REPL")
except Exception as e:
    ex.append((dt.datetime(), e))


################################
## METHODS

def showExceptions():
    for i in range(len(ex)):
        print("{}\t{}\t{}".format(i, ex[i][0], ex[i][1]))

def printException(nr):
    if 0 <= nr and nr < len(ex):
        print(ex[nr][0])
        sys.print_exception(ex[nr][1])
    else:
        print("List index ({}) is out of range ({}).".format(nr, len(ex)))

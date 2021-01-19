import esp, gc, network, uos, sys, webrepl

from machine   import Pin, PWM, RTC, UART
from ubinascii import hexlify


dt = RTC()
ex = []



################################
## INITIALISATION

gc.enable()
esp.osdebug(None)
esp.sleep_type(esp.SLEEP_NONE)


try:
    core = sys.modules.get("ubot_core")
except Exception as e:
    ex.append((dt.datetime(), e))


try:
    dt = core.DT
except Exception as e:
    ex.append((dt.datetime(), e))


try:
    ex =  core.EXCEPTIONS + ex
except Exception as e:
    ex.append((dt.datetime(), e))


try:
    P1 = Pin(1, Pin.OUT)    # UART0 + Connected to the  2nd pin of the motor driver (SN754410). T0 terminal (M3, M6)
    P3 = Pin(3, Pin.OUT)    # UART0 + Connected to the  7th pin of the motor driver (SN754410). T0 terminal (M3, M6)
    P4 = Pin(4, Pin.OUT)    #         Connected to the 10th pin of the motor driver (SN754410). T1 terminal (M11, M14)
    P5 = Pin(5, Pin.OUT)    #         Connected to the 15th pin of the motor driver (SN754410). T1 terminal (M11, M14)
    P1.off()
    P3.off()
    P4.off()
    P5.off()

    motorPins = [[P1, P3], [P4, P5]]
except Exception as e:
    ex.append((dt.datetime(), e))


try:
    errorSignal = PWM(Pin(15), 1, 500)
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
## PUBLIC METHODS

def listExceptions():
    for i in range(len(ex)):
        print("{}\t{}\t{}".format(i, ex[i][0], ex[i][1]))


def printException(nr):
    if 0 <= nr and nr < len(ex):
        print(ex[nr][0])
        sys.print_exception(ex[nr][1])
    else:
        print("List index ({}) is out of range ({}).".format(nr, len(ex)))


def startUart():
    """ You should deactivate the motor first. """
    try:
        uart = UART(0, baudrate = 115200)
        uos.dupterm(uart, 1)
    except Exception as e:
        ex.append((dt.datetime(), e))


def stopUart():
    try:
        uos.dupterm(None, 1)
        P1.off()
        P3.off()
    except Exception as e:
        ex.append((dt.datetime(), e))


def stopErrorSignal():
    try:
        errorSignal.deinit()
    except Exception as e:
        ex.append((dt.datetime(), e))

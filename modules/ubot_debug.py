"""
    uBot_firmware   // The firmware of the μBot, the educational floor robot. (A MicroPython port to ESP8266 with additional modules.)

    This file is part of uBot_firmware.
    [https://zza.hu/uBot_firmware]
    [https://git.zza.hu/uBot_firmware]


    MIT License

    Copyright (c) 2020-2021 Szabó László András // hu-zza

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

import esp, network, uos, usys, webrepl

from machine   import Pin, PWM, Timer, UART
from ubinascii import hexlify

import ubot_logger as logger



################################
## INITIALISATION

_uartState = 0

try:
    esp.osdebug(None)
    esp.sleep_type(esp.SLEEP_NONE)
except Exception as e:
    logger.append(e)


try:
    signal = PWM(Pin(15), 1, 500)
except Exception as e:
    logger.append(e)


try:
    P1 = Pin(1, Pin.OUT)     # UART0 + Connected to the  2nd pin of the motor driver (SN754410). T0 terminal (M3, M6)
    P3 = Pin(3, Pin.OUT)     # UART0 + Connected to the  7th pin of the motor driver (SN754410). T0 terminal (M3, M6)
    P4 = Pin(4, Pin.OUT)     #         Connected to the 10th pin of the motor driver (SN754410). T1 terminal (M11, M14)
    P5 = Pin(5, Pin.OUT)     #         Connected to the 15th pin of the motor driver (SN754410). T1 terminal (M11, M14)

    P16 = Pin(16, Pin.OUT)   # FUTURE: P16 = Pin(16, Pin.IN)
    P16.off()                # DEPRECATED: New PCB design (2.1) will resolve this.
    P16.init(Pin.IN)         # DEPRECATED: New PCB design (2.1) will resolve this.

    P1.off()
    P3.off()
    P4.off()
    P5.off()

    motorPins = [[P1, P3], [P4, P5]]
except Exception as e:
    logger.append(e)


try:
    usys.modules.get("ubot_turtle")._stopButtonChecking()
except Exception as e:
    logger.append(e)


try:
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.ifconfig(("192.168.11.1", "255.255.255.0", "192.168.11.1", "8.8.8.8"))
    ap.config(authmode = network.AUTH_WPA_WPA2_PSK)
except Exception as e:
    logger.append(e)


try:
    ssid = "uBot__" + hexlify(ap.config("mac"), ":").decode()[9:]
    ap.config(ssid = ssid)
except Exception as e:
    logger.append(e)
    try:
        ap.config(ssid = "uBot_debug")
    except Exception as e:
        logger.append(e)


try:
    ap.config(password = "uBot_pwd")
except Exception as e:
    logger.append(e)


try:
    webrepl.start(password = "uBot_REPL")
except Exception as e:
    logger.append(e)



################################
## PUBLIC METHODS

def listExceptions():
    stopSignal()
    exceptionFiles = uos.listdir("/log/exception")
    print()
    for fileName in exceptionFiles:
        print("{}\t{}".format(int(fileName[:-4]), fileName))        # [:-4] strip the file extension: .txt
    print()


def printExceptions(nr = None):
    stopSignal()
    if nr is None:
        print(("\r\nThis function needs one parameter,\r\n"
               "the ordinal of a specific exception log.\r\n"
               "You can list ordinals and file names with\r\n"
               "listExceptions() command.\r\n"))
    else:
        exceptionFiles = uos.listdir("/log/exception")
        fileName = "{:010d}.txt".format(nr)

        if fileName in exceptionFiles:
            try:
                print()
                with open("/log/exception/" + fileName) as file:
                    for line in file:
                        print(line, end="")
                print()
            except Exception as e:
                logger.append(e)
        else:
            print("\r\nThere is no exception file with the given ordinal: {}\r\n".format(nr))


def startUart():
    global _uartState

    if _uartState == 0:
        print(("\r\nPlease check that you deactivated the feedback\r\n"
               "sensors by the physical switch on main PCB.\r\n"
               "After that, call this method again.\r\n"))
        _uartState += 1
    elif _uartState == 1:
        try:
            usys.modules.get("ubot_feedback").deinit()
            uos.dupterm(UART(0, 115200), 1)
            stopSignal()
            _uartState += 1
            print("\r\nThe UART has been started.\r\n")
        except Exception as e:
            logger.append(e)
    else:
        print("\r\nThe UART is already active.\r\n")


def stopUart():
    global _uartState

    if _uartState == 0:
        print("\r\nThe UART is already stopped.\r\n")
    else:
        try:
            uos.dupterm(None, 1)
            P1.off()
            P3.off()
            _uartState = 0
            print("\r\nThe UART has been stopped.\r\n")
        except Exception as e:
            logger.append(e)


def stopSignal():
    try:
        signal.duty(0)
    except Exception as e:
        logger.append(e)



################################
## PRIVATE, HELPER METHODS

def _periodicalChecks(timer):
    if _uartState < 2:
        _checkButtonPress()
    _stopSignalAtLogin()


def _checkButtonPress():
    # pseudo pull-down           # DEPRECATED: New PCB design (2.1) will resolve this.
    if P16.value() == 1:         # DEPRECATED: New PCB design (2.1) will resolve this.
        P16.init(Pin.OUT)        # DEPRECATED: New PCB design (2.1) will resolve this.
        P16.off()                # DEPRECATED: New PCB design (2.1) will resolve this.
        P16.init(Pin.IN)         # DEPRECATED: New PCB design (2.1) will resolve this.

    if P16.value() == 1:
        startUart()


def _stopSignalAtLogin():
    """ Stops the error signal, if user starts the login process. """
    try:
        if webrepl.client_s is not None:
            webrepl.client_s.read(1)    # Dirty hack, but there is no proper check for socket state and this throws
            stopSignal()                # OSError: [Errno 9] EBADF for closed (state = -16) sockets...
    except Exception:
        pass



################################
## INITIALISATION (END)

try:
    timer = Timer(-1)
    timer.init(period = 1000, mode = Timer.PERIODIC, callback = _periodicalChecks)
except Exception as e:
    logger.append(e)

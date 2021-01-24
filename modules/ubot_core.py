import esp, gc, network, ujson, uos, usocket, sys, webrepl

from machine     import Pin, PWM, RTC, Timer, UART, WDT
from ubinascii   import hexlify
from utime       import sleep, sleep_ms

import feedback
import ubot_buzzer    as buzzer
import ubot_logger    as logger
import ubot_motor     as motor
import ubot_turtle    as turtle
import ubot_webserver as webserver


DT     = RTC()
CONFIG = {}



################################
## IMPORT CONFIG FILES

datetimeLoaded = True
configLoaded   = True
defaultsLoaded = True


try:
    import etc.datetime as datetime
except Exception as e:
    datetimeLoaded = False
    logger.append(e)


try:
    import etc.config as config
except Exception as e:
    configLoaded = False
    logger.append(e)


try:
    import etc.defaults as defaults
except Exception as e:
    defaultsLoaded = False
    logger.append(e)



################################
## PUBLIC METHODS

###########
## SERVER

def executeJson(json):
    global CONFIG
    results = []

    if json.get("dateTime") != None:
        dateTime = json.get("dateTime")

        if len(dateTime) == 8:
            DT.datetime(dateTime)
        elif len(dateTime) == 2:
            date = dateTime[0].split("-")
            time = dateTime[1].split(":")
            DT.datetime((int(date[0]), int(date[1]), int(date[2]), 0, int(time[0]), int(time[1]), 0, 0))

        saveDateTime()
        results.append("New dateTime has been set.")

    if json.get("commandList") != None:
        for command in json.get("commandList"):
            if command[0:7] == "TURTLE_":
                for char in command[7:].strip():
                    turtle.move(char)

            elif command[0:6] == "PRESS_":
                pressedList = command[6:].strip().split(":")
                for pressed in pressedList:
                    turtle.press(pressed)

            elif command[0:6] == "SLEEP_":
                sleep_ms(int(command[6:].strip()))

            elif command[0:5] == "BEEP_":
                beepArray = command[5:].strip().split(":")
                buzzer.beep(int(beepArray[0]), int(beepArray[1]), int(beepArray[2]))

            elif command[0:5] == "MIDI_":
                beepArray = command[5:].strip().split(":")
                buzzer.midiBeep(int(beepArray[0]), int(beepArray[1]), int(beepArray[2]))

            elif command[0:5] == "REST_":
                buzzer.rest(int(command[5:].strip()))

            elif command[0:4] == "MOT_":
                motor.move(int(command[4]), int(command[6:].strip()))

            elif command[0:5] == "EXEC_": ##############################################################################
                exec(command[5:])


            if command[0:5] == "EVAL_": ################################################################################
                results.append("'{}' executed successfully, the result is: '{}'".format(command, eval(command[5:])))
            else:
                results.append("'{}' executed successfully.".format(command))


    if json.get("service") != None:
            for command in json.get("service"):
                if command == "START UART":
                    uart = UART(0, 115200)
                    uos.dupterm(uart, 1)
                    CONFIG['uartActive'] = True
                    results.append("UART has started.")

                elif command == "STOP UART":
                    uos.dupterm(None, 1)
                    CONFIG['uartActive'] = False
                    results.append("UART has stopped.")

                elif command == "START WEBREPL":
                    webrepl.start()
                    CONFIG['webReplActive'] = True
                    results.append("WebREPL has started.")

                elif command == "STOP WEBREPL":
                    webrepl.stop()
                    CONFIG['webReplActive'] = False
                    results.append("WebREPL has stopped.")

                elif command == "STOP WEBSERVER":
                    webserver.stop("WebServer has stopped.")

                elif command == "CALIBRATE FEEDBACK":
                    calibrateFeedback()
                    results.append("Calibration has started. It will take 2 minutes.")

                elif command == "CHECK DATETIME":
                    results.append(str(DT.datetime()))

                elif command == "SAVE CONFIG":
                    saveConfig()
                    results.append("Configuration has saved.")

    if len(results) == 0:
        results = ["Processing has completed without any result."]

    return results


###########
## CONFIG

def saveConfig():
    try:
        saveDateTime()
        with open("etc/config.py", "w") as file:

            for key in sorted([k for k in CONFIG.keys()]):
                value = CONFIG.get(key)
                if isinstance(value, str):
                    file.write("{} = '{}'\n".format(key, value))
                else:
                    file.write("{} = {}\n".format(key, value))
    except Exception as e:
        logger.append(e)


def saveDateTime():
    saveToFile("etc/datetime.py", "w", "DT = {}".format(DT.datetime()))


###########
## HELPER

def saveToFile(fileName, mode, content):
    try:
        with open(fileName, mode) as file:
            file.write(content)
    except Exception as e:
        logger.append(e)



###########
## FEEDBACK

def calibrateFeedback():
    result = False
    buzzer.setDefaultState(1)
    buzzer.keyBeep("beepAttention")

    try:
        result = feedback.calibrate(60)         # Duration: 60 seconds
        if result != ():
            CONFIG["feedbackMagMin"] = result[0]
            CONFIG["feedbackMagMax"] = result[1]
            saveConfig()
            result = True
    except Exception as e:
        logger.append(e)

    buzzer.setDefaultState(0)
    buzzer.keyBeep("beepReady")
    return result


################################
## INITIALISATION

gc.enable()
esp.osdebug(None)
esp.sleep_type(esp.SLEEP_NONE)


if datetimeLoaded:
    try:
        DT.datetime(datetime.DT)
    except Exception as e:
        logger.append(e)


if configLoaded or defaultsLoaded:
    if configLoaded:
        conf = "config"
    else:
        conf = "defaults"

    # Fetch every variable from config.py / defaults.py
    for v in dir(eval(conf)):
        if v[0] != "_":                                                       # Do not load private and magic variables.
            CONFIG[v] = eval("{}.{}".format(conf, v))

    if conf == "defaults":
        try:
            CONFIG["powerOnCount"] = int(uos.listdir("log/exception")[-1][:-4]) + 1 # [last file][cut extension]
        except Exception as e:
            logger.append(e)
    else:
        CONFIG["powerOnCount"] = CONFIG.get("powerOnCount") + 1

    # If etc/datetime.py is not accessible, set the DT to 'initialDateTime'.
    if not datetimeLoaded:
        DT.datetime(CONFIG.get("initialDateTime"))


try:
        logger.config(DT, CONFIG.get("powerOnCount"))
except Exception as e:
    logger.append(e)


try:
    with open("log/datetime.txt", "a") as file:
        file.write("{:010d}\n{}\n\n".format(CONFIG.get("powerOnCount"), DT.datetime()))
except Exception as e:
    logger.append(e)


if CONFIG.get("i2cActive"):
    try:
        feedback.config(CONFIG.get("i2cFreq"), CONFIG.get("i2cSda"), CONFIG.get("i2cScl"))
        feedback.setMinMaxTuples(CONFIG.get("feedbackMagMin"), CONFIG.get("feedbackMagMax"))
    except Exception as e:
        logger.append(e)


###########
## GPIO

buzzer.config(CONFIG)

if CONFIG.get("turtleActive"):
    turtle.config(CONFIG)
else:
    P13 = Pin(13, Pin.OUT)
    P16 = Pin(16, Pin.IN)   # MicroPython can not handle the pull-down resistor of the GPIO16: Use PULL physical switch.
    P13.off()


P12 = Pin(12, Pin.OUT)              # GPIO pin. On μBot turtle it can drive a LED if you switch physical switch on.
P14 = Pin(14, Pin.IN, Pin.PULL_UP)  # GPIO pin.
P12.off()


if not CONFIG.get("i2cActive"):
    P0 = Pin(0, Pin.IN)
    P2 = Pin(2, Pin.IN)


motor.config(
    (
        (4, 5),                                         # Left motor
        (0, 0) if CONFIG.get("uartActive") else (1, 3)  # Right motor
    ),
    (
        CONFIG.get("motorPeriod"),
        CONFIG.get("motorDuty"),
        CONFIG.get("motorDutyRange"),
        CONFIG.get("motorRatio")
    )
)


###########
## AP

AP = network.WLAN(network.AP_IF)

AP.active(CONFIG.get("apActive"))
AP.ifconfig(("192.168.11.1", "255.255.255.0", "192.168.11.1", "8.8.8.8"))
AP.config(authmode = network.AUTH_WPA_WPA2_PSK)


try:
    AP.config(essid = CONFIG.get("apEssid"))
except Exception as e:
    logger.append(e)


try:
    AP.config(password = CONFIG.get("apPassword"))
except Exception as e:
    logger.append(e)


###########
## GENERAL

if CONFIG.get("watchdogActive"):
    WD = WDT()


# The REPL is attached by default to UART0, detach if not needed.
if not CONFIG.get("uartActive"):
    uos.dupterm(None, 1)


if CONFIG.get("webReplActive"):
    try:
        webrepl.start()
    except Exception as e:
        logger.append(e)


if CONFIG.get("webServerActive"):
    try:
        socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        socket.bind(("", 80))
        socket.listen(5)

        webserver.config(socket, CONFIG, executeJson)
        saveConfig()
        buzzer.keyBeep("beepAttention")
        buzzer.keyBeep("beepReady")
        webserver.start()
    except Exception as e:
        logger.append(e)

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

import esp, network, uasyncio, uos, uselect, webrepl

from machine     import Pin, UART
from ubinascii   import hexlify
from utime       import sleep_ms

import ubot_config    as config
import ubot_logger    as logger
import ubot_buzzer    as buzzer

buzzer.keyBeep("started")

if config.get("feedback", "active"):
    import ubot_feedback  as feedback

if config.get("motor", "active"):
    import ubot_motor as motor

if config.get("turtle", "active"):
    import ubot_turtle as turtle

if config.get("webServer", "active"):
    import ubot_webserver as webserver



################################
## PUBLIC METHODS

def executeCommand(command):
    if command[:6] == "PRESS_":
        pressedList = command[6:].strip().split(":")
        for pressed in pressedList:
            turtle.press(pressed)

    elif command[:5] == "STEP_":
        for char in command[5:].strip():
            turtle.move(char)

    elif command[:5] == "BEEP_":
        beepArray = command[5:].strip().split(":")
        size = len(beepArray)
        buzzer.beep(float(beepArray[0]) if size > 0 else 440.0,
                    int(beepArray[1]) if size > 1 else 100,
                    int(beepArray[2]) if size > 2 else 100,
                    int(beepArray[3]) if size > 3 else 1)

    elif command[:5] == "MIDI_":
        beepArray = command[5:].strip().split(":")
        size = len(beepArray)
        buzzer.midiBeep(int(beepArray[0]) if size > 0 else 69,
                        int(beepArray[1]) if size > 1 else 100,
                        int(beepArray[2]) if size > 2 else 100,
                        int(beepArray[3]) if size > 3 else 1)

    elif command[:5] == "REST_":
        buzzer.rest(int(command[5:].strip()))

    elif command[:4] == "MOT_":
        motor.move(int(command[4]), int(command[6:].strip()))

    elif command[:6] == "SLEEP_":
        sleep_ms(int(command[6:].strip()))

    return True


def doProgramAction(folder, title, action):
    try:
        if action == "run":
            turtle.loadProgramFromEeprom(folder, title)
            turtle.press(64)
            return "The program has started."
    except Exception as e:
        logger.append(e)
        return ""


################################
## PRIVATE METHODS FOR REST/JSON

def executeJson(path, json):
    if json.get("logging"):
        logger.append("Incoming JSON object. Title: {}".format(json.get("title")))
        logger.append(json)

    results = []

    if json.get("dateTime"):
        dateTime = json.get("dateTime")

        if len(dateTime) == 8:              # For classical tuple format
            config.datetime(dateTime)
        elif len(dateTime) == 2:            # For human readable format: ("yyyy-mm-dd", "hh:mm") or ("yyyy-mm-dd", "hh:mm:ss")
            date = dateTime[0].split("-")
            time = dateTime[1].split(":")
            seconds = int(time[2]) if 2 < len(time) else 0
            config.datetime((int(date[0]), int(date[1]), int(date[2]), 0, int(time[0]), int(time[1]), seconds, 0))

        results.append("New date and time has been set.")

    if json.get("service"):
        for command in json.get("service"):
            if command == "START UART":
                config.set("uart", "active", True)
                uos.dupterm(UART(0, 115200), 1)
                results.append("UART has started.")

            elif command == "STOP UART":
                config.set("uart", "active", False)
                uos.dupterm(None, 1)
                results.append("UART has stopped.")

            elif command == "START WEBREPL":
                config.set("webRepl", "active", True)
                webrepl.start()
                results.append("WebREPL has started.")

            elif command == "STOP WEBREPL":
                config.set("webRepl", "active", False)
                webrepl.stop()
                results.append("WebREPL has stopped.")

            elif command == "STOP WEBSERVER":
                webserver.stop()
                results.append("WebServer has stopped.")

    if len(results) == 0:
        results = ["Processing has completed without any return value."]
    if json.get("logging"):
        logger.append(results)

    return results


def _executeJsonGet(pathArray, isPresent, ignoredJson):      ########################################### JSON GET HANDLER
    if pathArray[0] == "program":                           # get or execution
        if True not in isPresent[4:]:
            if isPresent[1:4] == (True, True, True):        # action constant is present: info / run / ... (index: 3)
                return _jsonGetProgramAction(pathArray[1], pathArray[2], pathArray[3])
            elif isPresent[1:4] == (True, True, False):     # get the code of a specific program
                return _jsonGetProgramCode(pathArray[1], pathArray[2])
            elif True not in isPresent[2:]:                 # list a directory or the whole 'program' dir
                return _jsonGetProgramList(pathArray[1])

    elif pathArray[0] == "system":                          # only get
        if True not in isPresent[3:]:
            if isPresent[1] and isPresent[2]:
                return _jsonGetSystemAttribute(pathArray[1], pathArray[2])
            elif not (not isPresent[1] and isPresent[2]):
                return _jsonGetSystemAttributes(pathArray[1])

    elif pathArray[0] == "log":                             # only get
        if True not in isPresent[3:]:
            if isPresent[1] and isPresent[2]:
                return _jsonGetLog(pathArray[1], pathArray[2])
            elif not (not isPresent[1] and isPresent[2]):
                return _jsonGetLogList(pathArray[1])

    elif pathArray[0] == "command":                         # only execution
        if isPresent[1] and True not in isPresent[2:]:
            return _jsonGetCommandExecution(pathArray[1])

    return "403 Forbidden", "The format of the URI is invalid. More info: https://zza.hu/uBot_API", None


def _jsonGetProgramAction(folder, title, action):
    result = doProgramAction(folder, title, action)

    if result is not None and result != "":
        return "200 OK", "", result
    else:
        return "403 Forbidden", "The processing of the request failed. Cause: Semantic error in URI. " \
                                           "More info: https://zza.hu/uBot_API", None


def _jsonGetProgramCode(folder, title):
    result = turtle.getProgramCode(folder, title)

    if result is not None and result != ():
        return "200 OK", "", result
    else:
        return "404 Not Found", "The processing of the request failed. Cause: No such program. " \
                                           "More info: https://zza.hu/uBot_API", None


def _jsonGetProgramList(folder):
    result = _getProgramCatalog() if folder is None or folder == "" else turtle.getProgramList(folder)

    if result is not None and result != {}:                # Empty tuple is OK -> empty dir, but empty dictionary is not
        return "200 OK", "", result
    else:
        return "404 Not Found", "The processing of the request failed. Cause: 'Program' folder is not available. " \
                                           "More info: https://zza.hu/uBot_API", None


def _getProgramCatalog():
    programFolders = turtle.getProgramFolders()
    return {folder: turtle.getProgramList(folder) for folder in programFolders}


def _jsonGetSystemAttribute(module, attribute):
    result = config.get(module, attribute)

    if result is not None:
        return "200 OK", "", result
    else:
        return "404 Not Found", "The processing of the request failed. Cause: No such system attribute. " \
                                           "More info: https://zza.hu/uBot_API", None


def _jsonGetSystemAttributes(module):
    result = _getSystemInfo() if module is None or module == "" else _getModuleInfo(module)

    if result is not None and result != {}:
        return "200 OK", "", result
    else:
        return "404 Not Found", "The processing of the request failed. Cause: No such system module. " \
                                           "More info: https://zza.hu/uBot_API", None


def _getSystemInfo():
    modules = config.getModules()
    return {module: _getModuleInfo(module) for module in modules}


def _getModuleInfo(module):
    attributes = config.getModuleAttributes(module)
    return {attr: config.get(module, attr) for attr in attributes}


def _jsonGetLog(category, title):
    result = logger.getLog(category, title)

    if result is not None and result != ():                           # There should be an initialisation entry at least
        return "200 OK", "", result
    else:
        return "404 Not Found", "The processing of the request failed. Cause: No such log file. " \
                                           "More info: https://zza.hu/uBot_API", None


def _jsonGetLogList(category):
    result = _getLogCatalog() if category is None or category == "" else _getLogList(category)

    if result is not None and result != {}:                # Empty tuple is OK -> empty dir, but empty dictionary is not
        return "200 OK", "", result
    else:
        return "404 Not Found", "The processing of the request failed. Cause: No such log category. " \
                                           "More info: https://zza.hu/uBot_API", None


def _getLogCatalog():
    categories = logger.getLogCategories()
    return {category: _getLogList(category) for category in categories}


def _getLogList(category):
    return logger.getCategoryLogs(category)


def _jsonGetCommandExecution(command):
    if executeCommand(command.upper()):
        return "200 OK", "", "Processed commands: 1"
    else:
        return "403 Forbidden", "The processing of the request failed. Cause: Semantic error in URI. " \
                                           "More info: https://zza.hu/uBot_API", "Processed commands: 0"


def _executeJsonPost(pathArray, isPresent, json):            ########################################## JSON POST HANDLER
    if pathArray[0] == "program":                           # persistent
        if isPresent[1] and isPresent[2] and True not in isPresent[3:]:
            return _jsonPostProgram(pathArray[1], pathArray[2], json)
    elif pathArray[0] == "command":                         # temporary, only execution
        if True not in isPresent[1:]:
            return _jsonPostCommand(json)
    elif pathArray[0] == "root":                            # ONLY DURING DEVELOPMENT
        if True not in isPresent[1:]:
            return _jsonPostRoot(json)
    return "403 Forbidden", "The format of the URI is invalid. More info: https://zza.hu/uBot_API", None


def _jsonPostProgram(folder, title, json):
    program = json.get("data")
    if program is None or program == "":
        turtle.saveLoadedProgram(folder, title)
    else:
        turtle.saveProgram(program, folder, title)

    if turtle.isProgramExist(folder, title):
        return "201 Created", "", "http://{}/program/{}/{}".format(AP.ifconfig()[0], folder, title)
    else:
        return "422 Unprocessable Entity", "The processing of the request failed. Cause: Semantic error in JSON. " \
                                           "More info: https://zza.hu/uBot_API", None


def _jsonPostCommand(json):
    counter = 0
    try:
        for command in json.get("data"):
            if executeCommand(command):
                counter += 1
    except Exception as e:
        logger.append(e)

    if counter == len(json.get("data")):
        return "200 OK", "", "Processed commands: {}".format(counter)
    else:
        return "422 Unprocessable Entity", "The processing of the request failed. Cause: Semantic error in JSON. " \
                                           "More info: https://zza.hu/uBot_API", "Processed commands: {}".format(counter)


def _jsonPostRoot(json):
    results = []
    try:
        for command in json.get("data"):
            if command[0] == "EXEC":
                results.append("[EXEC] '{}' : void".format(exec(command[1])))
            elif command[0] == "EVAL":
                results.append("[EVAL] '{}' : '{}'".format(command[1], eval(command[1])))
    except Exception as e:
        logger.append(e)

    if len(results) == len(json.get("data")):
        return "200 OK", "", results
    else:
        return "422 Unprocessable Entity", "The processing of the request failed. Cause: Semantic error in JSON. " \
                                           "More info: https://zza.hu/uBot_API", results


def _executeJsonPut(pathArray, isPresent, json):             ########################################### JSON PUT HANDLER
    if pathArray[0] == "program":                           # persistent
        if isPresent[1] and isPresent[2] and True not in isPresent[3:]:
            return _jsonPutProgram(pathArray, isPresent, json)
    elif pathArray[0] == "system":                          # persistent
        if isPresent[1] and True not in isPresent[2:]:
            return _jsonPutSystemProperty(pathArray, isPresent, json)
    return "403 Forbidden", "The format of the URI is invalid. More info: https://zza.hu/uBot_API", None


def _jsonPutProgram(pathArray, isPresent, json):
    return "200 OK", "", _putProgram()


def _jsonPutSystemProperty(pathArray, isPresent, json):
    return "200 OK", "", _putSystemProp()


def _putProgram(directory, fileName, program):
    return ""


def _putSystemProp(property, value):
    return ""


def _executeJsonDelete(pathArray, isPresent, ignoredJson):   ######################################## JSON DELETE HANDLER
    if pathArray[0] == "program":                           # final
        if True not in isPresent[3:]:
            if isPresent[1:3] == (False, False):
                return _jsonDeleteEveryProgram()
            elif isPresent[1]:
                return _jsonClearProgramFolder(pathArray[1])
            elif isPresent[1] and isPresent[2]:
                return _jsonDeleteProgram(pathArray, isPresent)
    elif pathArray[0] == "log":                             # final
        if True not in isPresent[3:]:
            if isPresent[1:3] == (False, False):
                return _jsonDeleteEveryLog()
            elif isPresent[1]:
                return _jsonClearLogFolder(pathArray[1])
            elif isPresent[1] and isPresent[2]:
                return _jsonDeleteLog(pathArray, isPresent)
    return "403 Forbidden", "The format of the URI is invalid. More info: https://zza.hu/uBot_API", None


def _jsonDeleteEveryProgram():
    return "200 OK", "", _deleteProgram()


def _jsonClearProgramFolder(subDir):
    return "200 OK", "", _deleteProgram()


def _jsonDeleteProgram(pathArray, isPresent):
    return "200 OK", "", _deleteProgram()


def _jsonDeleteEveryLog():
    return "200 OK", "", _deleteLog()


def _jsonClearLogFolder(pathArray, isPresent):
    return "200 OK", "", _deleteLog()


def _jsonDeleteLog(pathArray, isPresent):
    return "200 OK", "", _deleteLog()


def _clearFolder(path):
    return ""


def _deleteProgram(directory, fileName):
    return ""


def _deleteLog(directory, fileName):
    return ""



################################
## INITIALISATION

esp.osdebug(None)
esp.sleep_type(esp.SLEEP_NONE)


###########
## GPIO

if not config.get("turtle", "active"):
    P13 = Pin(13, Pin.OUT)
    P16 = Pin(16, Pin.IN)   # MicroPython can not handle the pull-down resistor of the GPIO16: Use PULL physical switch.
    P13.off()


P12 = Pin(12, Pin.OUT)              # GPIO pin. On μBot turtle it can drive a LED if you switch physical switch on.
P14 = Pin(14, Pin.IN, Pin.PULL_UP)  # GPIO pin.
P12.off()


if not config.get("i2c", "active"):
    P0 = Pin(0, Pin.IN)
    P2 = Pin(2, Pin.IN)


if config.get("motor", "active"):
    motor.config(
        (
            (0, 0) if config.get("uart", "active") else (1, 3), # Right motor - T0
            (4, 5)                                              # Left motor  - T1
        ),
        (
            (config.get("motor", "T0Period"),       config.get("motor", "T0Duration")),
            (config.get("motor", "T1Frequency"),    config.get("motor", "T1Duty")),
            (config.get("motor", "T1DutyFactor"),   config.get("motor", "T1MinDuty"), config.get("motor", "T1MaxDuty")),
            config.get("motor", "breathLength")
        )
    )

if config.get("turtle", "active"):
    motor.setBreath(config.get("turtle", "breathLength"))

###########
## AP

AP = network.WLAN(network.AP_IF)

AP.active(config.get("ap", "active"))
AP.ifconfig(("192.168.11.1", "255.255.255.0", "192.168.11.1", "8.8.8.8"))
AP.config(authmode = network.AUTH_WPA_WPA2_PSK)


try:
    AP.config(essid = config.get("ap", "essid"))
except Exception as e:
    logger.append(e)


try:
    AP.config(password = config.get("ap", "password"))
except Exception as e:
    logger.append(e)


###########
## GENERAL

if config.get("feedback", "active"):
    feedback.start()


if not config.get("uart", "active"):    # The REPL is attached by default to UART0, detach if it is not active.
    uos.dupterm(None, 1)


if config.get("webRepl", "active"):
    try:
        webrepl.start()
    except Exception as e:
        logger.append(e)


if config.get("webServer", "active"):
    try:
        webserver.setJsonCallback("GET", _executeJsonGet)
        webserver.setJsonCallback("POST", _executeJsonPost)
        webserver.setJsonCallback("PUT", _executeJsonPut)
        webserver.setJsonCallback("DELETE", _executeJsonDelete)
        webserver.start()
    except Exception as e:
        logger.append(e)

buzzer.keyBeep("ready")

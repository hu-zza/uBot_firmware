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

import esp, network, uos, webrepl

from machine import Pin
from utime   import sleep_ms

import ubot_config as config
import ubot_logger as logger
import ubot_buzzer as buzzer
import ubot_structure as structure

buzzer.keyBeep("started")

if config.get("feedback", "active"):
    import ubot_feedback  as feedback

if config.get("motor", "active"):
    import ubot_motor as motor

if config.get("turtle", "active"):
    import ubot_turtle as turtle

if config.get("web_server", "active"):
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

    elif command[:6] == "DRIVE_":
        breath = motor.getBreath()
        motor.setBreath(0)
        for char in command[6:].strip():
            turtle.move(char, True)
        motor.setBreath(breath)

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
            return turtle.runProgram(folder, title), {}
    except Exception as e:
        logger.append(e)
    return False, {}


################################
## PRIVATE METHODS FOR REST/JSON

def _executeJsonGet(pathArray, isPresent, ignoredJson):     ########################################### JSON GET HANDLER
    secondImpliesFirst = not isPresent[2] or isPresent[1]
    if pathArray[0] == "":                                  ### GET
        return structure.createJsonInstanceFrom()

    elif pathArray[0] == "command":                         ### EXECUTION
        if isPresent[1] and not any(isPresent[2:]):
            return _jsonGetCommandExecution(pathArray[1])

    elif pathArray[0] == "etc":                             ### GET
        if not any(isPresent[3:]):
            if all(isPresent[1:3]):
                return _jsonGetEtcAttribute(pathArray[1], pathArray[2])
            elif isPresent[1]:
                return _jsonGetEtcModule(pathArray[1])
            elif not any(isPresent[1:]):
                return structure.createJsonInstanceFrom("etc")

    elif pathArray[0] == "log":                             ### GET
        if not any(isPresent[3:]):
            if all(isPresent[1:3]):
                return _jsonGetLog(pathArray[1], pathArray[2])
            elif isPresent[1]:
                return structure.createJsonInstanceFrom("log", pathArray[1])
            elif not any(isPresent[1:]):
                return structure.createJsonInstanceFrom("log")

    elif pathArray[0] == "program":                        ### GET or EXECUTION
        if not any(isPresent[4:]):
            if all(isPresent[1:4]):                         # program / <folder> / <title> / <action>
                return _jsonGetStartProgramAction(pathArray[1], pathArray[2], pathArray[3])
            elif all(isPresent[1:3]):                       # program / <folder> / <title>
                return _jsonGetProgram(pathArray[1], pathArray[2])
            elif isPresent[1]:                              # program / <folder>
                return _jsonGetFolder(pathArray[1])
            elif not any(isPresent[1:]):                    # program
                structure.createJsonInstanceFrom("log")

    elif pathArray[0] == "raw":                             ### GET
        if not any(isPresent[4:]):
            return structure.createJsonInstanceFrom(pathArray[1], pathArray[2], pathArray[3])

    return "403 Forbidden", "Job: [REST] GET request. Cause: The format of the URI is invalid.", {}


def _jsonGetStartProgramAction(folder, title, action):
    result = doProgramAction(folder, title, action)
    job = "Request: Starting action '{}' of program '{}' ({}).".format(action, title, folder)

    if result[0]:
        return "200 OK", job, result[1]
    else:
        return "403 Forbidden", job + " Cause: Semantic error in URI.", {}


def _jsonGetProgram(folder, title):
    job = "Request: Get the program '{}' ({}).".format(title, folder)

    if turtle.doesProgramExist(folder, title):
        programCode = turtle.getProgramCode(folder, title)

        return "200 OK", job, {
            "name": title,
            "type": "program",
            "href": "{}{}/{}".format(_programDirLink, folder, title),
            "raw":  "{}{}/{}.txt".format(_programRawDirLink, folder, title),
            "parent": {
                "name": folder,
                "type": "folder",
                "href": "{}{}".format(_programDirLink, folder),
                "raw":  "{}{}".format(_programRawDirLink, folder)
            },
            "children": [],
            "code": programCode,
            "action": {
                "run": "{}{}/{}/run".format(_programDirLink, folder, title)
            }}
    else:
        return "404 Not Found", job + " Cause: No such program.", {}


def _jsonGetFolder(folder):
    job = "Request: Get the folder '{}'.".format(folder)

    if turtle.doesFolderExist(folder):
        children = [{"name": program, "type": "program", "href": "{}{}/{}".format(_programDirLink, folder, program),
                    "raw": "{}{}/{}.txt".format(_programRawDirLink, folder, program)}
                    for program in turtle.getProgramList(folder)]

        return "200 OK", job, {
            "name": folder,
            "type": "folder",
            "href": "{}{}/".format(_programDirLink, folder),
            "raw":  "{}{}/".format(_programRawDirLink, folder),
            "parent": {
                "name": "program",
                "type": "folder",
                "href": _programDirLink,
                "raw":  _programRawDirLink
            },
            "children": children}
    else:
        return "404 Not Found", job + " Cause: No such program folder.", {}


def _jsonGetEtcAttribute(module, attribute):
    job = "Request: Get the system attribute '{}' ({}).".format(attribute, module)

    if config.doesAttributeExist(module, attribute):
        value = config.get(module, attribute)

        return "200 OK", job, {
            "name": attribute,
            "type": "attribute",
            "href": "{}{}/{}".format(_etcDirLink, module, attribute),
            "raw":  "{}{}/{}.txt".format(_etcRawDirLink, module, attribute),
            "parent": {
                "name": module,
                "type": "folder",
                "href": "{}{}".format(_etcDirLink, module),
                "raw":  "{}{}".format(_etcRawDirLink, module)
            },
            "children": [],
            "value": value}
    else:
        return "404 Not Found", job + " Cause: No such system attribute.", {}


def _jsonGetEtcModule(module):
    job = "Request: Get the folder '{}'.".format(module)

    if config.doesModuleExist(module):
        children = [{"name": attribute, "type": "attribute", "href": "{}{}/{}".format(_etcDirLink, module, attribute),
                     "raw": "{}{}/{}.txt".format(_etcRawDirLink, module, attribute)}
                    for attribute in config.getModuleAttributes(module)]

        return "200 OK", job, {
            "name": module,
            "type": "folder",
            "href": "{}{}/".format(_etcDirLink, module),
            "raw":  "{}{}/".format(_etcRawDirLink, module),
            "parent": {
                "name": "etc",
                "type": "folder",
                "href": _etcDirLink,
                "raw":  _etcRawDirLink
            },
            "children": children}
    else:
        return "404 Not Found", job + " Cause: No such system folder.", {}


def _jsonGetLog(category, title):
    result = logger.getLog(category, title)

    if result is not None and result != ():                           # There should be an initialisation entry at least
        return "200 OK", "", result
    else:
        return "404 Not Found", "The processing of the request failed. Cause: No such log file.", {}


def _jsonGetCommandExecution(command):
    if executeCommand(command.upper()):
        return "200 OK", "", "Processed commands: 1"
    else:
        return "403 Forbidden", "The processing of the request failed. Cause: Semantic error in URI.", {}



def _executeJsonPost(pathArray, isPresent, json):           ########################################## JSON POST HANDLER
    if pathArray[0] == "program":                           ### persistent
        if all(isPresent[1:3]) and not any(isPresent[3:]):
            return _jsonPostProgram(pathArray[1], pathArray[2], json)
    elif pathArray[0] == "command":                         ### temporary, only execution
        if not any(isPresent[1:]):
            return _jsonPostCommand(json)
    elif pathArray[0] == "root":                            ### ONLY DURING DEVELOPMENT
        if not any(isPresent[1:]):
            return _jsonPostRoot(json)
    return "403 Forbidden", "Job: [REST] POST request. Cause: The format of the URI is invalid.", {}


def _jsonPostProgram(folder, title, json):
    program = json.get("data")
    if program is None or program == "":
        turtle.saveLoadedProgram(folder, title)
    else:
        turtle.saveProgram(program, folder, title)

    if turtle.doesProgramExist(folder, title):
        return "201 Created", "", "http://{}/program/{}/{}".format(AP.ifconfig()[0], folder, title)
    else:
        return "422 Unprocessable Entity", "The processing of the request failed. Cause: Semantic error in JSON.", {}


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
        return "422 Unprocessable Entity", "The processing of the request failed. Cause: Semantic error in JSON.",\
               "Processed commands: {}".format(counter)


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
        return "422 Unprocessable Entity", "The processing of the request failed. Cause: Semantic error in JSON.", results



def _executeJsonPut(pathArray, isPresent, json):            ########################################### JSON PUT HANDLER
    if pathArray[0] == "program":                           ### persistent
        if isPresent[1] and isPresent[2] and True not in isPresent[3:]:
            return _jsonPutProgram(pathArray, isPresent, json)
    elif pathArray[0] == "etc":                             ### persistent
        if isPresent[1] and True not in isPresent[2:]:
            return _jsonPutSystemProperty(pathArray, isPresent, json)
    return "403 Forbidden", "Job: [REST] PUT request. Cause: The format of the URI is invalid.", {}


def _jsonPutProgram(pathArray, isPresent, json):
    return "200 OK", "", _putProgram()


def _jsonPutSystemProperty(pathArray, isPresent, json):
    return "200 OK", "", _putSystemProp()


def _putProgram(directory, fileName, program):
    return ""


def _putSystemProp(property, value):
    return ""



def _executeJsonDelete(pathArray, isPresent, ignoredJson):  ######################################## JSON DELETE HANDLER
    if pathArray[0] == "program":                           ### final
        if True not in isPresent[3:]:
            if isPresent[1:3] == (False, False):
                return _jsonDeleteEveryProgram()
            elif isPresent[1]:
                return _jsonClearProgramFolder(pathArray[1])
            elif isPresent[1] and isPresent[2]:
                return _jsonDeleteProgram(pathArray, isPresent)
    elif pathArray[0] == "log":                             ### final
        if True not in isPresent[3:]:
            if isPresent[1:3] == (False, False):
                return _jsonDeleteEveryLog()
            elif isPresent[1]:
                return _jsonClearLogFolder(pathArray[1])
            elif isPresent[1] and isPresent[2]:
                return _jsonDeleteLog(pathArray, isPresent)
    return "403 Forbidden", "Job: [REST] DELETE request. Cause: The format of the URI is invalid.", {}


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

AP = config.getAp()

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
## JSON VAR

_hostLink = "http://{}/".format(AP.ifconfig()[0])
_rawLink  = _hostLink + "raw/"

_programDirLink    = _hostLink + "program/"
_programRawDirLink = _rawLink  + "program/"

_etcDirLink    = _hostLink + "etc/"
_etcRawDirLink = _rawLink  + "etc/"

_logDirLink    = _hostLink + "log/"
_logRawDirLink = _rawLink  + "log/"

###########
## GENERAL

if config.get("feedback", "active"):
    feedback.start()


if not config.get("uart", "active"):    # The REPL is attached by default to UART0, detach if it is not active.
    uos.dupterm(None, 1)


if config.get("web_repl", "active"):
    try:
        webrepl.start()
    except Exception as e:
        logger.append(e)


if config.get("web_server", "active"):
    try:
        webserver.setJsonCallback("GET", _executeJsonGet)
        webserver.setJsonCallback("POST", _executeJsonPost)
        webserver.setJsonCallback("PUT", _executeJsonPut)
        webserver.setJsonCallback("DELETE", _executeJsonDelete)
        webserver.start()
    except Exception as e:
        logger.append(e)

buzzer.keyBeep("ready")

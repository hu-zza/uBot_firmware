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

from machine import Pin, Timer
from utime   import sleep_ms

import ubot_config as config
import ubot_logger as logger
import ubot_buzzer as buzzer
import ubot_data   as data

buzzer.keyBeep("started")

if config.get("feedback", "active"):
    import ubot_feedback  as feedback

if config.get("motor", "active"):
    import ubot_motor as motor

if config.get("turtle", "active"):
    import ubot_turtle as turtle

if config.get("web_server", "active"):
    import ubot_webserver as webserver

_timer = Timer(-1)
_workIndicatorFunction = None
_resultSupplierFunction = None

################################
## PUBLIC METHODS


def executeCommand(command):
    if command[:5] == "PRESS":                                      # PRESS_1_1_16_64
        pressedList = extractIntTupleFromString(command[5:])
        for pressed in pressedList:
            turtle.press(pressed)

    elif command[:4] == "STEP":                                     # STEP_FFR
        commands = extractCharTupleFromString(command[4:], turtle.getValidMoveChars())
        for char in commands:
            turtle.move(char)

    elif command[:5] == "DRIVE":                                    # DRIVE_FFR
        breath = motor.getBreath()
        motor.setBreath(0)
        commands = extractCharTupleFromString(command[5:], turtle.getValidMoveChars())
        turtle.skipSignal(len(commands), 1)
        for char in commands:
            turtle.move(char)
        motor.setBreath(breath)

    elif command[:4] == "BEEP":                                     # BEEP_440_100_100_1
        beepArray = extractIntTupleFromString(command[4:])
        size = len(beepArray)
        buzzer.beep(float(beepArray[0]) if size > 0 else 440.0,
                    int(beepArray[1]) if size > 1 else 100,
                    int(beepArray[2]) if size > 2 else 100,
                    int(beepArray[3]) if size > 3 else 1)

    elif command[:4] == "MIDI":                                     # MIDI_69_100_100_1
        beepArray = extractIntTupleFromString(command[4:])
        size = len(beepArray)
        buzzer.midiBeep(int(beepArray[0]) if size > 0 else 69,
                        int(beepArray[1]) if size > 1 else 100,
                        int(beepArray[2]) if size > 2 else 100,
                        int(beepArray[3]) if size > 3 else 1)

    elif command[:4] == "REST":                                     # REST_1000
        inp = extractIntTupleFromString(command[4:])
        buzzer.rest(inp[0] if inp != () else 1000)

    elif command[:3] == "MOT":                                      # MOT_1_1000
        inp = extractIntTupleFromString(command[3:])
        length = len(inp)
        direction = inp[0] if 0 < length else 1
        length = inp[1] if 1 < length else 1000

        motor.move(direction, length)

    elif command[:5] == "SLEEP":                                    # SLEEP_1000
        inp = extractIntTupleFromString(command[5:])
        sleep_ms(inp[0] if inp != () else 1000)

    else:
        return False
    waitForExecution(turtle.isBusy)


def doProgramAction(folder, title, action):
    action = action.lower()
    try:
        if action == "run":
            return turtle.runProgram(folder, title), {}
    except Exception as e:
        logger.append(e)
    return False, {}


def extractIntTupleFromString(tupleString):
    result = []
    current  = 0
    unsaved  = False

    for char in tupleString:
        if char.isdigit():
            current *= 10
            current += int(char)
            unsaved = True
        elif unsaved:
            result.append(current)
            current = 0
            unsaved = False

    if unsaved:
        result.append(current)

    return tuple(result)


def extractCharTupleFromString(tupleString, enabledCharsSet):
    return tuple([char for char in tupleString if char in enabledCharsSet])


def waitForExecution(workIndicatorFunction, resultSupplierFunction = None):
    global _workIndicatorFunction
    global _resultSupplierFunction

    _workIndicatorFunction = workIndicatorFunction
    _resultSupplierFunction = resultSupplierFunction
    _waitForFalse()


def _waitForFalse(timer = None):
    if _workIndicatorFunction():
        _timer.init(
            period = 1000,
            mode = Timer.ONE_SHOT,
            callback = _waitForFalse
        )
    else:
        return True if _resultSupplierFunction is None else _resultSupplierFunction()



################################
## PRIVATE METHODS FOR REST/JSON

def _executeJsonGet(pathArray, isPresent, ignoredJson):     ########################################### JSON GET HANDLER
    if pathArray[0] == "raw":
        return data.createRestReplyFrom(pathArray[1], pathArray[2], pathArray[3])
    elif pathArray[0] == "program" and all(isPresent[1:4]):
        return _jsonGetProgramActionStarting(pathArray[1], pathArray[2], pathArray[3])
    elif pathArray[0] == "command":
        return _jsonGetCommandExecution(pathArray[1])
    else:
        return data.createRestReplyFrom(pathArray[0], pathArray[1], pathArray[2])


def _jsonGetProgramActionStarting(folder, title, action):
    job = "Request: Starting action '{}' of program '{}' ({}).".format(action, title, folder)
    if turtle.doesProgramExist(folder, title):
        result = doProgramAction(folder, title, action)

        if result[0]:
            status, message, json = data.createRestReplyFrom("program", folder, title)
            json["result"] = result[1]

            return status, "{} <- {}".format(job, message), json
        else:
            return "403 Forbidden", job + " Cause: Semantic error in the URL.", {}
    else:
        return "404 Not Found", job + " Cause: No such program.", {}


def _jsonGetCommandExecution(command):
    command = command.upper()
    job = "Request: Starting command '{}' execution.".format(command)
    try:
        if executeCommand(command):
            return "200 OK", job, {"name": command, "type": "command", "result": "started",
                                   "href": "http://{}/command/{}".format(config.get("ap", "ip"), command)}
    except Exception:
        pass
    return "403 Forbidden", job + " Cause: Semantic error in the URL.", {}



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
    return "403 Forbidden", "Job: [REST] POST request. Cause: The format of the URL is invalid.", {}


def _jsonPostProgram(folder, title, json):
    program = json.get("data")
    if program is None or program == "":
        turtle.saveLoadedProgram(folder, title)
    else:
        turtle.saveProgram(program, folder, title)

    if turtle.doesProgramExist(folder, title):
        return "201 Created", "", "http://{}/program/{}/{}".format(config.get("ap", "ip"), folder, title)
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
    return "403 Forbidden", "Job: [REST] PUT request. Cause: The format of the URL is invalid.", {}


def _jsonPutProgram(pathArray, isPresent, json):
    return "200 OK", "", _putProgram()


def _jsonPutSystemProperty(pathArray, isPresent, json):
    return "200 OK", "", _putSystemProp()


def _putProgram(folder, fileName, program):
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
    return "403 Forbidden", "Job: [REST] DELETE request. Cause: The format of the URL is invalid.", {}


def _jsonDeleteEveryProgram():
    return "200 OK", "", _deleteProgram()


def _jsonClearProgramFolder(subFolder):
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


def _deleteProgram(folder, fileName):
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
            (config.get("motor", "t0_period"),       config.get("motor", "t0_duration")),
            (config.get("motor", "t1_frequency"),    config.get("motor", "t1_duty")),
            (config.get("motor", "t1_factor"),       config.get("motor", "t1_min_duty"), config.get("motor", "t1_max_duty")),
            config.get("motor", "breath_length")
        )
    )

if config.get("turtle", "active"):
    motor.setBreath(config.get("turtle", "breath_length"))

###########
## AP

_ap = network.WLAN(network.AP_IF)

_ap.active(config.get("ap", "active"))
_ap.ifconfig((config.get("ap", "ip"), config.get("ap", "netmask"), config.get("ap", "gateway"), config.get("ap", "dns")))
_ap.config(authmode = network.AUTH_WPA_WPA2_PSK)


try:
    _ap.config(essid = config.get("ap", "ssid"))
except Exception as e:
    logger.append(e)


try:
    _ap.config(password = config.get("ap", "password"))
except Exception as e:
    logger.append(e)

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

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
import esp, network, ujson, uos, webrepl

from machine import Pin
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
    return True


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
    return tuple(char for char in tupleString if char in enabledCharsSet)



################################
## PRIVATE METHODS FOR REST/JSON

_jsonRequest = {                                                                        ########## JSON REQUEST HANDLING
    "path": tuple(),
    "present": 0,
    "body": "",
    "parsed": False,
    "exception": []
}


def _updateJsonRequest(path = "", body = ""):
    global _jsonRequest

    array = [item for item in path.split("/") if item != ""]

    _jsonRequest["present"] = len(array)

    array += [""] * (10 - len(array))           # add placeholders to prevent IndexError

    _jsonRequest["path"] = tuple(array)
    _jsonRequest["body"] = body
    _jsonRequest["parsed"] = False
    _jsonRequest["exception"] = []


def _parseJsonRequestBody():
    try:
        _jsonRequest["body"] = ujson.loads(_jsonRequest.get("body"))
        _jsonRequest["parsed"] = True
    except Exception as e:
        logger.append(e)
        _jsonRequest["exception"].append(data.dumpException(e))
        _jsonRequest["parsed"] = False


def _jsonBodyValidator(job, obligatoryParameters = ("value",)):                               ########## GENERAL HELPERS
    if _jsonRequest.get("parsed"):
        body = _jsonRequest.get("body")
        if all(body.get(item) is not None for item in obligatoryParameters):
            return "200 OK", job, {}
        else:
            return "403 Forbidden", "{} Cause: The request body is present and parsed, but incomplete.".format(job), {}
    else:
        return "400 Bad Request", "{} Cause: The request body could not be parsed.".format(job), {}


def _jsonReplyWithFileInstance(job, path):
    if path != "":
        pathArray = path.split("/")
        jobGist = job[:job.find("'")]
        job = "{}'{}' ({}).".format(jobGist, pathArray[3], pathArray[2])
        savedProgram = _jsonGetFileOfPath(pathArray[1:4])

        if savedProgram[0] == "200 OK":
            return "200 OK", job, savedProgram[2]
        else:
            return "500 Internal Server Error", "{} Cause: The file system is not available.".format(job), {}
    else:
        return "422 Unprocessable Entity", "{} Cause: Semantic error in JSON.".format(job), {}


def _jsonGetFileOfPath(path):
    return data.createRestReplyFrom(path[0], path[1], path[2])


def _executeJsonGet():                                                                       ########## JSON GET HANDLER
    if _jsonRequest.get("present") < 5:
        category = _jsonRequest.get("path")[0]
        if category == "program" and _jsonRequest.get("present") == 4:
            return _jsonGetProgramActionStarting()
        else:
            result = _jsonGetFunctions.setdefault(category, _jsonGetFileByJsonLink)()
            if result is not None and result != ():
                return result

    return "403 Forbidden", "Job: [REST] GET request. Cause: The format of the URL is invalid.", {}


def _jsonGetProgramActionStarting():
    folder, title, action = _jsonRequest.get("path")[1:4]
    
    job = "Request: Starting action '{}' of program '{}' ({}).".format(action, title, folder)

    if turtle.doesProgramExist(folder, title):
        result = doProgramAction(folder, title, action)

        if result[0]:
            return "200 OK", job, result[1]
        else:
            return "403 Forbidden", "{} Cause: Semantic error in the URL.".format(job), {}
    else:
        return "404 Not Found", "{} Cause: No such program.".format(job), {}


def _jsonGetFileByRawLink():                                                                  # TODO: real raw for files
    return _jsonGetFileOfPath(_jsonRequest.get("path")[1:4])


def _jsonGetFileByJsonLink():
    return _jsonGetFileOfPath(_jsonRequest.get("path")[0:3])


def _jsonGetCommandExecution():
    command = _jsonRequest.get("path")[1].upper()
    job = "Request: Starting command '{}' execution.".format(command)
    try:
        if executeCommand(command):
            return "200 OK", job, {"name": command, "type": "command", "result": "started",
                                   "href": "http://{}/command/{}".format(config.get("ap", "ip"), command)}
    except Exception:
        pass
    return "403 Forbidden", "{} Cause: Semantic error in the URL.".format(job), {}


_jsonGetFunctions = {
    "command": _jsonGetCommandExecution,
    "raw":     _jsonGetFileByRawLink,
}


def _executeJsonPost():                                                                     ########## JSON POST HANDLER
    if 0 < _jsonRequest.get("present") < 4:
        _parseJsonRequestBody()
        category = _jsonRequest.get("path")[0]

        if category in config.get("data", "write_rights"):
            if category == "program":
                return _jsonPostProgram()
            elif _jsonRequest.get("present") == 3:
                return _jsonPostFile()


        if _jsonRequest.get("present") == 1:
            if category in _jsonPostFunctions.keys():
                return _jsonPostFunctions.get(category)()

    return "403 Forbidden", "Job: [REST] POST request. Cause: The format of the URL is invalid.", {}


def _jsonPostProgram():
    folder, title = _jsonRequest.get("path")[1:3]
    title = data.normalizeTxtFilename(title)

    job = "Request: Save program '{}' ({}).".format(title, folder)
    if not turtle.doesProgramExist(folder, title):
        return _jsonWriteProgram(folder, title, job)
    else:
        return "403 Forbidden", "{} Cause: The program already exists.".format(job), {}


def _jsonWriteProgram(folder, title, job):
    body = _jsonRequest.get("body")
    if body == "":
        path = turtle.saveLoadedProgram(folder, title)
    else:
        result = _jsonBodyValidator(job)
        if result[0] != "200 OK":
            return result

        path = turtle.saveProgram(folder, title, body.get("value"))
    return _jsonReplyWithFileInstance(job, path)


def _jsonPostFile():
    category, folder, title = _jsonRequest.get("path")[0:3]
    title = data.normalizeTxtFilename(title)

    job = "Request: Save file '{}' ({}).".format(title, folder)
    path = data.getNormalizedPathOf((category, folder), title)
    if not data.doesExist(path):
        return _jsonWriteFile(job, path)
    else:
        return "403 Forbidden", "{} Cause: The file already exists.".format(job), {}


def _jsonWriteFile(path, job):
    result = _jsonBodyValidator(job)
    if result[0] != "200 OK":
        return result

    body = _jsonRequest.get("body")
    file = ujson.dumps(body.get("value")) if body.get("isJson") is True else body.get("value")
    path = path if data.saveFileOfPath(path, file, True) else ""

    return _jsonReplyWithFileInstance(job, path)


def _jsonPostCommand():
    job = "Request: Starting commands execution."

    result = _jsonBodyValidator(job)
    if result[0] != "200 OK":
        return result

    commandArray = _jsonRequest.get("body").get("value")
    counter, commandCount = 0, -1
    try:
        commandCount = len(commandArray)
        for command in commandArray:
            counter += 1 if executeCommand(command) else 0
    except Exception as e:
        logger.append(e)

    if counter == commandCount:
        return "200 OK", job, counter
    else:
        return "422 Unprocessable Entity", "{} Cause: Semantic error in JSON.".format(job), {}


def _jsonPostLog():
    job = "Request: Send log for processing."

    if config.get("logger", "active"):
        result = _jsonBodyValidator(job)
        if result[0] != "200 OK":
            return result

        log = _jsonRequest.get("body").get("value")

        logFile = "event" if isinstance(log, str) else "object"
        if logFile in config.get("logger", "active_logs"):
            logger.append(log)
            status, message, json = _jsonGetFileOfPath(("log", logFile, config.get("system", "power_ons")))

            if status == "200 OK":
                return "200 OK", job, json
            else:
                return "500 Internal Server Error", "{} Cause: The file system is not available.".format(job), {}
        else:
            return "403 Forbidden", "{} Cause: The log '{}' is inactive.".format(job, logFile), {}
    else:
        return "403 Forbidden", "{} Cause: The logger module is inactive.".format(job), {}


def _jsonPostRoot():
    if config.get("system", "root"):
        job = "Request: Starting MicroPython commands execution."

        result = _jsonBodyValidator(job, ("value", "chk"))
        if result[0] == "200 OK":
            body = _jsonRequest.get("body")

            if body.get("chk") == config.get("system", "chk"):
                commands = body.get("value")
                results = []
                try:
                    for command in commands:
                        if command[0] == "EXEC":
                            results.append("[EXEC] {} : {}".format(command[1], exec(command[1])))
                        elif command[0] == "EVAL":
                            results.append("[EVAL] {} : {}".format(command[1], eval(command[1])))
                except Exception as e:
                    logger.append(e)

                if len(results) == len(commands):
                    return "200 OK", job, results
                else:
                    return "422 Unprocessable Entity", "{} Cause: Semantic error in JSON.".format(job), results
    return "403 Forbidden", "Job: [REST] POST request. Cause: The format of the URL is invalid.", {}


_jsonPostFunctions = {
    "command": _jsonPostCommand,
    "log":     _jsonPostLog,
    "root":    _jsonPostRoot
}


def _executeJsonPut():                                                                       ########## JSON PUT HANDLER
    if _jsonRequest.get("present") == 3:
        _parseJsonRequestBody()
        return _jsonPutFile()

    return "403 Forbidden", "Job: [REST] PUT request. Cause: The format of the URL is invalid.", {}


def _jsonPutFile():
    category, folder, title = _jsonRequest.get("path")[0:3]
    title = data.normalizeTxtFilename(title)

    job = "Request: Modify file '{}' ({}).".format(title, folder)
    if category in config.get("data", "write_rights") or category == "etc" and folder in config.get("data", "modify_rights"):

        path = data.getNormalizedPathOf((category, folder), title)

        if data.doesExist(path):
            return _jsonWriteFile(job, path)
        else:
            return "403 Forbidden", "{} Cause: The file doesn't exist.".format(job), {}
    else:
        return "403 Forbidden", "{} Cause: The file can not be modified.".format(job), {}



def _executeJsonDelete():                                                                 ########## JSON DELETE HANDLER
    if 0 < _jsonRequest.get("present") < 4:
        category = _jsonRequest.get("path")[0]

        if category in config.get("data", "clean_rights"):
            return _jsonDelete()

    return "403 Forbidden", "Job: [REST] DELETE request. Cause: The format of the URL is invalid.", {}


def _jsonDelete():
    pass



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
        if config.get("web_server", "json_enabled"):
            webserver.setJsonSender(_updateJsonRequest)
            webserver.setJsonCallback("GET", _executeJsonGet)
            webserver.setJsonCallback("POST", _executeJsonPost)
            #webserver.setJsonCallback("PUT", _executeJsonPut)
            #webserver.setJsonCallback("DELETE", _executeJsonDelete)
        webserver.start()
    except Exception as e:
        logger.append(e)

buzzer.keyBeep("ready")

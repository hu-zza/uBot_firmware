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
import ubot_data   as data
import ubot_buzzer as buzzer
import ubot_future as future

buzzer.keyBeep("started")

if config.get("feedback", "active"):
    import ubot_feedback  as feedback

if config.get("motor", "active"):
    import ubot_motor as mot

if config.get("turtle", "active"):
    import ubot_turtle as turtle

if config.get("web_server", "active"):
    import ubot_webserver as webserver


################################
## PUBLIC METHODS

powerOns = config.get("system", "power_ons")

def printEvents(nr: int = -1) -> None:
    logger.printLog("event", powerOns if nr < 0 else nr)


def printExceptions(nr: int = -1) -> None:
    logger.printLog("exception", powerOns if nr < 0 else nr)


def printObjects(nr: int = -1) -> None:
    logger.printLog("object", powerOns if nr < 0 else nr)


def printRuns(nr: int = -1) -> None:
    logger.printLog("run", powerOns if nr < 0 else nr)


def executeCommandList(commands: tuple) -> tuple:
    counter = 0
    try:
        for command in commands:
            if executeCommand(command):
                counter += 1
            else:
                break
    except Exception as e:
        logger.append(e)

    return counter == len(commands), counter


_commandsByLength = {
    5: {"DRIVE", "MOTOR", "PRESS", "SLEEP"},
    4: {"BEEP", "MIDI", "REST", "STEP", "TIME"}
}

def executeCommand(command: str) -> bool:
    try:
        length = 5
        while 0 < length:
            if command[:length] in _commandsByLength.get(length):
                _commandFunctions.get(command[:length])(command[length:])
                return True

            length -= 1

        return False
    except Exception as e:
        logger.append(e)
        return False


def beep(args: str):    # BEEP_440_100_100_1
    beepArray = data.extractIntTupleFromString(args, 4)
    size = len(beepArray)
    buzzer.beep(float(beepArray[0]) if size > 0 else 440.0,
                beepArray[1] if size > 1 else 100,
                beepArray[2] if size > 2 else 100,
                beepArray[3] if size > 3 else 1)


def drive(args: str):   # DRIVE_FFR
    breath = mot.getBreath()
    mot.setBreath(0)
    commands = data.extractCharTupleFromString(args, turtle.getValidMoveChars())
    turtle.skipSignal(len(commands), 1)
    for char in commands:
        turtle.move(char)
    mot.setBreath(breath)


def midi(args: str):    # MIDI_69_100_100_1
    beepArray = data.extractIntTupleFromString(args, 4)
    size = len(beepArray)
    buzzer.midiBeep(beepArray[0] if size > 0 else 69,
                    beepArray[1] if size > 1 else 100,
                    beepArray[2] if size > 2 else 100,
                    beepArray[3] if size > 3 else 1)


def motor(args: str):  # MOT_1_1000
    inp = data.extractIntTupleFromString(args, 2)
    length = len(inp)
    direction = inp[0] if 0 < length else 1
    length = inp[1] if 1 < length else 1000

    mot.move(direction, length)


def press(args: str):   # PRESS_1_1_16_64
    pressedList = data.extractIntTupleFromString(args)
    for pressed in pressedList:
        turtle.press(pressed)


def rest(args: str):    # REST_1000
    inp = data.extractIntTupleFromString(args, 1)
    buzzer.rest(inp[0] if inp != () else 1000)


def sleep(args: str):   # SLEEP_1000
    inp = data.extractIntTupleFromString(args, 1)
    sleep_ms(inp[0] if inp != () else 1000)


def step(args: str):    # STEP_FFR
    commands = data.extractCharTupleFromString(args, turtle.getValidMoveChars())
    for char in commands:
        turtle.move(char)


def time(args: str):    # TIME_2020-02-02_20:20:20:200
    inp = data.extractIntTupleFromString(args, 7)
    if 2 < len(inp):
        inp = list(inp)
        inp.insert(3, 0)   # Insert week day nr at position 3, it's calculated by MicroPython either way, so 0 is OK
        inp += [0] * (8 - len(inp))
        config.datetime(inp)
    else:
        config.datetime()


_commandFunctions = {
    "BEEP"  : beep,     # BEEP_440_100_100_1
    "DRIVE" : drive,    # DRIVE_FFR
    "MIDI"  : midi,     # MIDI_69_100_100_1
    "MOTOR" : motor,    # MOT_1_1000
    "PRESS" : press,    # PRESS_1_1_16_64
    "REST"  : rest,     # REST_1000
    "SLEEP" : sleep,    # SLEEP_1000
    "STEP"  : step,     # STEP_FFR
    "TIME"  : time      # TIME_2020-02-02_20:20:20:200
}


################################
## PRIVATE METHODS FOR REST/JSON

_jsonRequest = {                                                                        ########## JSON REQUEST HANDLING
    "path": data.INVALID_PATH,
    "body": "",
    "parsed": False
}


def _updateJsonRequest(path: data.Path, body: str = "", parsed: bool = False) -> None:
    global _jsonRequest

    _jsonRequest["path"] = path
    _jsonRequest["body"] = body
    _jsonRequest["parsed"] = parsed


def _parseJsonRequestBody() -> None:
    try:
        body = _jsonRequest.get("body")
        if body == "":
            _jsonRequest["parsed"] = False
        else:
            _jsonRequest["body"] = ujson.loads(body)
            _jsonRequest["parsed"] = True
    except Exception as e:
        logger.append(e)
        _jsonRequest["parsed"] = False


def _jsonBodyValidator(job: str, obligatoryParameters: tuple = ("value",)) -> tuple:          ########## GENERAL HELPERS
    if _jsonRequest.get("parsed"):
        body = _jsonRequest.get("body")
        if all(body.get(item) is not None for item in obligatoryParameters):
            return "200 OK", job, {}
        else:
            return "403 Forbidden", "{} Cause: The request body is present and parsed, but incomplete.".format(job), {}
    else:
        return "400 Bad Request", "{} Cause: The request body could not be parsed.".format(job), {}


def _jsonReplyWithFileInstance(path: data.Path, job: str) -> tuple:
    if path.isExist:
        savedProgram = data.createRestReply(path)

        if savedProgram[0] == "200 OK":
            return "200 OK", job, savedProgram[2]
        else:
            return "500 Internal Server Error", "{} Cause: The file system is not available.".format(job), {}
    else:
        return "422 Unprocessable Entity", "{} Cause: Semantic error in JSON.".format(job), {}


def _executeJsonGet() -> tuple:                                                              ########## JSON GET HANDLER
    path = _jsonRequest.get("path")
    args = path.args

    if 0 < len(path.args):
        function = _actionFunctions.get(args[0])
        if function is not None:
            return _actionFunctions.get(args[0])()
    else:
        return _jsonGetFileByJsonLink()

    return "403 Forbidden", "Request: REST GET. Cause: The format of the URL is invalid.", {}


def _jsonGetFileByJsonLink() -> tuple:
    return data.createRestReply(_jsonRequest.get("path"))


def _jsonGetProgramActionStarting() -> tuple:
    path = _jsonRequest.get("path")
    folder, title = path.array[1:3]

    job = "Request: Starting action '{}' of program '{}' ({}).".format(path.args[1], title, folder)

    if turtle.doesProgramExist(folder, title):
        return future.getJsonTicket(future.add(_jsonRequest, _jsonExecuteProgramAction), job)
    else:
        return "404 Not Found", "{} Cause: No such program.".format(job), {}


def _jsonExecuteProgramAction() -> tuple:
    path = _jsonRequest.get("path")
    folder, title = path.array[1:3]
    action = path.args[1]

    job = "Request: Executing action '{}' of program '{}' ({}).".format(action, title, folder)

    result = turtle.doProgramAction(folder, title, action)

    if result[0]:
        return "200 OK", job, {
            "name": "Executed action '{}' of program '{}' ({}).".format(action, title, folder),
            "type": "program action",
            "href": "http://{}/program/{}".format(config.get("ap", "ip"), "/".join((folder, title, action))),
            "raw":  "",
            "parent": {},
            "children": [],
            "value": result[1]
        }

    else:
        return "403 Forbidden", "{} Cause: Semantic error in the URL.".format(job), {}


def _jsonGetCommandExecutionStarting() -> tuple:
    return future.getJsonTicket(future.add(_jsonRequest, _jsonExecuteCommand),
                                "Request: Starting command list ({}) execution.".format(
                                    len(_jsonRequest.get("path").args[1:])))


def _jsonExecuteCommand() -> tuple:
    commands = tuple(command.upper() for command in _jsonRequest.get("path").args[1:])
    count = len(commands)
    job = "Request: Executing command list ({}).".format(count)

    if executeCommandList(commands):
        return "200 OK", job, {
            "name": "{} executed commands at {}.".format(count, config.datetime()),
            "type": "command list",
            "href": "http://{}/command/{}".format(config.get("ap", "ip"), "/".join(commands)),
            "raw":  "",
            "parent": {},
            "children": [],
            "value": {
                "commands": commands
            }
        }

    return "403 Forbidden", "{} Cause: Semantic error in the URL.".format(job), {}


_actionFunctions = {
    "command" : _jsonGetCommandExecutionStarting,
    "program" : _jsonGetProgramActionStarting,
    "raw"     : _jsonGetFileByJsonLink
}



def _executeJsonPost() -> tuple:                                                            ########## JSON POST HANDLER
    pathSize = _jsonRequest.get("path").size

    if 0 < pathSize < 4:
        _parseJsonRequestBody()
        category = _jsonRequest.get("path").array[0]

        if category == "program":
            return _jsonPostProgram()
        elif pathSize == 3:
            return _jsonPostFile()
        elif pathSize == 1:
            if category in _jsonPostFunctions.keys():
                return _jsonPostFunctions.get(category)()

    return "403 Forbidden", "Request: REST POST. Cause: The format of the URL is invalid.", {}


def _jsonPostProgram() -> tuple:
    path = _jsonRequest.get("path")

    job = "Request: Save the {}.".format(path.description)

    if path.size < 3:
        _jsonWriteProgram("", "", job)
    else:
        folder, title = path.array[1:3]

        if not turtle.doesProgramExist(folder, title):
            return _jsonWriteProgram(folder, title, job)
        else:
            return "403 Forbidden", "{} Cause: The program already exists.".format(job), {}


def _jsonWriteProgram(folder, title, job) -> tuple:
    body = _jsonRequest.get("body")
    if body == "":
        path = turtle.saveLoadedProgram(folder, title)
    else:
        result = _jsonBodyValidator(job)
        if result[0] != "200 OK":
            return result

        path = turtle.saveProgram(folder, title, body.get("value"))
    return _jsonReplyWithFileInstance(path, job)


def _jsonPostFile() -> tuple:
    path = _jsonRequest.get("path")
    job = "Request: Save the {}.".format(path.description)

    if not path.isExist:
        if data.canCreate(path):
            return _jsonWriteFile(path, job)
        else:
            return "403 Forbidden", "{} Cause: Missing write permission.".format(job), {}
    else:
        return "403 Forbidden", "{} Cause: The file already exists.".format(job), {}


def _jsonWriteFile(path: data.Path, job: str, isJson: bool = None) -> tuple:
    result = _jsonBodyValidator(job)
    if result[0] != "200 OK":
        return result

    body   = _jsonRequest.get("body")
    isJson = isJson is True or body.get("isJson") is True

    file = ujson.dumps(body.get("value")) if isJson else body.get("value")
    data.saveFile(path, file)

    return _jsonReplyWithFileInstance(path, job)


def _jsonPostCommand() -> tuple:
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


def _jsonPostLog() -> tuple:
    job = "Request: Send log for processing."

    if config.get("logger", "active"):
        result = _jsonBodyValidator(job)
        if result[0] != "200 OK":
            return result

        log = _jsonRequest.get("body").get("value")

        logFile = "event" if isinstance(log, str) else "object"
        if logFile in config.get("logger", "active_logs"):
            logger.append(log)
            status, message, json = data.createRestReplyOf("log", logFile, str(powerOns))

            if status == "200 OK":
                return "200 OK", job, json
            else:
                return "500 Internal Server Error", "{} Cause: The file system is not available.".format(job), {}
        else:
            return "403 Forbidden", "{} Cause: The log '{}' is inactive.".format(job, logFile), {}
    else:
        return "403 Forbidden", "{} Cause: The logger module is inactive.".format(job), {}


def _jsonPostRoot() -> tuple:
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


def _executeJsonPut() -> tuple:                                                              ########## JSON PUT HANDLER
    if _jsonRequest.get("path").size == 3:
        _parseJsonRequestBody()
        return _jsonPutFile()

    return "403 Forbidden", "Request: REST PUT. Cause: The format of the URL is invalid.", {}


def _jsonPutFile() -> tuple:
    path = _jsonRequest.get("path")

    job = "Request: Modify the {}.".format(path.description)

    if path.isExist:
        if data.canWrite(path) or data.canModify(path):
            return _jsonWriteFile(path, job)
        else:
            return "403 Forbidden", "{} Cause: Missing write / modify permission.".format(job), {}
    else:
        return "403 Forbidden", "{} Cause: The file doesn't exist.".format(job), {}



def _executeJsonDelete() -> tuple:                                                        ########## JSON DELETE HANDLER
    if 1 < _jsonRequest.get("path").size < 4:
        return _jsonDeleteEntity()

    return "403 Forbidden", "Request: REST DELETE. Cause: The format of the URL is invalid.", {}


def _jsonDeleteEntity() -> tuple:
    path = _jsonRequest.get("path")
    job  = "Request: Delete the {}".format(path.description)

    if path.isExist:
        if data.canDelete(path):
            if data.delete(path):
                return "200 OK", job, {}
            else:
                return "500 Internal Server Error", "{} Cause: The file system is not available.".format(job), {}
        else:
            if path.isFolder and 0 < data.getEntityCountOfFolder(path):
                return "403 Forbidden", "{} Cause: The folder '{}' is not empty.".format(job, path), {}
            else:
                return "403 Forbidden", "{} Cause: Missing delete permission.".format(job), {}
    else:
        return "403 Forbidden", "{} Cause: The {} doesn't exist.".format(job, path.description), {}



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
    mot.config(
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
    mot.setBreath(config.get("turtle", "breath_length"))

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
            webserver.setJsonCallback("PUT", _executeJsonPut)
            webserver.setJsonCallback("DELETE", _executeJsonDelete)
            future.setJsonSender(_updateJsonRequest)
        webserver.start()
    except Exception as e:
        logger.append(e)

buzzer.keyBeep("ready")

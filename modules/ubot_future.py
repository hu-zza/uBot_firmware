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

import ujson, uos

from machine import Timer

import ubot_config    as config
import ubot_logger    as logger
import ubot_data      as data
import ubot_webserver as server
import ubot_motor     as motor

_timer  = Timer(-1)
_period = config.get("future", "period")
_processing = False

_powerOns = config.get("system", "power_ons")
_writeFolder = "/future/{:010d}/".format(_powerOns)

uos.mkdir(_writeFolder[:-1])
_ticketNr = 0
_jobs = []

_hostLink = "http://{}".format(config.get("ap", "ip"))
_rawLink  = "{}/raw{}".format(_hostLink, _writeFolder)
_hostLink = "{}{}".format(_hostLink, _writeFolder)


def _unavailableJsonSender(*args):
    raise Exception("ubot_future#_unavailableJsonSender\r\nThe '_jsonSender' is unavailable, processing had stopped.")

_jsonSender = _unavailableJsonSender

def setJsonSender(method):
    global _jsonSender
    _jsonSender = method


def isProcessing() -> bool:
    return _processing


def add(request: dict, function) -> int:
    global _ticketNr
    try:
        _ticketNr += 1
        _jobs.append((_ticketNr, request, function))
        return _ticketNr
    except Exception as e:
        logger.append(e)
        return -1


def getJsonTicket(ticketNr: int, job: str = "") -> tuple:
    if 0 < ticketNr:
        name = normalizeFutureTitle(ticketNr)

        return "202 Accepted", job, {
            "name": name,
            "type": "future",
            "href": "{}{}".format(_hostLink, name[:name.rindex(".")]),
            "raw":  "{}{}".format(_rawLink,  name),
            "parent": {},
            "children": [],
            "value": {}}
    else:
        return "406 Not Acceptable", job, {}


def normalizeFutureTitle(title) -> str:
    return "{:010d}.txt".format(data.extractIntTupleFromString(title, 1)[0])


def getFutureFolders():
    return data.getFoldersOf(data.FUTURE)


def getFutureTicketsOf(folder: str) -> tuple:
    return data.getFileNameListOf("future", folder, "txt")


def _work(timer) -> None:
    global _processing

    try:
        if _jobs:
            if _canWork():
                _processing = True
                if _canWork():
                    _pollJob()
                else:
                    _processing = False
    except Exception as e:
        logger.append(e)
    finally:
        _processing = False

_timer.init(period = _period, mode = Timer.PERIODIC, callback = _work)


def _canWork() -> bool:
    return not server.isProcessing() and \
           not motor.isProcessing()


def _pollJob() -> None:
    ticketNr, request, function = _jobs.pop(0)

    _jsonSender(request.get("path"), request.get("body"), request.get("parsed"))
    status, message, result = function()

    try:
        with open("{}{}".format(_writeFolder, normalizeFutureTitle(ticketNr)), "w") as file:
            file.write("{}\r\n".format(status))
            file.write("{}\r\n".format(message))
            file.write("{}\r\n".format(ujson.dumps(result)))
    except Exception as e:
        logger.append(e)
        logger.append(result)

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
_processing = False

_powerOns = config.get("system", "power_ons")
_writeFolder = "/future/{:010d}/".format(_powerOns)
_tickets = config.get("future", "tickets")

uos.mkdir(_writeFolder[:-1])
_ticketNr = 0
_jobs = []

_hostLink = "http://{}".format(config.get("ap", "ip"))
_rawLink  = "{}/raw".format(_hostLink)
_futureLink = "{}/future".format(_hostLink)
_futureRawLink = "{}/future".format(_rawLink)


def _unavailableJsonSender(*args) -> None:
    raise Exception("ubot_future#_unavailableJsonSender\r\nThe '_jsonSender' is unavailable, processing had stopped.")

_jsonSender = _unavailableJsonSender

def setJsonSender(method) -> None:
    global _jsonSender
    _jsonSender = method


def isProcessing() -> bool:
    return _processing


def add(request: dict, function) -> int:
    global _ticketNr
    try:
        if _tickets:
            _ticketNr += 1
            _jobs.append((_ticketNr, request.copy(), function))
            return _ticketNr
        else:
            _jobs.append((0, request.copy(), function))
            return 0

    except Exception as e:
        logger.append(e)
        return -1


def createJsonTicket(folder: int, ticketNr: int, job: str = "") -> tuple:
    if 0 <= ticketNr:

        return "202 Accepted", job, {
            "name": "Ticket [{}]".format(ticketNr),
            "type": "future single ticket",
            "href": "{}/ticket/{:010d}/{:05d}".format(_hostLink, folder, ticketNr),
            "raw":  "",
            "parent": {},
            "children": [],
            "value": _createResultDictionary(folder, (ticketNr,)) if ticketNr != 0 else {}
            }
    else:
        return "406 Not Acceptable", job, {}


def createJsonBlockTicket(folder: int, fromNr: int, toNr: int, job: str = "") -> tuple:
    if 0 <= toNr and fromNr <= toNr:
        return createJsonBlockTicketFromTuple(folder, tuple(i + fromNr for i in range(toNr - fromNr + 1)), job)
    else:
        return "406 Not Acceptable", job, {}


def createJsonBlockTicketFromTuple(folder: int, ticketNrs: tuple, job: str = "") -> tuple:
    minNr, maxNr = min(ticketNrs), max(ticketNrs)
    if 0 <= maxNr and minNr <= maxNr:
        return "202 Accepted", job, {
            "name": "Block ticket [{} - {}]".format(minNr, maxNr),
            "type": "future block ticket",
            "href": "{}/ticket/{:010d}/{:05d}/{:05d}".format(_hostLink, folder, minNr, maxNr),
            "raw":  "",
            "parent": {},
            "children": [],
            "value": _createResultDictionary(folder, ticketNrs)}
    else:
        return "406 Not Acceptable", job, {}


def _createResultDictionary(folder: int, ticketNrs: tuple) -> dict:

    files = [(ticketNr, "/{:010d}/{:05d}".format(folder, ticketNr)) for ticketNr in ticketNrs]

    return {str(file[0]): {"name": file[1][file[1].rindex("/") + 1:],
                           "type": "file",
                           "href": "{}{}".format(_futureLink, file[1]),
                           "raw":  "{}{}.txt".format(_futureRawLink, file[1]),
                           "ready": doesFutureContentExist(folder, file[0]),
                           "size": getFutureContentSizeInBytes(folder, file[0])} for file in files}


def doesFutureContentExist(folder: int, ticketNr: int) -> bool:
    return data.doesExist("/future/{:010d}/{}".format(folder, normalizeFutureTitle(ticketNr)))


def getFutureContentSizeInBytes(folder: int, ticketNr: int) -> int:
    try:
        return uos.stat("/future/{:010d}/{}".format(folder, normalizeFutureTitle(ticketNr)))[6]
    except Exception:
        return 0


def normalizeFutureTitle(title: object) -> str:
    if isinstance(title, int):
        if title < 0:
            return ""

    ticketTuple = data.extractIntTuple(title, 1)
    if ticketTuple != ():
        return "{:05d}.txt".format(ticketTuple[0])
    else:
        return ""


def getFutureFolders() -> tuple:
    return data.getFoldersOf(data.FUTURE)


def getFutureTicketsOf(folder: str) -> tuple:
    return data.getFileNameListOf("future", folder, "txt")


def urge() -> None:
    _work()


def _work(timer: Timer = None) -> None:
    global _processing

    try:
        if _jobs:
            if _canWork():
                _processing = True
                if _canWork():
                    while _jobs and _canWork():
                        _pollJob()
                else:
                    _processing = False
    except Exception as e:
        logger.append(e)
    finally:
        _processing = False

_timer.init(period = config.get("future", "period"), mode = Timer.PERIODIC, callback = _work)


def _canWork() -> bool:
    return not server.isProcessing() and \
           not motor.isProcessing()


def _pollJob() -> None:
    ticketNr, request, function = _jobs.pop(0)

    _jsonSender(request.get("path"), request.get("body"), request.get("parsed"))

    if 0 == ticketNr:
        function()
    else:
        status, message, result = function()

        try:
            if not data.doesExist(_writeFolder):
                uos.mkdir(_writeFolder[:-1])

            with open("{}{}".format(_writeFolder, normalizeFutureTitle(ticketNr)), "w") as file:
                file.write("{}\r\n".format(status))
                file.write("{}\r\n".format(message))
                file.write("{}\r\n".format(ujson.dumps(result)))
        except Exception as e:
            logger.append(e)
            logger.append(result)

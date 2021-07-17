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

import usys

import ubot_config as config

_enabled  = config.get("logger", "active")

        # Name        | List  | Path  | Enabled
_logs = (
        ["Exception",   [],     "",     "exception" in config.get("logger", "active_logs")],
        ["Event",       [],     "",     "event" in config.get("logger", "active_logs")],
        ["Object",      [],     "",     "object" in config.get("logger", "active_logs")],
        ["Run",         [],     "",     "run" in config.get("logger", "active_logs")])


################################
## PUBLIC METHODS

def append(item, logIndex = None):
    if _enabled:
        try:
            logIndex = _defineIndex(item) if logIndex is None else logIndex
            if 0 <= logIndex:
                with open(_logs[logIndex][2], "a") as file:
                    _writeOutItem(config.datetime(), file, item)
        except Exception as e:
            _appendToList(e)
            _appendToList(item)


def logCommandsAndProgram():
    if _logs[3][3]:
        append((turtle.getCommandArray(), turtle.getProgramArray()), 3)


def getLogCategories():
    return data.getFoldersOf(data.LOG)


def getCategoryLogs(category):
    return data.getFileListOf("log", category, "txt")


def getLog(category: str, title) -> tuple:
    return data.getFile(getPathOf(category, title), False)


def printLog(category: str, title) -> None:
    data.printFile(getPathOf(category, title), False)


def doesLogExist(category, title):
    return normalizeLogTitle(title) in getCategoryLogs(category)


def getPathOf(category: str, title = "") -> data.Path:
    return data.createPathOf("log", category, normalizeLogTitle(title))


def normalizeLogTitle(title) -> str:
    return "{:010d}.txt".format(data.extractIntTupleFromString(title, 1)[0])


################################
## PRIVATE, HELPER METHODS

def _appendToList(item):
    global _logs

    index = _defineIndex(item)

    if 0 <= index:
        try:
            _logs[index][1].append((config.datetime(), item))

            if 30 < len(_logs[index][1]):
                try:
                    _saveFromList(_logs[index])
                except Exception as e:
                    _logs[index][1] = _logs[index][1][10:]         # Reassign list (Delete the oldest 10 items.)

        except Exception as e:
            usys.print_exception(e)
            if index == 0:
                usys.print_exception(item)


def _saveFromList(logFile, fallback = False):
    if _enabled and logFile[3] and 0 < len(logFile[1]):             # Logger and log is active and log list has item(s).

        filename = "0000000000.txt" if fallback else _filename
        try:
            with open(logFile[2] + filename, "a") as file:
                for item in logFile[1]:
                    _writeOutItem(item[0], file, item[1])
            logFile[1] = []
        except Exception as e:
            usys.print_exception(e)

            if not fallback:
                _saveFromList(logFile, True)


def _writeOutItem(dateTime, logFile, item):
    if isinstance(item, str):
        logFile.write("{}     \t".format(dateTime))
    else:
        logFile.write("{}\r\n".format(dateTime))

    if _defineIndex(item) == 0:
        usys.print_exception(item, logFile)
    else:
        _chooseWriteOutMethod(logFile, item)
    logFile.write("\r\n\r\n")


def _chooseWriteOutMethod(logFile, item, indentation = ""):
    if isinstance(item, dict):
        _writeOutDict(logFile, item, indentation)
    elif isinstance(item, tuple) or isinstance(item, list):
        _writeOutIterable(logFile, item, indentation)
    else:
        if item != "":
            logFile.write("{}{}\r\n".format(indentation, item))
        else:
            logFile.write("{}[empty string]\r\n".format(indentation))


def _writeOutIterable(logFile, iterable, indentation = ""):
    if 0 < len(iterable):
        for item in iterable:
            _chooseWriteOutMethod(logFile, item, indentation)
    else:
        logFile.write("{}[empty iterable]\r\n".format(indentation))


def _writeOutDict(logFile, dictionary, indentation = ""):
    if 0 < len(dictionary):
        for key in dictionary.keys():
            logFile.write("{}{}:\r\n".format(indentation, key))
            _chooseWriteOutMethod(logFile, dictionary.get(key), indentation + "\t")
    else:
        logFile.write("{}[empty map]\r\n".format(indentation))


def _defineIndex(item):
    if not _enabled:
        return -1
    elif isinstance(item, Exception):
        return 0 if _logs[0][3] else -1
    elif isinstance(item, str):
        return 1 if _logs[1][3] else -1
    else:
        return 2 if _logs[2][3] else -1



################################
## INITIALISATION

_filename = "{:010d}.txt".format(config.get("system", "power_ons"))

try:
    with open("/log/datetime.txt", "a") as file:
        file.write("{}\r\n{}\r\n\r\n".format(config.datetime(), _filename))
except Exception as e:
    _appendToList(e)

for _logFile in _logs:
    _logFile[2] = "/log/{}/{}".format(_logFile[0].lower(), _filename)
    try:
        with open(_logFile[2], "w") as file:
            file.write("{}     \t{} log initialised successfully.\r\n\r\n\r\n".format(config.datetime(), _logFile[0]))
            _saveFromList(_logFile)
    except Exception as e:
        _appendToList(e)


# Preventing circular dependency

import ubot_data   as data
import ubot_turtle as turtle


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

import ujson, usys

import ubot_config as config
import ubot_turtle as turtle
import ubot_data   as data

_fileName = 0
_enabled = config.get("logger", "active")

                # Name        | List  | Path  | Enabled
_logFiles = (
                ["Exception",   [],     "",     "Exception" in config.get("logger", "active_logs")],
                ["Event",       [],     "",     "Event" in config.get("logger", "active_logs")],
                ["Object",      [],     "",     "Object" in config.get("logger", "active_logs")],
                ["Run",         [],     "",     "Run" in config.get("logger", "active_logs")])


################################
## PUBLIC METHODS

def append(item, logIndex = None):
    if _enabled:
        if _fileName != 0:
            try:
                logIndex = _defineIndex(item) if logIndex is None else logIndex
                if 0 <= logIndex:
                    with open(_logFiles[logIndex][2], "a") as file:
                        _writeOutItem(config.datetime(), file, item)
            except Exception as e:
                _appendToList(e)
                _appendToList(item)
        else:
            _appendToList(item)


def logCommandsAndProgram():
    if _logFiles[3][3]:
        append((turtle.getCommandArray(), turtle.getProgramArray()), 3)


def getLogCategories():
    return data.getFoldersOf("log")


def getCategoryLogs(category):
    return data.getFilenamesOf("log", category)


def getLog(category, title):
    return data.getFile(data.getNormalizedPathOf(("log", category), title))


def doesLogExist(category, title):
    return title in getCategoryLogs(category)


################################
## PRIVATE, HELPER METHODS

def _appendToList(item):
    global _logFiles

    index = _defineIndex(item)

    if 0 <= index:
        try:
            _logFiles[index][1].append((config.datetime(), item))

            if 30 < len(_logFiles[index][1]):
                try:
                    _saveFromList(_logFiles[index])
                except Exception as e:
                    _logFiles[index][1] = _logFiles[index][1][10:]         # Reassign list (Delete the oldest 10 items.)

        except Exception as e:
            usys.print_exception(e)
            if index == 0:
                usys.print_exception(item)


def _saveFromList(logFile, fallback = False):
    if _enabled and logFile[3] and 0 < len(logFile[1]):             # Logger and log is active and log list has item(s).

        if _fileName == 0:                                          # If filename is undefined.
            fallback = True

        fileName = "0000000000.txt" if fallback else _fileName
        try:
            with open(logFile[2] + fileName, "a") as file:
                for item in logFile[1]:
                    _writeOutItem(item[0], file, item[1])
            logFile[1] = []
        except Exception as e:
            usys.print_exception(e)

            if not fallback:
                _saveFromList(logFile, True)


def _writeOutItem(dateTime, logFile, item):
    logFile.write("{}\n".format(dateTime))

    if _defineIndex(item) == 0:
        usys.print_exception(item, logFile)
    else:
        if isinstance(item, tuple) or isinstance(item, list):
            for i in item:
                logFile.write("{}\n".format(i))
        else:
            logFile.write("{}\n".format(item))

    logFile.write("\n")


def _defineIndex(item):
    if not _enabled:
        return -1
    elif isinstance(item, Exception):
        return 0 if _logFiles[0][3] else -1
    elif isinstance(item, str):
        return 1 if _logFiles[1][3] else -1
    else:
        return 2 if _logFiles[2][3] else -1



################################
## INITIALISATION

_fileName = "{:010d}.txt".format(int(config.get("system", "power_ons")))

try:
    with open("/log/datetime.txt", "a") as file:
        file.write("{}\n{}\n\n".format(config.datetime(), _fileName))
except Exception as e:
    _appendToList(e)

for _logFile in _logFiles:
    _logFile[2] = "/log/{}/{}".format(_logFile[0].lower(), _fileName)
    try:
        with open(_logFile[2], "w") as file:
            file.write("{}\n{} log initialised successfully.\n\n".format(config.datetime(), _logFile[0]))
            _saveFromList(_logFile)
    except Exception as e:
        _appendToList(e)

import uos, sys

from machine import RTC

import ubot_config as config


_fileName = 0
                #    Name   | List |   Directory
_logFiles = (
                ["Exception", [], "log/exception/"],
                ["Event",     [], "log/event/"],
                ["Object",    [], "log/object/"]
            )



################################
## PUBLIC METHODS

def append(item):
    if _fileName != 0:
        try:
            with open(_logFiles[_defineIndex(item)][2] + _fileName, "a") as file:
                _writeOutItem(config.datetime(), file, item)
        except Exception as e:
            _appendToList(e)
            _appendToList(item)
    else:
        _appendToList(item)



################################
## PRIVATE, HELPER METHODS

def _appendToList(item):
    global _logFiles

    index = _defineIndex(item)

    try:
        _logFiles[index][1].append((config.datetime(), item))

        if 30 < len(_logFiles[index][1]):
            try:
                _saveFromList(_logFiles[index])
            except Exception as e:
                _logFiles[index][1] = _logFiles[index][1][10:]              # Reassign list (Delete the oldest 10 items.)

    except Exception as e:
        sys.print_exception(e)
        if index == 0:
            sys.print_exception(item)


def _saveFromList(logFile, fallback = False):
    if logFile[1] != []:                                            # If this list contains item(s).

        if _fileName == 0:                                          # If filename is undefined.
            fallback = True

        fileName = "0000000000.txt" if fallback else _fileName
        try:
            with open(logFile[2] + fileName, "a") as file:
                for item in logFile[1]:
                    _writeOutItem(item[0], file, item[1])
            logFile[1] = []
        except Exception as e:
            sys.print_exception(e)

            if not fallback:
                _saveFromList(logFile, True)


def _writeOutItem(dateTime, file, item):
    file.write("{}\n".format(dateTime))

    if _defineIndex(item) == 0:
        sys.print_exception(item, file)
    else:
        if isinstance(item, list):
            for i in item:
                file.write("{}\n".format(i))
        else:
            file.write("{}\n".format(item))

    file.write("\n")


def _defineIndex(item):
    if isinstance(item, Exception):
        return 0
    elif isinstance(item, dict):
        return 2
    else:
        return 1



################################
## INITIALISATION

_fileName = "{:010d}.txt".format(int(config.get("system", "powerOnCount")))

try:
    with open("log/datetime.txt", "a") as file:
        file.write("{}\n{}\n\n".format(config.datetime(), _fileName))
except Exception as e:
    _appendToList(e)

for logFile in _logFiles:
    try:
        with open(logFile[2] + _fileName, "w") as file:
            file.write("{}\n{} log initialised successfully.\n\n".format(config.datetime(), logFile[0]))
            _saveFromList(logFile)
    except Exception as e:
        _appendToList(e)

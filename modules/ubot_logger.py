import uos, sys

from machine import RTC


_dateTime = 0
_fileName = 0
                #    Name   | List |   Directory
_logFiles = [
                ["Exception", [], "log/exception/"],
                ["Event",     [], "log/event/"]
            ]



################################
## CONFIG

def config(dateTime, powerOnCount):
    global _dateTime
    global _fileName
    global _logFiles

    _dateTime = dateTime
    _fileName = "{:010d}.txt".format(int(powerOnCount))

    try:
        with open("log/datetime.txt", "a") as file:
            file.write("{}\n{}\n\n".format(_dateTime.datetime(), _fileName))
    except Exception as e:
        _appendToList(e)

    for logFile in _logFiles:
        try:
            with open(logFile[2] + _fileName, "w") as file:
                file.write("{}\n{} log initialised successfully.\n\n".format(_dateTime.datetime(), logFile[0]))
                _saveFromList(logFile)
        except Exception as e:
            _appendToList(e)



################################
## PUBLIC METHODS

def getDateTime():
    return _dateTime.datetime()


def append(item):
    global _logFiles

    if _fileName != 0:
        try:
            with open(_logFiles[_defineIndex(item)][2] + _fileName, "a") as file:
                _writeOutItem(_dateTime.datetime(), file, item)
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
        _logFiles[index][1].append((() if _dateTime == 0 else _dateTime.datetime(), item))

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
        dateTime = () if _dateTime == 0 else _dateTime.datetime()
        try:
            with open(logFile[2] + fileName, "a") as file:
                for item in logFile[1]:
                    if item[0] != ():                               # The first tuple of the list item should contain datetime.
                        _writeOutItem(item[0], file, item[1])
                    else:                                           # If the first tuple is empty, save it with the current datetime, or ().
                        _writeOutItem(dateTime, file, item[1])
            logFile[1] = []                                         # Clear the list.
        except Exception as e:
            sys.print_exception(e)

            if fallback:
                raise
            else:
                _saveFromList(logFile, True)


def _writeOutItem(dateTime, file, item):
    file.write("{}\n".format(dateTime))

    if _defineIndex(item) == 0:
        sys.print_exception(item, file)
    else:
        file.write("{}\n".format(item))

    file.write("\n")


def _defineIndex(item):
    if isinstance(item, Exception):
        return 0
    else:
        return 1

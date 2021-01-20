import uos, sys

from machine import RTC


_exceptions = []
_dateTime   = 0
_fileName   = 0



################################
## CONFIG

def config(dateTime, powerOnCount):
    global _exceptions
    global _dateTime
    global _fileName

    _dateTime = dateTime
    _fileName = "log/exception/{:010d}.txt".format(powerOnCount)

    try:
        with open(_fileName, "w") as f:
            f.write("{}\nException log initialised successfully.\n\n".format(_dateTime.datetime()))
    except Exception as e:
        _appendToList(e)

    if _exceptions != []:                                       # Use case: append() can be used before config()
        try:                                                    #           So save the possible exceptions from list.
            with open(_fileName, "a") as f:
                for exception in _exceptions:
                    f.write("{}\n".format(_dateTime.datetime()))# Exceptions appended before config() hasn't got datetime.
                    sys.print_exception(exception[1], f)
                    f.write("\n")
            _exceptions = []                                    # Clear the list. Maybe it will be used later.
        except Exception as e:
            _appendToList(e)



################################
## PUBLIC METHODS

def append(exception):
    global _fileName

    if _fileName != 0:
        try:
            with open(_fileName, "a") as f:
                f.write("{}\n".format(_dateTime.datetime()))
                sys.print_exception(exception, f)
                f.write("\n")
        except Exception as e:
            _appendToList(e)
            _appendToList(exception)
    else:
        _appendToList(exception)


def getExceptions():
    return ""



################################
## PRIVATE, HELPER METHODS

def _appendToList(exception):
    global _exceptions

    try:
        _exceptions.append((() if _dateTime == 0 else _dateTime.datetime(), exception))
        if 30 < len(_exceptions):
            _exceptions = _exceptions[10:]
    except Exception as e:
        sys.print_exception(e)
        sys.print_exception(exception)


"""
TODO....

def listExceptions():
    for i in range(len(exception)):
        print("{}t{}t{}".format(i, exception[i][0], exception[i][1]))


def printException(nr):
    if 0 <= nr and nr < len(exception):
        print(exception[nr][0])
        sys.print_exception(exception[nr][1])
    else:
        print("List index ({}) is out of range ({}).".format(nr, len(exception)))
"""

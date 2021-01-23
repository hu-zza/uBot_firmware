import uos, sys

from machine import RTC


_dateTime       = 0
_events         = []
_exceptions     = []
_eventsFile     = 0
_exceptionsFile = 0



################################
## CONFIG

def config(dateTime, powerOnCount):
    global _exceptions
    global _dateTime
    global _exceptionsFile

    _dateTime       = dateTime
    _eventsFile     = "log/event/{:010d}.txt".format(powerOnCount)
    _exceptionsFile = "log/exception/{:010d}.txt".format(powerOnCount)

    files = (("Exception", _exceptions, _exceptionsFile), ("Event", _events, _eventsFile))

    for attr in files:
        try:
            with open(attr[2], "w") as file:
                file.write("{}\n{} log initialised successfully.\n\n".format(_dateTime.datetime(), attr[0]))
        except Exception as e:
            _appendToList(e)

        if attr[1] != []:                                               # Use case: append() can be used before config(),
            try:                                                        #         so save the possible items from lists.
                with open(attr[2], "a") as file:
                    for item in attr[1]:
                        file.write("{}\n".format(_dateTime.datetime())) # Exceptions appended before config() hasn't got datetime.

                        if isinstance(item, Exception):
                            sys.print_exception(item, file)
                        else:
                            file.write("{}\n".format(item))

                        file.write("\n")
                attr[1] = []                                            # Clear the list. Maybe it will be used later.
            except Exception as e:
                _appendToList(e)



################################
## PUBLIC METHODS


def getDateTime():
    return _dateTime.datetime()


def append(item):
    global _eventsFile
    global _exceptionsFile

    if isinstance(item, Exception):
        fileName = _exceptionsFile
    else:
        fileName = _eventsFile

    if fileName != 0:
        try:
            with open(fileName, "a") as file:
                file.write("{}\n".format(_dateTime.datetime()))

                if isinstance(item, Exception):
                    sys.print_exception(item, file)
                else:
                    file.write("{}\n".format(item))

                file.write("\n")
        except Exception as e:
            _appendToList(e)
            _appendToList(item)
    else:
        _appendToList(item)



################################
## PRIVATE, HELPER METHODS

def _appendToList(item):
    global _events
    global _exceptions

    if isinstance(item, Exception):
        list = _exceptions
    else:
        list = _events

    try:
        list.append((() if _dateTime == 0 else _dateTime.datetime(), item))
        if 30 < len(list):
            list = list[10:]
    except Exception as e:
        sys.print_exception(e)
        sys.print_exception(exception)

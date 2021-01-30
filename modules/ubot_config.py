import ujson, uos

from machine import RTC



################################
## PUBLIC METHODS

def get(module, attribute):
    """ Returns the value of the attribute, or None. Firstly reads it from file, then deserializes it. """
    return _manageAttribute(module, attribute, "r")


def set(module, attribute, value):
    """ Sets the value of the attribute. Firstly serializes it and then writes it out. """
    return _manageAttribute(module, attribute, "w", value)


def datetime(newDateTime = None):
    if newDateTime != None:
        dateTime.datetime(newDateTime)
        saveDateTime()

    return dateTime.datetime()


def saveDateTime():
    try:
        with open("etc/datetime.py", "w") as file:
            file.write("DT = {}".format(dateTime.datetime()))
    except Exception as e:
        logger.append(e)



################################
## PRIVATE, HELPER METHODS

def _manageAttribute(dir, file, mode, value = None):
    try:
        with open("etc/{}/{}.txt".format(dir, file), mode) as file:
            if mode == "r":
                return ujson.loads(file.readline())
            elif mode == "w":
                return file.write("{}\n".format(ujson.dumps(value)))
    except Exception as e:
        logger.append(e)


def _readOrThrow(dir, file):
    with open("etc/{}/{}.txt".format(dir, file), "r") as file:
        return ujson.loads(file.readline())



################################
## INITIALISATION

initExceptions = []

dateTime       = RTC()
dateTimeSource = "factory default"

try:
    import etc.datetime
    dateTime.datetime(etc.datetime.DT)
    dateTimeSource = "etc.datetime module"
except Exception as e:
    initExceptions.append(e)

    try:
        initialDateTime = _readOrThrow("system", "initialDateTime")
        dateTime.datetime(initialDateTime)
        dateTimeSource = "firmware default"
    except Exception as e:
        initExceptions.append(e)


powerOnCount       = 0
powerOnCountSource = "firmware default"

try:
    powerOnCount       = _readOrThrow("system", "powerOnCount")
    powerOnCountSource = "configuration file (etc/system)"
except Exception as e:
    initExceptions.append(e)

    powerOnCount = int(uos.listdir("log/exception")[-1][:-4])   # [last file][cut extension]
    powerOnCountSource = "guessing based on filenames"

powerOnCount += 1                                               # Increment the counter
_manageAttribute("system", "powerOnCount", "w", powerOnCount)   # and save it


import ubot_logger as logger

for exception in initExceptions:
    logger.append(exception)

logger.append("System RTC has been set. Source: {}".format(dateTimeSource))
logger.append("'Power on count' has been set. Source: {}".format(powerOnCountSource))

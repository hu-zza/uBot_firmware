import ujson, uos

from machine import RTC

import ubot_logger as logger


dateTime = RTC()



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



################################
## INITIALISATION

try:
    import etc.datetime
    dateTime.datetime(etc.datetime.DT)
except Exception as e:
    logger.append(e)

    initialDateTime = get("system", "initialDateTime")
    if initialDateTime != None:
        dateTime.datetime(initialDateTime)


powerOnCount = get("system", "powerOnCount")
if powerOnCount == None:
    powerOnCount = int(uos.listdir("log/exception")[-1][:-4])   # [last file][cut extension]
powerOnCount += 1                                               # Increment the counter
_manageAttribute("system", "powerOnCount", "w", powerOnCount)   # and save it

try:
    logger.config(dateTime, powerOnCount)
except Exception as e:
    logger.append(e)



"""
TODO:

defaultsLoaded = True

try:
    import etc.defaults as defaults
except Exception as e:
    defaultsLoaded = False
    logger.append(e)
"""

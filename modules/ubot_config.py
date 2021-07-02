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

from machine import RTC



################################
## PUBLIC METHODS

def getModules():
    """ Returns a tuple consists all available modules, or an empty tuple. """
    try:
        moduleFolders = uos.listdir("/etc")
        return tuple([module for module in moduleFolders if uos.stat("/etc/{}".format(module))[0] == 0x04000])    # only dirs
    except Exception as e:
        logger.append(e)
        return ()


def getModuleAttributes(module):
    """ Returns a tuple consists all available attributes, or an empty tuple. """
    try:
        moduleFiles = uos.listdir("/etc/{}".format(module.lower()))
        return tuple([fileName[:-4] for fileName in moduleFiles if fileName[-4:] == ".txt"])
    except Exception as e:
        logger.append(e)
        return ()


def get(module, attribute):
    """ Returns the value of the attribute, or None. Firstly reads it from file, then deserializes it. """
    return _manageAttribute(module, attribute, "r")


def getDefault(module, attribute):
    """ Returns the default value of the attribute, or None. Firstly reads it from file, then deserializes it. """
    return _manageAttribute(module, attribute, "r", None, "def")


def restore(module, attribute):
    try:
        value = _manageAttribute(module, attribute, "r", None, "def")   # Read the default config value if it exists
        _manageAttribute(module, attribute, "w", value)                 # Replace the config file
        logger.append(
            ("Configuration: /etc/{dir}/{file}.txt could not be read. "
             "It has been replaced with /etc/{dir}/{file}.def").format(dir = module, file = attribute)
        )
        return value
    except Exception as e:
        logger.append(e)


def set(module, attribute, value):
    """ Sets the value of the attribute. Firstly serializes it and then writes it out. """
    _manageRelated(module, attribute, value)    # Can not be at _manageAttribute's mode == "w" branch: too deep.
    return _manageAttribute(module, attribute, "w", value)


def datetime(newDateTime = None):
    if newDateTime is not None:
        dateTime.datetime(newDateTime)
        saveDateTime()

    return dateTime.datetime()


def saveDateTime():
    try:
        with open("/etc/datetime.py", "w") as file:
            file.write("DT = {}".format(dateTime.datetime()))
    except Exception as e:
        logger.append(e)



################################
## PRIVATE, HELPER METHODS

def _manageAttribute(dir, name, mode, value = None, extension = "txt"):
    try:
        with open("/etc/{}/{}.{}".format(dir, name, extension), mode) as file:
            if mode == "r":
                return ujson.loads(file.readline())
            elif mode == "w":
                return file.write("{}\n".format(ujson.dumps(value)))
    except Exception as e:
        logger.append(e)


def _manageRelated(module, attribute, value):
    try:
        if module == "webRepl" and attribute == "active":
                if value and ".webrepl_cfg.py" in uos.listdir("/"):
                    uos.rename("/.webrepl_cfg.py", "/webrepl_cfg.py")
                elif not value and "webrepl_cfg.py" in uos.listdir("/"):
                    uos.rename("/webrepl_cfg.py", "/.webrepl_cfg.py")
    except Exception as e:
        logger.append(e)


def _readOrThrow(dir, file):
    with open("/etc/{}/{}.txt".format(dir, file), "r") as file:
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
        initDateTime = _readOrThrow("system", "initDateTime")
        dateTime.datetime(initDateTime)
        dateTimeSource = "firmware default"
    except Exception as e:
        initExceptions.append(e)



powerOnCount       = 0
powerOnCountSource = "firmware default"

try:
    powerOnCount       = _readOrThrow("system", "powerOnCount")
    powerOnCountSource = "configuration file (/etc/system)"
except Exception as e:
    initExceptions.append(e)

    powerOnCount = int(uos.listdir("/log/exception")[-1][:-4])   # [last file][cut extension]
    powerOnCountSource = "guessing based on filenames"

powerOnCount += 1                                               # Increment the counter
_manageAttribute("system", "powerOnCount", "w", powerOnCount)   # and save it


import ubot_logger as logger

for exception in initExceptions:
    logger.append(exception)

logger.append("System RTC has been set. Source: {}".format(dateTimeSource))
logger.append("'Power on count' has been set. Source: {}".format(powerOnCountSource))

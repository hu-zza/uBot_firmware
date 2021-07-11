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
    return data.getFoldersOf("etc")


def getAttributesOf(module):
    """ Returns a tuple consists all available attributes, or an empty tuple. """
    return data.getFileNamesOf("etc", module)


def get(module, attribute):
    """ Returns the value of the attribute, or None. Firstly reads it from file, then deserializes it. """
    return _manageAttribute(module, attribute, "r")


def getDefault(module, attribute):
    """ Returns the default value of the attribute, or None. Firstly reads it from file, then deserializes it. """
    return _manageAttribute(module, attribute, "r", None, "def")


def doesModuleExist(module):
    return module in getModules()


def doesAttributeExist(module, attribute):
    return attribute in getAttributesOf(module)


def restore(module, attribute):
    try:
        logger.append("Resetting /etc/{}/{} to default.".format(module, attribute))
        value = _manageAttribute(module, attribute, "r", None, "def")                    # Read the default config value
        _manageAttribute(module, attribute, "w", value)                                  # Replace the config file
        logger.append("Success:  /etc/{}/{} is now '{}'.".format(module, attribute, value))
    except Exception as e:
        logger.append(e)


def set(module, attribute, value):
    """ Sets the value of the attribute. Firstly serializes it and then writes it out. """
    _manageWebReplFile(module, attribute, value)        # Can not be at _manageAttribute's mode == "w" branch: too deep.
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

def _manageAttribute(module, attribute, mode, value = None, extension = "txt"):
    try:
        with open("/etc/{}/{}.{}".format(module, attribute, extension), mode) as file:
            if mode == "r":
                return ujson.loads(file.readline())
            elif mode == "w":
                return file.write("{}\r\n".format(ujson.dumps(value)))
    except Exception as e:
        logger.append(e)


def _manageWebReplFile(module, attribute, value):
    if module == "web_repl" and attribute == "active":
        try:
            if value and ".webrepl_cfg.py" in uos.listdir("/"):
                uos.rename("/.webrepl_cfg.py", "/webrepl_cfg.py")
            elif not value and "webrepl_cfg.py" in uos.listdir("/"):
                uos.rename("/webrepl_cfg.py", "/.webrepl_cfg.py")
        except Exception as e:
            logger.append(e)


def _readOrThrow(module, attribute):
    with open("/etc/{}/{}.txt".format(module, attribute), "r") as file:
        return ujson.loads(file.readline())


################################
## INITIALISATION

dateTime       = RTC()
dateTimeSource = "factory default"
_exceptions    = []

try:
    import etc.datetime
    dateTime.datetime(etc.datetime.DT)
    dateTimeSource = "etc.datetime module"
except Exception as e:
    _exceptions.append(e)

    try:
        dateTime.datetime(_readOrThrow("system", "init_datetime"))
        dateTimeSource = "firmware default"
    except Exception as e:
        _exceptions.append(e)


powerOns       = 0
powerOnsSource = "firmware default"

try:
    powerOns       = _readOrThrow("system", "power_ons")
    powerOnsSource = "configuration file (/etc/system)"
except Exception as e:
    _exceptions.append(e)

    powerOns = int(uos.listdir("/log/exception")[-1][:-4])   # [last file][cut extension '.txt']
    powerOnsSource = "guessing based on filenames"

powerOns += 1                                               # Increment the counter
_manageAttribute("system", "power_ons", "w", powerOns)   # and save it


# Preventing circular dependency

import ubot_logger as logger

for exception in _exceptions:
    logger.append(exception)

del _exceptions
logger.append("System RTC has been set. Source: {}".format(dateTimeSource))
logger.append("'Power on count' has been set. Source: {}".format(powerOnsSource))

import ubot_data as data

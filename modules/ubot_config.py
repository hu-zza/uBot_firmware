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

def getModules() -> tuple:
    """ Returns a tuple consists all available modules, or an empty tuple. """
    return data.getFoldersOf(data.ETC)


def getAttributesOf(module: str) -> tuple:
    """ Returns a tuple consists all available attributes, or an empty tuple. """
    return data.getFileNameListOf("etc", module, "txt")


def get(module: str, attribute: str):
    """ Returns the value of the attribute, or None. Firstly reads it from file, then deserializes it. """
    return _manageAttribute(module, attribute, "r")


def getDefault(module: str, attribute: str):
    """ Returns the default value of the attribute, or None. Firstly reads it from file, then deserializes it. """
    return _manageAttribute(module, attribute, "r", None, "def")


def doesModuleExist(module: str) -> bool:
    return module in getModules()


def doesAttributeExist(module: str, attribute: str) -> bool:
    return attribute in getAttributesOf(module)


def restore(module: str, attribute: str) -> bool:
    try:
        logger.append("Resetting /etc/{}/{} to default.".format(module, attribute))
        value = _manageAttribute(module, attribute, "r", None, "def")                    # Read the default config value
        _manageAttribute(module, attribute, "w", value)                                  # Replace the config file
        logger.append("Success:  /etc/{}/{} is now '{}'.".format(module, attribute, value))
        return True
    except Exception as e:
        logger.append(e)
        return False


def set(module: str, attribute: str, value: object) -> int:
    """ Sets the value of the attribute. Firstly serializes it and then writes it out. """
    _manageWebReplFile(module, attribute, value)        # Can not be at _manageAttribute's mode == "w" branch: too deep.
    return _manageAttribute(module, attribute, "w", value)


def datetime(newDateTime: tuple = None) -> tuple:
    if newDateTime is not None:
        logger.append("Set new datetime: {}".format(newDateTime))
        dateTime.datetime(newDateTime)
        saveDateTime()
        logger.append("The new datetime: {}".format(dateTime.datetime()))

    return dateTime.datetime()


def saveDateTime() -> None:
    try:
        with open("/etc/datetime.py", "w") as file:
            file.write("DT = {}".format(dateTime.datetime()))
    except Exception as e:
        logger.append(e)


################################
## PRIVATE, HELPER METHODS

def _manageAttribute(module: str, attribute: str, mode: str, value: object = None, extension: str = "txt"):
    try:
        with open("/etc/{}/{}.{}".format(module, attribute, extension), mode) as file:
            if mode == "r":
                return ujson.loads(file.readline())
            elif mode == "w":
                return file.write("{}\r\n".format(ujson.dumps(value)))
    except Exception as e:
        logger.append(e)


def _manageWebReplFile(module: str, attribute: str, value: object) -> None:
    if module == "web_repl" and attribute == "active":
        try:
            if value and ".webrepl_cfg.py" in uos.listdir("/"):
                uos.rename("/.webrepl_cfg.py", "/webrepl_cfg.py")
            elif not value and "webrepl_cfg.py" in uos.listdir("/"):
                uos.rename("/webrepl_cfg.py", "/.webrepl_cfg.py")
        except Exception as e:
            logger.append(e)


def _readOrThrow(module: str, attribute: str) -> str:
    with open("/etc/{}/{}.txt".format(module, attribute), "r") as file:
        return ujson.loads(file.readline())


################################
## INITIALISATION

dateTime       = RTC()
dateTimeSource = "factory default"
exceptions    = []

try:
    import etc.datetime
    dateTime.datetime(etc.datetime.DT)
    dateTimeSource = "etc.datetime module"
except Exception as e:
    exceptions.append(e)

    try:
        dateTime.datetime(_readOrThrow("system", "init_datetime"))
        dateTimeSource = "firmware default"
    except Exception as e:
        exceptions.append(e)


powerOns       = 0
powerOnsSource = "firmware default"

try:
    powerOns       = _readOrThrow("system", "power_ons")
    powerOnsSource = "configuration file (/etc/system)"
except Exception as e:
    exceptions.append(e)

    powerOns = int(uos.listdir("/log/exception")[-1][:-4])   # [last file][cut extension '.txt']
    powerOnsSource = "guessing based on filenames"

powerOns += 1                                               # Increment the counter
_manageAttribute("system", "power_ons", "w", powerOns)      # and save it


# Preventing circular dependency

import ubot_logger as logger

for exception in exceptions:
    logger.append(exception)

logger.append("System RTC has been set. Source: {}".format(dateTimeSource))
logger.append("'Power on count' has been set. Source: {}".format(powerOnsSource))

import ubot_data as data

del exceptions
del dateTimeSource

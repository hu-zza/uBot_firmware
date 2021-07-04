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

import ubot_config as config
import ubot_logger as logger

_hostLink = "http://{}/".format(config.getAp().ifconfig()[0])
_rawLink  = _hostLink + "raw/"


def isDir(path):
    try:
        return uos.stat(path)[0] == 0x4000
    except Exception as e:
        logger.append(e)
        return False


def isFile(path):
    try:
        return uos.stat(path)[0] == 0x8000
    except Exception as e:
        logger.append(e)
        return False


def getFoldersOf(folder = None):
    """ Returns subfolders of the given folder as a string tuple. """
    folder = _getUnifiedFolderName(folder)
    try:
        entities = uos.listdir(folder)
        return tuple([fileName for fileName in entities if isDir("{}{}".format(folder, fileName))])
    except Exception as e:
        logger.append(e)
        return ()


def _getUnifiedFolderName(folder):
    if folder is None or folder == "":
        folder = "/"
    elif folder[0] != "/":
        folder = "/" + folder.lower()

    if folder[-1] != "/":
        folder += "/"

    return folder


def getFilenamesOf(folder = None, subFolder = None, suffix = None):
    """ Returns files of the given folder (or /folder/subfolder) as a string tuple. The strings contains only file names
    (without the dot and the suffix). Result can be filtered by suffix."""
    return tuple([file[:file.rindex(".")] for file in getFilesOf(folder, subFolder, suffix)])


def getFilesOf(folder = None, subFolder = None, suffix = None):
    """ Returns files of the given folder (or /folder/subfolder) as a string tuple. Result can be filtered by suffix."""
    path = _getUnifiedFolderPath(folder, subFolder)

    if suffix is None:
        suffix = ""
        chopIndex = 2147483647
    else:
        suffix = "." + suffix
        chopIndex = 0 - len(suffix)

    try:
        entities = uos.listdir(path)
        return tuple([name for name in entities if name[chopIndex:] == suffix and isFile("{}{}".format(path, name))])
    except Exception as e:
        logger.append(e)
        return ()


def _getUnifiedFolderPath(folder, subFolder):
    folder = _getUnifiedFolderName(folder)

    if folder == "/":
        return "/", ""

    subFolder = _getUnifiedFolderName(subFolder)

    return "{}{}".format(folder, "" if subFolder == "/" else subFolder[1:])



def createJsonInstanceFrom(folder = None, subFolder = None, file = None):
    presentInt = (0 if _isBlank(folder) else 4) + (0 if _isBlank(subFolder) else 2) + (0 if _isBlank(file) else 1)
    if presentInt == 0:
        return _createFolderInstance("", True)
    elif presentInt == 4:
        return _createFolderInstance(folder)
    elif presentInt == 6:
        return _createSubFolderInstance(folder, subFolder)
    elif presentInt == 7:
        return _createFileInstance(folder, subFolder, file)


def _isBlank(text):
    return text is None or text == ""


def _createFolderInstance(folder, isRoot = False):
    job = "Request: Get the folder '{}'{}.".format(folder, "" if isRoot else " [ / ]")
    realFolder = _getUnifiedFolderName(folder)

    if isRoot or isDir(realFolder):
        subFolders    = getFoldersOf(realFolder)
        folderLink    = "{}{}".format(_hostLink, realFolder[1:])
        folderRawLink = "{}{}".format(_rawLink, realFolder[1:])

        return "200 OK", job, {
            "name": "root" if isRoot else folder,
            "type": "folder",
            "href": folderLink,
            "raw":  folderRawLink,

            "parent": {} if isRoot else {"name": "root", "type": "folder", "href": _hostLink, "raw": _rawLink},

            "children": [{"name": subFolder, "type": "folder", "href": "{}{}/".format(folderLink, subFolder),
                          "raw": "{}{}/".format(folderRawLink, subFolder)} for subFolder in subFolders]}
    else:
        return "404 Not Found", job + " Cause: No such folder: '{}'".format(folder), {}


def _createSubFolderInstance(folder, subFolder):
    return ""


def _createFileInstance(folder, subFolder, file):
    return ""

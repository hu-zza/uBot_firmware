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

import ubot_config as config
import ubot_logger as logger


def doesExist(path):
    try:
        uos.stat(normalizePath(path))
        return True
    except:
        return False


def normalizePath(path):
    """ Prepare for error-free using. Make it lowercase, and add leading slash if necessary. """
    if path is None or path == "":
        return "/"
    else:
        return path if path[0] == "/" else "/{}".format(path.lower())


def normalizeFolderPath(folder):
    folder = normalizePath(folder)
    return folder if folder[-1] == "/" else "{}/".format(folder)


def getNormalizedPathOf(pathAsList = (), fileName = None):
    if 0 == len(pathAsList):
        path = "/"
    else:
        path = normalizeFolderPath("/".join(pathAsList))

    return path if fileName is None else "{}{}".format(path, fileName)


def isFolder(path):
    return _typeIntEqualsExpectedInt(path, 0x4000)


def isFile(path):
    return _typeIntEqualsExpectedInt(path, 0x8000)


def _typeIntEqualsExpectedInt(path, expectedInt):
    path = normalizePath(path)

    if doesExist(path):
        try:
            return uos.stat(path)[0] == expectedInt
        except Exception as e:
            logger.append(e)
            return False
    else:
        logger.append(AttributeError("Path '{}' doesn't exist."))
        return False


def doesFolderExist(path):
    if doesExist(path):
        return isFolder(path)
    else:
        return False


def doesFileExist(path):
    if doesExist(path):
        return isFile(path)
    else:
        return False


def getFoldersOf(folder = None):
    """ Returns subfolders of the given folder as a string tuple. """
    folder = normalizeFolderPath(folder)
    try:
        entities = uos.listdir(folder)
        return tuple([fileName for fileName in entities if isFolder("{}{}".format(folder, fileName))])
    except Exception as e:
        logger.append(e)
        return ()


def getFilenamesOf(folder = None, subFolder = None, suffix = None):
    """ Returns files of the given folder (or /folder/subfolder) as a string tuple. The strings contains only file names
    (without the dot and the suffix). Result can be filtered by suffix."""
    return tuple([file[:file.rindex(".")] for file in getFilesOf(folder, subFolder, suffix)])


def getFilenamesOfPath(path = None, suffix = None):
    """ Returns files of the given path as a string tuple. The strings contains only file names
    (without the dot and the suffix). Result can be filtered by suffix."""
    return tuple([file[:file.rindex(".")] for file in getFilesOfPath(path, suffix)])


def getFilesOf(folder = None, subFolder = None, suffix = None):
    """ Returns files of the given folder (or /folder/subfolder) as a string tuple. Result can be filtered by suffix."""
    return getFilesOfPath(getNormalizedPathOf((folder, subFolder)), suffix)


def getFilesOfPath(path = None, suffix = None):
    """ Returns files of the given path as a string tuple. Result can be filtered by suffix."""
    path = normalizeFolderPath(path)
    suffix, chopIndex = _getSuffixAndChopIndexFrom(suffix)

    try:
        entities = uos.listdir(path)
        return tuple([name for name in entities if name[chopIndex:] == suffix and isFile("{}{}".format(path, name))])
    except Exception as e:
        logger.append(e)
        return ()


def _getSuffixAndChopIndexFrom(suffix):
    if suffix is None:
        return "", 2147483647
    else:
        return ".{}".format(suffix), -1 - len(suffix)


def getFile(path, isJson = False):
    path = normalizePath(path)

    if doesFileExist(path):
        try:
            with open(path, "r") as file:
                if isJson:
                    return tuple([ujson.loads(line) for line in file])
                else:
                    return tuple([line for line in file])
        except Exception as e:
            logger.append(e)
            return ()
    else:
        logger.append(AttributeError("Path '{}' doesn't exist.".format(path)))
        return ()


def saveFile(path, lines):
    path = normalizePath(path)
    # TODO: checks... and some odds and ends
    try:
        with open(path, "w") as file:
            if isinstance(lines, tuple) or isinstance(lines, list):
                for line in lines:
                    file.write("{}\n".format(line))
            else:
                file.write("{}\n".format(lines))
            return True
    except Exception as e:
        logger.append(e)
        return False


################################
## REST/JSON related methods

_hostLink = "http://{}/".format(config.get("ap", "ip"))
_rawLink  = _hostLink + "raw/"

def createRestReplyFrom(*path):
    pathLen = len(path)
    if pathLen == 0:
        return _createJsonFolderInstance("", True)
    elif pathLen == 1:
        return _createJsonFolderInstance(path[0])
    elif pathLen == 2:
        return _createJsonSubFolderInstance(path[0], path[1])
    elif pathLen == 3:
        return _createJsonFileInstance(path[0], path[1], path[2])


def _isBlank(text):
    return text is None or text == ""


def _createJsonFolderInstance(folder, isRoot = False):
    realFolder = normalizeFolderPath(folder)
    job = "Request: Get the folder '{}'.".format(realFolder)

    if isRoot or isFolder(realFolder):
        subFolders    = getFoldersOf(realFolder)
        folderLink    = "{}{}".format(_hostLink, realFolder[1:])
        folderRawLink = "{}{}".format(_rawLink, realFolder[1:])

        return "200 OK", job, {
            "name": "root" if isRoot else folder,
            "type": "folder",
            "href": folderLink,
            "raw":  folderRawLink,

            "parent": {} if isRoot else {"name": "root",
                                         "type": "folder",
                                         "href": _hostLink,
                                         "raw": _rawLink},

            "children": [{"name": subFolder,
                          "type": "folder",
                          "href": "{}{}/".format(folderLink, subFolder),
                          "raw":  "{}{}/".format(folderRawLink, subFolder)} for subFolder in subFolders]}
    else:
        return "404 Not Found", job + " Cause: No such folder.", {}


def _createJsonSubFolderInstance(folder, subFolder):
    path = getNormalizedPathOf((folder, subFolder))
    job = "Request: Get the folder '{}'.".format(path)

    if isFolder(path):
        files         = getFilenamesOfPath(path, "txt")                                           #! Burnt-in txt suffix
        parent        = normalizeFolderPath(folder)
        folderLink    = "{}{}".format(_hostLink, path[1:])
        folderRawLink = "{}{}".format(_rawLink, path[1:])

        return "200 OK", job, {
            "name": subFolder,
            "type": "folder",
            "href": folderLink,
            "raw":  folderRawLink,

            "parent": {"name": folder,
                       "type": "folder",
                       "href": "{}{}".format(_hostLink, parent[1:]),
                       "raw":  "{}{}".format(_rawLink, parent[1:])},

            "children": [{"name": file,
                          "type": "file",
                          "href": "{}{}".format(folderLink, file),
                          "raw":  "{}{}.txt".format(folderRawLink, file)} for file in files]}     #! Burnt-in txt suffix
    else:
        return "404 Not Found", job + " Cause: No such folder.", {}


def _createJsonFileInstance(folder, subFolder, file):
    _file  = file if file == "" or file[-4:] == ".txt" else "{}.txt".format(file)                 #! Burnt-in txt suffix
    path   = getNormalizedPathOf((folder, subFolder), _file)                                      #! if file != ""
    parent = getNormalizedPathOf((folder, subFolder))
    job = "Request: Get the file '{}'.".format(path)

    if doesFolderExist(parent):
        if doesFileExist(path):
            isJson = folder in config.get("system", "json_folders")
            return "200 OK", job, {
                "name": file,
                "type": "file",
                "href": "{}{}".format(_hostLink, path[1:path.rindex(".")]),
                "raw":  "{}{}".format(_rawLink, path[1:]),
                "parent": {
                    "name": subFolder,
                    "type": "folder",
                    "href": "{}{}".format(_hostLink, parent[1:]),
                    "raw":  "{}{}".format(_rawLink, parent[1:])
                },
                "children": [],
                "value": getFile(path, isJson)}
        else:
            return "404 Not Found", job + " Cause: No such file.", {}
    else:
        return "403 Forbidden", job + " Cause: Invalid path in URI.", {}

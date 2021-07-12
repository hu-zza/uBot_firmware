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
    """ Prepare for error-free using. Make it stripped, lowercase, and add leading slash if necessary. """
    if path is None or path == "":
        return "/"
    else:
        try:
            path = path.strip().lower()
            path = path if path[0] == "/" else "/{}".format(path)
            return _sanitizePath(path)
        except Exception as e:
            logger.append(e)
            logger.append(AttributeError("ubot_data#normalizePath\r\n'{}' is not a string representing a path.\r\n"
                                         .format(path)))
            return "/Exception @ ubot_data#normalizePath"


def _sanitizePath(path):
    path = path.strip(".")

    while 0 <= path.find("/../") or 0 <= path.find("/./"):
        path = path.replace("/../", "/").replace("/./", "/")
    return path


def normalizeFolderPath(folder):
    folder = normalizePath(folder)
    return folder if folder[-1] == "/" else "{}/".format(folder)


def normalizeTxtFilename(filename):
    if isinstance(filename, str):
        filename = filename.lower()
        return filename if filename.endswith(".txt") or filename == "" else "{}.txt".format(filename)
    else:
        logger.append(AttributeError("ubot_data#normalizeTxtFilename\r\n'{}' is not a string representing a filename.\r\n"
                                     .format(filename)))
        return "Exception @ ubot_data#normalizeTxtFilename"


def getNormalizedPathOf(pathAsList = (), filename = ""):
    if pathAsList is None or len(pathAsList) == 0:
        path = "/"
    elif isinstance(pathAsList, list) or isinstance(pathAsList, tuple):
        path = normalizeFolderPath("".join(normalizePath(item) for item in pathAsList))
    else:
        logger.append(AttributeError("ubot_data#getNormalizedPathOf\r\n'{}' is not an iterable representing a path.\r\n"
                                     .format(pathAsList)))
        return "/Exception @ ubot_data#getNormalizedPathOf/"

    return path if filename == "" else "{}{}".format(path, filename)


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
            logger.append(AttributeError("ubot_data#_typeIntEqualsExpectedInt\r\nCan not process '{}'.\r\n".format(path)))
            return False
    else:
        logger.append(AttributeError("ubot_data#_typeIntEqualsExpectedInt\r\nPath '{}' doesn't exist.\r\n".format(path)))
        return False


def getFoldersOf(folder = ""):
    """ Returns subfolders of the given folder as a string tuple. """
    folder = normalizeFolderPath(folder)
    try:
        entities = uos.listdir(folder)
        return tuple(filename for filename in entities if isFolder("{}{}".format(folder, filename)))
    except Exception as e:
        logger.append(e)
        logger.append(AttributeError("ubot_data#getFoldersOf\r\nFolder '{}' doesn't exist.\r\n".format(folder)))
        return ()


def getFileNamesOf(folder ="", subFolder ="", suffix =""):
    """ Returns files of the given folder (or /folder/subFolder) as a string tuple. The strings contains only file names
    (without the dot and the suffix). Result can be filtered by suffix."""
    return tuple(file[:file.rindex(".")] for file in getFilesOf(folder, subFolder, suffix))


def getFileNamesOfPath(path ="", suffix =""):
    """ Returns files of the given path as a string tuple. The strings contains only file names
    (without the dot and the suffix). Result can be filtered by suffix."""
    return tuple(file[:file.rindex(".")] for file in getFilesOfPath(path, suffix))


def getFilesOf(folder = "", subFolder = "", suffix = ""):
    """ Returns filenames (file_name.suffix) of the given folder (or /folder/subFolder) as a string tuple. Result can be
     filtered by suffix."""
    return getFilesOfPath(getNormalizedPathOf((folder, subFolder)), suffix)


def getFilesOfPath(path = "", suffix = ""):
    """ Returns filenames (file_name.suffix) of the given path as a string tuple. Result can be filtered by suffix."""
    path = normalizeFolderPath(path)

    try:
        entities = uos.listdir(path)
        return tuple(name for name in entities if name.endswith(suffix) and isFile("{}{}".format(path, name)))
    except Exception as e:
        logger.append(e)
        logger.append(AttributeError("ubot_data#getFilesOfPath\r\nPath '{}' doesn't exist.\r\n".format(path)))
        return ()


def getFile(path, isJson = None):
    path = normalizePath(path)

    if doesFileExist(path):
        try:
            likelyJson = isJson is True or isJson is not False and getLineCountOfFile(path) == 1
            with open(path, "r") as file:
                if likelyJson:
                    return tuple(loadsJsonSoftly(line) for line in file)
                else:
                    return tuple(line for line in file)
        except Exception as e:
            logger.append(e)
            logger.append(AttributeError("ubot_data#getFile\r\nCan not process '{}'.\r\n".format(path)))
            return ()
    else:
        logger.append(AttributeError("ubot_data#getFile\r\nPath '{}' doesn't exist.\r\n".format(path)))
        return ()


def loadsJsonSoftly(line):
    try:
        return ujson.loads(line)
    except:
        return line


def getLineCountOfFile(path):
    path = normalizePath(path)
    if isFile(path):
        return sum(1 for _ in open(path))
    else:
        return 0


def getEntityCountOfFolder(path):
    path = normalizePath(path)
    if isFolder(path):
        return len(uos.listdir(path))
    else:
        return 0


def canCreate(path):
    if not doesExist(path):
        return _checkPermission(path, "write_rights")
    else:
        return False


def canWrite(path):
    return _checkPermission(path, "write_rights")


def canDelete(path):
    if doesExist(path):
        if isFolder(path) and 0 < len(uos.listdir(path)):
            return False
        return _checkPermission(path, "delete_rights")
    else:
        return False


def canModify(path):
    if doesExist(path):
        return _checkPermission(path, "modify_rights")
    else:
        return False


def _checkPermission(path, nameOfPrefixSet):
    path = normalizePath(path)
    for prefix in config.get("data", nameOfPrefixSet):
        if path.find(prefix) == 0 and len(prefix) < len(path):
            return True
    return False


def createFolderOf(folder = "", subFolder = ""):
    return createFolderOfPath(getNormalizedPathOf((folder, subFolder)))


def createFolderOfPath(path):
    if canCreate(path):
        uos.mkdir(normalizeFolderPath(path)[:-1])
        return doesExist(path)
    else:
        return False


def saveFileOf(pathAsList, filename, lines, isRecursive = False):
    return saveFileOfPath(
        getNormalizedPathOf(pathAsList, normalizeTxtFilename(filename)),
        lines, isRecursive)


def saveFileOfPath(path, lines, isRecursive = False):
    if canWrite(path) or canModify(path):
        return _saveFile(path, lines, isRecursive)
    else:
        return ""


def _saveFile(path, lines, isRecursive = False):
    path = normalizePath(path)
    written = 0
    try:
        if isRecursive:
            _createFoldersIfNeeded(path)

        with open(path, "w") as file:
            if isinstance(lines, tuple) or isinstance(lines, list):
                for line in lines:
                    written += _writeOut(file, line, False)
            elif isinstance(lines, str):
                written += _writeOut(file, lines, False)
            elif isinstance(lines, dict):
                written += _writeOut(file, lines, True)
            else:
                return ""

            return path
    except Exception as e:
        logger.append(e)
        logger.append(AttributeError("ubot_data#_saveFile\r\nCan not process '{}'.\r\n".format(path)))
        return ""


def _createFoldersIfNeeded(path):
        pathArray = path.split("/")[1:-1]
        elements = []
        for i in range(len(pathArray)):
            elements.append(pathArray[i])
            path = getNormalizedPathOf(elements)
            if not doesExist(path):
                createFolderOfPath(path)


def _writeOut(file, line, isJson = False):
    toWrite = "{}\r\n".format(ujson.dumps(line) if isJson else line)
    return file.write(toWrite) - len(toWrite)


def deleteFileOfPath(path):
    if canDelete(path):
        if isFile(path):
            try:
                uos.remove(path)
                return True
            except Exception as e:
                logger.append(e)
                logger.append(AttributeError("ubot_data#deleteFileOfPath\r\nCan not delete '{}'.\r\n".format(path)))
                return False
        else:
            logger.append(AttributeError("ubot_data#deleteFileOfPath\r\n'{}' is not a file.\r\n".format(path)))
            return False
    else:
        if doesExist(path):
            logger.append(AttributeError("ubot_data#deleteFileOfPath\r\nMissing delete permission.\r\n".format(path)))
        else:
            logger.append(AttributeError("ubot_data#deleteFileOfPath\r\nPath '{}' doesn't exist.\r\n".format(path)))
        return False


def deleteFolderOfPath(path):
    if canDelete(path):
        if isFolder(path):
            try:
                uos.rmdir(path)
                return True
            except Exception as e:
                logger.append(e)
                logger.append(AttributeError("ubot_data#deleteFolderOfPath\r\nCan not delete '{}'.\r\n".format(path)))
                return False
        else:
            logger.append(AttributeError("ubot_data#deleteFolderOfPath\r\n'{}' is not a folder.\r\n".format(path)))
            return False
    else:
        if doesExist(path):
            logger.append(AttributeError("ubot_data#deleteFolderOfPath\r\nMissing delete permission.\r\n".format(path)))
        else:
            logger.append(AttributeError("ubot_data#deleteFolderOfPath\r\nPath '{}' doesn't exist.\r\n".format(path)))
        return False



################################
## Other data related helpers

def dumpException(exception):
    return "{} {}".format(exception.__class__, exception.args)


################################
## REST/JSON related methods

_hostLink = "http://{}/".format(config.get("ap", "ip"))
_rawLink  = _hostLink + "raw/"

def createRestReplyFrom(*path):
    clearPath = _deleteSpaceholders(path)
    clearPathLen = len(clearPath)

    if clearPathLen < 2:
        return _createJsonFolderInstance(path[0], path[0] == "")    # Using path with placeholders, maybe it's [""] * 11
    elif clearPathLen == 2:
        return _createJsonSubFolderInstance(clearPath[0], clearPath[1])
    elif clearPathLen == 3:
        return _createJsonFileInstance(clearPath[0], clearPath[1], clearPath[2])
    else:
        return ()


def _deleteSpaceholders(path):
    return [attribute for attribute in path if not _isBlank(attribute)]


def _isBlank(text):
    return text is None or text == ""


def _createJsonFolderInstance(folder, isRoot = False):
    realFolder = normalizeFolderPath(folder)
    job = "Request: Get the folder '{}'.".format(realFolder)

    if isRoot or doesFolderExist(realFolder):
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
        return "404 Not Found", job + " Cause: The folder doesn't exist.", {}


def _createJsonSubFolderInstance(folder, subFolder):
    path = getNormalizedPathOf((folder, subFolder))
    job = "Request: Get the folder '{}'.".format(path)

    if doesFolderExist(path):
        files         = getFileNamesOfPath(path, "txt")              #! Burnt-in txt suffix: filtered by it, but chopped
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
        return "404 Not Found", job + " Cause: The folder doesn't exist.", {}


def _createJsonFileInstance(folder, subFolder, file):
    _file  = normalizeTxtFilename(logger.normalizeLogTitle(file) if folder == "log" else file)
    path   = getNormalizedPathOf((folder, subFolder), _file)
    parent = getNormalizedPathOf((folder, subFolder))
    job = "Request: Get the file '{}'.".format(path)

    if doesFolderExist(parent):
        if doesFileExist(path):
            isJson = True if folder in config.get("data", "json_folders") else None
            return "200 OK", job, {
                "name": _file,
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
            return "404 Not Found", job + " Cause: The file doesn't exist.", {}
    else:
        return "403 Forbidden", job + " Cause: Invalid path in the URL.", {}

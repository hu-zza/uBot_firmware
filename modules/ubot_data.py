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


class Path:
    """ Represents a path in filesystem. The main characteristic is initialized immediately after construction,
    but rights (create, write, delete, modify) are lazy. """
    def __init__(self, path: str) -> None:
        self.path  = path
        self.array = ()
        self.size  = 0
        self.isExist  = False
        self.isFolder = False
        self.isFile   = False
        self.isTxt    = False
        self.description = "[invalid]"
        self.canWrite  = None
        self.canDelete = None
        self.canModify = None

        _initializePath(self)

    def __str__(self) -> str:
        return self.path



def _initializePath(path: Path) -> None:
    """ Firstly tries to initialize Path object from the original path string,
    if it fails, appends the suffix ".txt" and tries again. """
    try:
        pathString = _normalizePathOrThrow(path.path)

        if _doesExist(pathString):
            path.isExist = True

            if uos.stat(pathString)[0] == 0x4000:     # Folder
                path.isFolder = True
                description = "folder '{}' ({})"

                if not pathString.endswith("/"):
                    pathString = "{}/".format(pathString)
            else:
                path.isFile = True
                description = "file '{}' ({})"
                path.isTxt = pathString.endswith(".txt")
        elif _doesExist("{}.txt".format(pathString)):                                             #! Burnt-in txt suffix
            path.isExist = True
            path.isFile  = True
            path.isTxt   = True
            pathString   = "{}.txt".format(pathString)
            description  = "file '{}' ({})"
        else:
            description = "[non-existent] '{}' ({})"

        array = tuple(item for item in pathString.split("/") if item != "")
        path.description = description.format(array[-1], "/{}".format("/".join(array[:-1])))
        path.path  = pathString
        path.array = array
        path.size  = len(array)

    except Exception as e:
        logger.append(e)
        logger.append(AttributeError("ubot_data#_initializePath\r\nCan not initialize Path object with path '{}'.\r\n"
                                     .format(path)))
        _invalidatePath(path)


def _invalidatePath(path: Path) -> None:
    path.path  = ""
    path.array = ()
    path.size  = 0
    path.isExist  = False
    path.isFolder = False
    path.isFile   = False
    path.isTxt    = False
    path.description = "[invalid]"
    path.canWrite  = False
    path.canDelete = False
    path.canModify = False


def _doesExist(path: str) -> bool:
    try:
        uos.stat(path)
        return True
    except:
        return False


def _isFolder(path: str) -> bool:
    try:
        return _typeIntEqualsExpectedInt(path, 0x4000)
    except Exception as e:
        logger.append(e)
        logger.append(AttributeError("ubot_data#_isFolder\r\nCan not process '{}'.\r\n".format(path)))
        return False


def _isFile(path: str) -> bool:
    try:
        return _typeIntEqualsExpectedInt(path, 0x8000)
    except Exception as e:
        logger.append(e)
        logger.append(AttributeError("ubot_data#_isFile\r\nCan not process '{}'.\r\n".format(path)))
        return False


def _typeIntEqualsExpectedInt(path: str, expectedInt: int) -> bool:
    return uos.stat(path)[0] == expectedInt


def _normalizePath(path: str) -> str:
    """ Prepare for error-free using: Make it stripped, lowercase, add leading slash if necessary, and sanitize it. """
    try:
        return _normalizePathOrThrow(path)
    except Exception as e:
        logger.append(e)
        logger.append(AttributeError("ubot_data#_normalizePath\r\n'{}' is not a string representing a path.\r\n"
                                     .format(path)))
        return "/Exception @ ubot_data#_normalizePath"


def _normalizePathOrThrow(path: str) -> str:
    """ Prepare for error-free using: Make it stripped, lowercase, add leading slash if necessary, and sanitize it. """
    if path is None or path == "":
        return "/"
    else:
        path = path.strip().lower()
        path = path if path[0] == "/" else "/{}".format(path)
        return _sanitizePath(path)


def _sanitizePath(path: str) -> str:
    path = path.strip(".")
    path = _replaceWhileFound(path, "//", "/")
    path = _replaceWhileFound(path, "/./", "/")
    return _replaceWhileFound(path, "/../", "/")


def _replaceWhileFound(path: str, old: str, new: str) -> str:
    while 0 <= path.find(old):
        path = path.replace(old, new)
    return path


def createPathOf(*pathArray: str) -> Path:
    return createPath(pathArray)


def createPath(pathArray: tuple) -> Path:
    try:
        return Path("/" if pathArray is None or len(pathArray) == 0 else "/".join(pathArray))
    except Exception as e:
        logger.append(AttributeError("ubot_data#createPath\r\n'{}' is not a string iterable representing a path.\r\n"
                                     .format(pathArray)))
    return INVALID_PATH

INVALID_PATH = Path("")
_invalidatePath(INVALID_PATH)


def createFolderOf(*pathArray: str) -> bool:
    return createFolder(createPath(pathArray))


def createFolder(path: Path) -> bool:
    if canCreate(path):
        pathString = path.path[:-1]
        uos.mkdir(pathString)
        return _doesExist(pathString)
    else:
        return False


def createFoldersOfPath(path: Path) -> None:
    if canWrite(path):
        pathArray = path.array
        elements = []
        for i in range(len(pathArray) - 1 if path.isFile else 0):
            elements.append(pathArray[i])
            path = "/{}".format("/".join(elements))
            if not _doesExist(path):
                createFolder(createPath(elements))


def normalizeTxtFilename(filename):
    if isinstance(filename, str):
        filename = filename.lower()
        return filename if filename.endswith(".txt") or filename == "" else "{}.txt".format(filename)
    else:
        logger.append(AttributeError("ubot_data#normalizeTxtFilename\r\n'{}' is not a string representing a filename.\r\n"
                                     .format(filename)))
        return "Exception @ ubot_data#normalizeTxtFilename"



def doesFolderExist(path: Path) -> bool:
    return path.isExist and path.isFolder


def doesFileExist(path: Path) -> bool:
    return path.isExist and path.isFile


def getFoldersOf(path: Path) -> tuple:
    """ Returns subfolders of the given folder as a string tuple. """
    if doesFolderExist(path):
        try:
            return tuple(filename for filename in uos.listdir(path.path) if _isFolder("{}{}".format(path, filename)))
        except Exception as e:
            logger.append(e)
            logger.append(AttributeError("ubot_data#getFoldersOf\r\nCan not process '{}'.\r\n".format(path)))
            return ()
    else:
        logger.append(AttributeError("ubot_data#getFoldersOf\r\nFolder '{}' doesn't exist.\r\n".format(path)))
        return ()


def getFileNameListOf(folder = "", subFolder = "", suffix = "") -> tuple:
    """ Returns files of the given folder (or /folder/subFolder) as a string tuple. The strings contains only file names
    (without the dot and the suffix). Result can be filtered by suffix."""
    return tuple(file[:file.rindex(".")] for file in getFileListOf(folder, subFolder, suffix))


def getFileListOf(folder = "", subFolder = "", suffix = "") -> tuple:
    """ Returns filenames (file_name.suffix) of the given folder (or /folder/subFolder) as a string tuple. Result can be
     filtered by suffix."""
    return getFileList(createPathOf(folder, subFolder), suffix)


def getFileNameList(path: Path, suffix = "") -> tuple:
    """ Returns files of the given path as a string tuple. The strings contains only file names
    (without the dot and the suffix). Result can be filtered by suffix."""
    return tuple(file[:file.rindex(".")] for file in getFileList(path, suffix))


def getFileList(path: Path, suffix = "") -> tuple:
    """ Returns filenames (file_name.suffix) of the given path as a string tuple. Result can be filtered by suffix."""
    try:
        pathString = path.path
        return tuple(name for name in uos.listdir(pathString)
                     if name.endswith(suffix) and _isFile("{}{}".format(pathString, name)))
    except Exception as e:
        logger.append(e)
        logger.append(AttributeError("ubot_data#getFilesOfPath\r\nPath '{}' doesn't exist.\r\n".format(path)))
        return ()


def getFile(path: Path, isJson: bool = None) -> tuple:
    if assertPath(path, True, False, True):
        try:
            likelyJson = isJson is True or isJson is not False and getLineCountOfFile(path) == 1
            with open(path.path, "r") as file:
                if likelyJson:
                    return tuple(__loadsJsonSoftly(line) for line in file)
                else:
                    return tuple(line for line in file)
        except Exception as e:
            logger.append(e)
            logger.append(AttributeError("ubot_data#getFile\r\nCan not process '{}'.\r\n".format(path)))
            return ()
    else:
        logger.append(AttributeError("ubot_data#getFile\r\nPath '{}' does not meet the requirements.\r\n".format(path)))
        return ()


def __loadsJsonSoftly(line: str) -> object:
    try:
        return ujson.loads(line)
    except:
        return line


def getLineCountOfFile(path: Path) -> int:
    if path.isFile:
        return sum(1 for _ in open(path.path))
    else:
        return 0


def getEntityCountOfFolder(path: Path) -> int:
    if doesFolderExist(path):
        return len(uos.listdir(path))
    else:
        return 0


def canCreate(path: Path) -> bool:
    if path.canWrite is None:
        path.canWrite = _checkPermission(path.path, "write_rights")

    return path.canWrite and not path.isExist


def canWrite(path: Path) -> bool:
    if path.canWrite is None:
        path.canWrite = _checkPermission(path.path, "write_rights")

    return path.canWrite


def canDelete(path: Path) -> bool:
    if path.canDelete is None:
        path.canDelete = _checkPermission(path.path, "delete_rights")

    return path.canDelete and path.isExist


def canModify(path: Path) -> bool:
    if path.canModify is None:
        path.canModify = _checkPermission(path.path, "modify_rights")

    return path.canModify and path.isExist


def _checkPermission(path: str, nameOfPrefixSet: str) -> bool:
    for prefix in config.get("data", nameOfPrefixSet):
        if path.find(prefix) == 0 and len(prefix) < len(path):
            return True
    return False


def assertPath(path: Path, isExist = False, isFolder = False, isFile = False, isTxt = False) -> bool:
    if path.isExist != isExist:
        if path.isExist:
            logger.append(AttributeError("ubot_data#_assertPath\r\nPath '{}' exists.\r\n".format(path)))
        else:
            logger.append(AttributeError("ubot_data#_assertPath\r\nPath '{}' does not exist.\r\n".format(path)))
        return False

    if path.isFolder != isFolder:
        if path.isFolder:
            logger.append(AttributeError("ubot_data#_assertPath\r\nPath '{}' represents a folder.\r\n".format(path)))
        else:
            logger.append(AttributeError("ubot_data#_assertPath\r\nPath '{}' does not represent a folder.\r\n".format(path)))
        return False

    if path.isFile != isFile:
        if path.isFile:
            logger.append(AttributeError("ubot_data#_assertPath\r\nPath '{}' represents a file.\r\n".format(path)))
        else:
            logger.append(AttributeError("ubot_data#_assertPath\r\nPath '{}' does not represent a file.\r\n".format(path)))
        return False

    if path.isTxt != isTxt:
        if path.isTxt:
            logger.append(AttributeError("ubot_data#_assertPath\r\nPath '{}' represents a txt file.\r\n".format(path)))
        else:
            logger.append(AttributeError("ubot_data#_assertPath\r\nPath '{}' does not represent a txt file.\r\n".format(path)))
        return False

    return True


def saveFile(path: Path, lines: object, isRecursive: bool = False) -> bool:
    if canWrite(path) or canModify(path):
        path = _normalizePath(path)
        written = 0
        try:
            if isRecursive:
                createFoldersOfPath(path)

            with open(path, "w") as file:
                if isinstance(lines, tuple) or isinstance(lines, list):
                    for line in lines:
                        written += _writeOut(file, line, False)
                elif isinstance(lines, str):
                    written += _writeOut(file, lines, False)
                elif isinstance(lines, dict):
                    written += _writeOut(file, lines, True)
                else:
                    return False

            return written == 0
        except Exception as e:
            logger.append(e)
            logger.append(AttributeError("ubot_data#saveFile\r\nCan not process '{}'.\r\n".format(path)))
            return False
    else:
        logger.append(AttributeError("ubot_data#saveFile\r\nCan not process '{}'.\r\n".format(path)))
        return False


def _writeOut(file: object, line: str, isJson: bool = False) -> int:
    toWrite = "{}\r\n".format(ujson.dumps(line) if isJson else line)
    return file.write(toWrite) - len(toWrite)


def deleteFileOfPath(path: Path) -> bool:
    if canDelete(path):
        if path.isFile:
            try:
                uos.remove(path.path)
                path.isExist = False
                return True
            except Exception as e:
                logger.append(e)
                logger.append(AttributeError("ubot_data#deleteFileOfPath\r\nCan not delete '{}'.\r\n".format(path)))
                return False
        else:
            logger.append(AttributeError("ubot_data#deleteFileOfPath\r\n'{}' is not a file.\r\n".format(path)))
            return False
    else:
        if path.isExist:
            logger.append(AttributeError("ubot_data#deleteFileOfPath\r\nMissing delete permission.\r\n"))
        else:
            logger.append(AttributeError("ubot_data#deleteFileOfPath\r\nPath '{}' doesn't exist.\r\n".format(path)))
        return False


def deleteFolderOfPath(path: Path) -> bool:
    if canDelete(path):
        if path.isFolder:
            try:
                uos.rmdir(path.path)
                path.isExist = False
                return True
            except Exception as e:
                logger.append(e)
                logger.append(AttributeError("ubot_data#deleteFolderOfPath\r\nCan not delete '{}'.\r\n".format(path)))
                return False
        else:
            logger.append(AttributeError("ubot_data#deleteFolderOfPath\r\n'{}' is not a folder.\r\n".format(path)))
            return False
    else:
        if _doesExist(path):
            logger.append(AttributeError("ubot_data#deleteFolderOfPath\r\nMissing delete permission.\r\n"))
        else:
            logger.append(AttributeError("ubot_data#deleteFolderOfPath\r\nPath '{}' doesn't exist.\r\n".format(path)))
        return False



################################
## Other data related helpers

def dumpException(exception):
    return "{} {}".format(exception.__class__, exception.args)


################################
## REST/JSON related methods

_hostLink = "http://{}".format(config.get("ap", "ip"))
_rawLink  = "{}/raw".format(_hostLink)

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
    path = Path(folder)
    name = str(path)
    job  = "Request: Get the folder '{}'.".format(name)

    if isRoot or path.isExist:
        subFolders    = getFoldersOf(path)
        folderLink    = "{}{}".format(_hostLink, name)
        folderRawLink = "{}{}".format(_rawLink,  name)

        return "200 OK", job, {
            "name": "root" if isRoot else folder,
            "type": "folder",
            "href": folderLink,
            "raw":  folderRawLink,

            "parent": {} if isRoot else {"name": "root",
                                         "type": "folder",
                                         "href": "{}/".format(_hostLink),
                                         "raw":  "{}/".format(_rawLink)},

            "children": [{"name": subFolder,
                          "type": "folder",
                          "href": "{}{}/".format(folderLink, subFolder),
                          "raw":  "{}{}/".format(folderRawLink, subFolder)} for subFolder in subFolders]}
    else:
        return "404 Not Found", job + " Cause: The folder doesn't exist.", {}


def _createJsonSubFolderInstance(folder, subFolder):
    path = createPathOf(folder, subFolder)
    name = str(path)
    job  = "Request: Get the folder '{}'.".format(name)

    if assertPath(path, True, True):
        files         = getFileNameList(path, "txt")              #! Burnt-in txt suffix: filtered by it, but chopped
        parentName    = name[:-len(subFolder) - 1]
        folderLink    = "{}{}".format(_hostLink, name)
        folderRawLink = "{}{}".format(_rawLink,  name)

        return "200 OK", job, {
            "name": subFolder,
            "type": "folder",
            "href": folderLink,
            "raw":  folderRawLink,

            "parent": {"name": folder,
                       "type": "folder",
                       "href": "{}{}".format(_hostLink, parentName),
                       "raw":  "{}{}".format(_rawLink,  parentName)},

            "children": [{"name": file,
                          "type": "file",
                          "href": "{}{}".format(folderLink, file),
                          "raw":  "{}{}.txt".format(folderRawLink, file)} for file in files]}     #! Burnt-in txt suffix
    else:
        return "404 Not Found", job + " Cause: The folder does not exist.", {} #! If it exists as a file, doesn't matter


def _createJsonFileInstance(folder, subFolder, file):
    path   = createPathOf(folder, subFolder, logger.normalizeLogTitle(file) if folder == "log" else file)
    name   = str(path)
    parent, fileName = name.rsplit("/", 1)
    parent = "{}/".format(parent)

    job = "Request: Get the file '{}'.".format(name)

    if assertPath(path, True, False, True):
        isJson = True if folder in config.get("data", "json_folders") else None
        return "200 OK", job, {
            "name": fileName,
            "type": "file",
            "href": "{}{}".format(_hostLink, name[:name.rindex(".")]),
            "raw":  "{}{}".format(_rawLink,  name),
            "parent": {
                "name": subFolder,
                "type": "folder",
                "href": "{}{}".format(_hostLink, parent),
                "raw":  "{}{}".format(_rawLink,  parent)
            },
            "children": [],
            "value": getFile(path, isJson)}
    else:
        return "404 Not Found", job + " Cause: The file does not exist.", {}

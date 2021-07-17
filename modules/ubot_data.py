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

import ubot_logger as logger


class Path:
    """ Represents a path in filesystem. The main characteristic is initialized immediately after construction,
    but rights (create, write, delete, modify) are lazy. """
    def __init__(self, path: str) -> None:
        self.path  = path
        self.array = ()
        self.args  = ()
        self.size  = 0
        self.isExist  = False
        self.isFolder = False
        self.isFile   = False
        self.isTxt    = False
        self.description = "[invalid]"
        self.isWritable   = None
        self.isDeletable  = None
        self.isModifiable = None

        _initializePath(self)


    def __str__(self) -> str:
        return self.path



def _initializePath(path: Path) -> None:
    """ Firstly tries to initialize Path object from the original path string,
    if it fails, appends the suffix ".txt" and tries again. """
    try:
        path.path = _normalizePathOrThrow(path.path)
        array = tuple(item for item in path.path.split("/") if item != "")
        path.array = array
        path.size  = len(array)
        refresh(path)

    except Exception as e:
        logger.append(e)
        logger.append(AttributeError("ubot_data#_initializePath\r\nCan not initialize Path object with path '{}'.\r\n"
                                     .format(path)))
        _invalidatePath(path)


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
        path = _sanitizePath(path)
        return "/" if path == "" else path


def _sanitizePath(path: str) -> str:
    path = path.strip(".")
    path = _replaceWhileFound(path, "/../", "/")
    path = _replaceWhileFound(path, "/./", "/")
    path = _replaceWhileFound(path, "//", "/")
    return "/{}".format(path.strip("/"))


def _replaceWhileFound(path: str, old: str, new: str) -> str:
    while 0 <= path.find(old):
        path = path.replace(old, new)
    return path


def refresh(path: Path) -> None:
    _refreshFlags(path)
    _refreshPathDescription(path)


def _refreshFlags(path: Path) -> None:
    _deleteRightsFlags(path)

    pathString = path.path

    if _doesExist(pathString):
        path.isExist = True
        typeInt = uos.stat(pathString)[0]

        if typeInt == 0x4000:
            path.isFolder = True

            if not pathString.endswith("/"):
                path.path = "{}/".format(pathString)
        elif typeInt == 0x8000:
            path.isFile = True
            path.isTxt = pathString.endswith(".txt")
        else:
            raise AttributeError("ubot_data#_refreshFlags\r\nPath '{}' should represent a folder or a file.\r\n"
                                 .format(path))
    else:
        _deleteBaseFlags(path)


def _refreshPathDescription(path: Path) -> None:
    if path.isExist:
        if path.size == 0:
            path.description = "root folder '/'"
            return
        else:
            if path.isFile:
                template = "file '{}' ({})"
            elif path.isFolder:
                template = "folder '{}' ({})"
            else:
                template = "[invalid]"
    else:
        template = "[non-existent] '{}' ({})"

    path.description = template.format(path.array[-1], "/{}".format("/".join(path.array[:-1])))


def _invalidatePath(path: Path) -> None:
    path.path  = ""
    path.array = ()
    path.args  = ()
    path.size  = 0
    path.description = "[invalid]"
    _deleteBaseFlags(path)
    _deleteRightsFlags(path)


def _makePathNonExistent(path: Path) -> None:
    _deleteBaseFlags(path)
    _deleteRightsFlags(path)
    _refreshPathDescription(path)


def _deleteBaseFlags(path: Path) -> None:
    path.isExist  = False
    path.isFolder = False
    path.isFile   = False
    path.isTxt    = False


def _deleteRightsFlags(path: Path) -> None:
    path.isWritable   = None
    path.isDeletable  = None
    path.isModifiable = None


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



INVALID_PATH = Path("/")
_invalidatePath(INVALID_PATH)
ROOT    = Path("/")
ETC     = Path("/etc")
FUTURE  = Path("/future")
HOME    = Path("/home")
LOG     = Path("/log")
PROGRAM = Path("/program")


def createPathOf(*pathEnumeration: str) -> Path:
    return createPathFrom(pathEnumeration)


def createPathFrom(pathArray: tuple) -> Path:
    try:
        return createPath("/" if pathArray is None or len(pathArray) == 0 else "/".join(pathArray))
    except Exception as e:
        logger.append(e)
        logger.append(AttributeError("ubot_data#createPathFrom\r\n'{}' is not a string iterable representing a path.\r\n"
                                     .format(pathArray)))
        return INVALID_PATH


def createPath(rawPath: str) -> Path:
    try:
        return Path(rawPath)
    except Exception as e:
        logger.append(e)
        logger.append(AttributeError("ubot_data#createPath\r\n'{}' does not represent a valid path.\r\n"
                                     .format(rawPath)))
        return INVALID_PATH


def createFolderOf(*pathEnumeration: str) -> bool:
    return createFolderFrom(pathEnumeration)


def createFolderFrom(pathArray: tuple) -> bool:
    return createFolder(createPathFrom(pathArray))


def createFolder(path: Path) -> bool:
    if assertPathIsCreatable(path):
        try:
            pathString = path.path.rstrip("/")
            uos.mkdir(pathString)
            refresh(path)
            return path.isExist
        except Exception as e:
            logger.append(e)
            logger.append(AttributeError("ubot_data#createFolder\r\nCan not process '{}'.\r\n".format(path)))
            return False
    else:
        logger.append(AttributeError("ubot_data#createFolder\r\nCan not create '{}' because of breach of preconditions.\r\n"
                                     .format(path)))
        return False


def createFoldersAlongPath(path: Path) -> None:
    if canWrite(path):
        pathArray = path.array
        elements = []
        for i in range(len(pathArray)):
            elements.append(pathArray[i])
            path = "/{}".format("/".join(elements))
            if not _doesExist(path):
                createFolderFrom(elements)


def assertPathIsExist(path: Path, isExist = True) -> bool:
    if path.isExist != isExist:
        _logAssertionException("IsExist", path, "exist." if path.isExist else "does not exist.")
        return False
    else:
        return True


def assertPathIsFolder(path: Path, isFolder = True) -> bool:
    if path.isFolder != isFolder:
        _logAssertionException("IsFolder", path, "represents a folder." if path.isFolder else "does not represent a folder.")
        return False
    else:
        return True


def assertPathIsFile(path: Path, isFile = True) -> bool:
    if path.isFile != isFile:
        _logAssertionException("IsFile", path, "represents a file." if path.isFile else "does not represent a file.")
        return False
    else:
        return True


def assertPathIsTxt(path: Path, isTxt = True) -> bool:
    if path.isTxt != isTxt:
        _logAssertionException("IsTxt", path, "has '.txt' suffix." if path.isTxt else "has no '.txt' suffix.")
        return False
    else:
        return True


def assertPathIsCreatable(path: Path, isCreatable = True) -> bool:
    property = canCreate(path)
    if property != isCreatable:
        _logAssertionException("IsCreatable", path, "is creatable." if property else "is not creatable.")
        return False
    else:
        return True


def assertPathIsWritable(path: Path, isWritable = True) -> bool:
    property = canWrite(path)
    if property != isWritable:
        _logAssertionException("IsWritable", path, "is writable." if property else "is not writable.")
        return False
    else:
        return True


def assertPathIsDeletable(path: Path, isDeletable = True) -> bool:
    property = canDelete(path)
    if property != isDeletable:
        _logAssertionException("IsDeletable", path, "is deletable." if property else "is not deletable.")
        return False
    else:
        return True


def assertPathIsReadable(path: Path, isReadable = True) -> bool:
    property = canRead(path)
    if property != isReadable:
        _logAssertionException("IsReadable", path, "is readable." if property else "is not readable.")
        return False
    else:
        return True


def assertPathIsSavable(path: Path, isSavable = True) -> bool:
    property = canWrite(path) or canModify(path)
    if property != isSavable:
        _logAssertionException("IsSavable", path, "is savable." if property else "is not savable.")
        return False
    else:
        return True


def assertPathIsModifiable(path: Path, isModifiable = True) -> bool:
    property = canModify(path)
    if property != isModifiable:
        _logAssertionException("IsModifiable", path, "is modifiable." if property else "is not modifiable.")
        return False
    else:
        return True


def _logAssertionException(assertionNameSuffix: str, path: Path, message: str) -> None:
    logger.append(AttributeError("ubot_data#assertPath{}\r\nPath '{}' {}\r\n"
                                 .format(assertionNameSuffix, path, message)))


def canRead(path: Path) -> bool:
    return path.isExist and path.isFile


def canCreate(path: Path) -> bool:
    if path.isWritable is None:
        path.isWritable = _checkPermission(path.path, "write_rights")

    return path.isWritable and not path.isExist


def canWrite(path: Path) -> bool:
    if path.isWritable is None:
        path.isWritable = _checkPermission(path.path, "write_rights")

    return path.isWritable


def canDelete(path: Path) -> bool:
    if path.isDeletable is None:
        path.isDeletable = _checkPermission(path.path, "delete_rights")

    return path.isDeletable and path.isExist


def canModify(path: Path) -> bool:
    if path.isModifiable is None:
        path.isModifiable = _checkPermission(path.path, "modify_rights")

    return path.isModifiable and path.isExist


def _checkPermission(path: str, nameOfPrefixSet: str) -> bool:
    for prefix in config.get("data", nameOfPrefixSet):
        if path.find(prefix) == 0 and len(prefix) < len(path):
            return True
    return False


def doesFolderExist(path: Path) -> bool:
    return path.isExist and path.isFolder


def doesFileExist(path: Path) -> bool:
    return path.isExist and path.isFile


def doesTxtFileExist(path: Path) -> bool:
    return path.isExist and path.isFile and path.isTxt


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
        logger.append(AttributeError("ubot_data#getFileList\r\nPath '{}' doesn't exist.\r\n".format(path)))
        return ()


def getFile(path: Path, isJson: bool = None) -> tuple:
    if assertPathIsReadable(path):
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
        logger.append(AttributeError("ubot_data#getFile\r\nCan not open '{}' because of breach of preconditions.\r\n"
                                     .format(path)))
        return ()


def __loadsJsonSoftly(line: str) -> object:
    try:
        return ujson.loads(line)
    except:
        return line


def getLineCountOfFile(path: Path) -> int:
    if assertPathIsReadable(path):
        return sum(1 for _ in open(path.path))
    else:
        return 0


def getEntityCountOfFolder(path: Path) -> int:
    if assertPathIsFolder(path):
        return len(uos.listdir(path))
    else:
        return 0


def printFile(path: Path, isJson: bool = None) -> tuple:    # Exactly same as getFile... TODO: Make it elegant.
    if assertPathIsReadable(path):
        try:
            likelyJson = isJson is True or isJson is not False and getLineCountOfFile(path) == 1
            with open(path.path, "r") as file:
                if likelyJson:
                    for line in file:
                        print(__loadsJsonSoftly(line), end = "")
                else:
                    for line in file:
                        print(line, end = "")
        except Exception as e:
            logger.append(e)
            logger.append(AttributeError("ubot_data#printFile\r\nCan not process '{}'.\r\n".format(path)))
            return ()
    else:
        logger.append(AttributeError("ubot_data#printFile\r\nCan not open '{}' because of breach of preconditions.\r\n"
                                     .format(path)))
        return ()


def saveFile(path: Path, lines: object, isRecursive: bool = False) -> bool:
    if assertPathIsSavable(path):
        written = 0
        try:
            if isRecursive:
                createFoldersAlongPath(createPathFrom(path.array[:-1]))

            with open(path.path, "w") as file:
                if isinstance(lines, str):
                    written += _writeOut(file, lines, False)
                elif isinstance(lines, tuple) or isinstance(lines, list):
                    for line in lines:
                        written += _writeOut(file, line, False)
                elif isinstance(lines, dict):
                    written += _writeOut(file, lines, True)
                else:
                    return False

            refresh(path)
            return written == 0
        except Exception as e:
            logger.append(e)
            logger.append(AttributeError("ubot_data#saveFile\r\nCan not process '{}'.\r\n".format(path)))
            return False
    else:
        logger.append(AttributeError("ubot_data#saveFile\r\nCan not save '{}' because of breach of preconditions.\r\n"
                                     .format(path)))
        return False


def _writeOut(file: object, line: object, isJson: bool = False) -> int:
    toWrite = "{}\r\n".format(ujson.dumps(line) if isJson else line)
    return file.write(toWrite) - len(toWrite)


def delete(path: Path) -> bool:
    if assertPathIsDeletable(path):
        try:
            if path.isFile:
                uos.remove(path.path)
            elif path.isFolder:
                uos.rmdir(path.path)
            else:
                return False

            _makePathNonExistent(path)
            return True
        except Exception as e:
            logger.append(e)
            logger.append(AttributeError("ubot_data#delete\r\nCan not delete '{}'.\r\n".format(path)))
            return False
    else:
        logger.append(AttributeError("ubot_data#delete\r\nCan not delete '{}' because of breach of preconditions. \r\n"
                                     .format(path)))
        return False


################################
## Other data related helpers

def dumpException(exception: Exception) -> str:
    return "{} {}".format(exception.__class__, exception.args)


def isStringWithContent(string: str) -> bool:
    return isinstance(string, str) and string != ""


def extractIntTupleFromString(tupleString: str, limit: int = -1) -> tuple:
    result  = []
    current = 0
    unsaved = False
    tupleString = str(tupleString)

    for char in tupleString:
        if char.isdigit():
            current *= 10
            current += int(char)
            unsaved = True
        elif unsaved:
            result.append(current)
            current = 0
            unsaved = False
            if len(result) == limit:
                break

    if unsaved:
        result.append(current)

    return tuple(result)


def extractCharTupleFromString(tupleString: str, enabledCharsSet: set, limit: int = -1) -> tuple:
    result = []
    tupleString = str(tupleString)

    for char in tupleString:
        if char in enabledCharsSet:
            result.append(char)
            if len(result) == limit:
                break

    return tuple(result)


################################
## REST/JSON related methods

def preparePathIfSpecial(path: Path) -> None:
    array = list(path.array)
    size  = path.size
    args  = list(path.args)

    if 0 < size:
        if array[0] == "raw":                                             # TODO: real raw instead of the alias behavior
            args = ["raw"]
            del array[0]
            size -= 1

        if 1 < size:
            if array[0] == "command":
                args = ["command" if _ticketLevel < len(array) else "quick"] + array[1:]
                del array[1:]
                size = 1

            if 2 < size:
                if array[0]  == "program":
                    array[2] = turtle.normalizeProgramTitleFromFolder(array[2], array[1])
                elif array[0] == "log":
                    array[2] = logger.normalizeLogTitle(array[2])
                elif not array[2].endswith(".txt"):
                    array[2] = "{}.txt".format(array[2])

                if 3 < size:
                    args = [array[0]] + array[3:]
                    del array[3:]

        path.path  = "/{}".format("/".join(array))
        path.array = tuple(array)
        path.size  = len(array)
        path.args  = tuple(args)
        refresh(path)


def createRestReplyOf(*pathEnumeration: str) -> tuple:
    return createRestReplyFrom(pathEnumeration)


def createRestReplyFrom(pathArray: tuple) -> tuple:
    try:
        return createRestReply(createPathFrom(pathArray))
    except Exception as e:
        logger.append(e)
        return "403 Forbidden", \
               "Request: Get JSON reply of path array '{}'. Cause: It is not acceptable.".format(pathArray), {}


def createRestReply(path: Path) -> tuple:
    length = path.size

    if length < 2:
        return _createJsonFolderInstance(path)
    elif length == 2:
        return _createJsonSubFolderInstance(path)
    elif length == 3:
        return _createJsonFileInstance(path)
    else:
        return "403 Forbidden", "Request: Get JSON reply of path array '{}'. Cause: It is too long.".format(path), {}


def _createJsonFolderInstance(path: Path) -> tuple:
    name   = str(path)
    isRoot = path.size == 0
    job    = "Request: Get the folder '{}'.".format(name)

    if assertPathIsFolder(path):
        subFolders    = getFoldersOf(path)
        folderLink    = "{}{}".format(_hostLink, name)
        folderRawLink = "{}{}".format(_rawLink,  name)

        return "200 OK", job, {
            "name": "/" if isRoot else path.array[0],
            "type": "folder",
            "href": folderLink,
            "raw":  folderRawLink,

            "parent": {} if isRoot else {"name": "/",
                                         "type": "folder",
                                         "href": "{}/".format(_hostLink),
                                         "raw":  "{}/".format(_rawLink)},

            "children": [{"name": subFolder,
                          "type": "folder",
                          "href": "{}{}/".format(folderLink, subFolder),
                          "raw":  "{}{}/".format(folderRawLink, subFolder)} for subFolder in subFolders]}
    else:
        return "404 Not Found", job + " Cause: The folder doesn't exist.", {}


def _createJsonSubFolderInstance(path: Path) -> tuple:
    name = str(path)
    job  = "Request: Get the folder '{}'.".format(name)

    if assertPathIsFolder(path):
        files         = getFileNameList(path, "txt")                 #! Burnt-in txt suffix: filtered by it, but chopped
        array         = path.array
        parentName    = array[0]
        folderLink    = "{}{}".format(_hostLink, name)
        folderRawLink = "{}{}".format(_rawLink,  name)

        return "200 OK", job, {
            "name": array[1],
            "type": "folder",
            "href": folderLink,
            "raw":  folderRawLink,

            "parent": {"name": parentName,
                       "type": "folder",
                       "href": "{}/{}/".format(_hostLink, parentName),
                       "raw":  "{}/{}/".format(_rawLink,  parentName)},

            "children": [{"name": file,
                          "type": "file",
                          "href": "{}{}".format(folderLink, file),
                          "raw":  "{}{}.txt".format(folderRawLink, file)} for file in files]}     #! Burnt-in txt suffix
    else:
        return "404 Not Found", job + " Cause: The folder does not exist.", {}


def _createJsonFileInstance(path: Path) -> tuple:
    name   = str(path)
    array  = path.array
    parent = array[1]

    job = "Request: Get the file '{}'.".format(name)

    if assertPathIsFile(path):
        isJson = True if array[0] in config.get("data", "json_folders") else None
        return "200 OK", job, {
            "name": array[2],
            "type": "file",
            "href": "{}{}".format(_hostLink, name[:-4] if name.endswith(".txt") else name),
            "raw":  "{}{}".format(_rawLink,  name),
            "parent": {
                "name": parent,
                "type": "folder",
                "href": "{}/{}/".format(_hostLink, parent),
                "raw":  "{}/{}/".format(_rawLink,  parent)
            },
            "children": [],
            "value": getFile(path, isJson)}
    else:
        return "404 Not Found", job + " Cause: The file does not exist.", {}


# Preventing circular dependency

import ubot_config as config
import ubot_turtle as turtle

_hostLink = "http://{}".format(config.get("ap", "ip"))
_rawLink  = "{}/raw".format(_hostLink)

_ticketLevel = config.get("data", "ticket_level")
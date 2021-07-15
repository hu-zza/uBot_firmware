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
        self.isWritable  = None
        self.isDeletable = None
        self.isModifiable = None

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
            typeInt = uos.stat(pathString)[0]

            if typeInt == 0x4000:
                path.isFolder = True

                if not pathString.endswith("/"):
                    pathString = "{}/".format(pathString)
            elif typeInt == 0x8000:
                path.isFile = True
                path.isTxt = pathString.endswith(".txt")
            else:
                raise AttributeError("ubot_data#_initializePath\r\nPath '{}' should represent a folder or a file.\r\n"
                                     .format(path))
        elif _doesExist("{}.txt".format(pathString)):                                             #! Burnt-in txt suffix
            pathString = "{}.txt".format(pathString)

            if uos.stat(pathString)[0] != 0x8000:
                raise AttributeError("ubot_data#_initializePath\r\nPath '{}' should represent a file.\r\n".format(path))

            path.isExist = True
            path.isFile  = True
            path.isTxt   = True

        array = tuple(item for item in pathString.split("/") if item != "")
        path.path  = pathString
        path.array = array
        path.size  = len(array)
        _refreshPathDescription(path)


    except Exception as e:
        logger.append(e)
        logger.append(AttributeError("ubot_data#_initializePath\r\nCan not initialize Path object with path '{}'.\r\n"
                                     .format(path)))
        _invalidatePath(path)


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
    path.size  = 0
    path.description = "[invalid]"
    _deletePathFlags(path)


def _makePathNonExistent(path: Path) -> None:
    _deletePathFlags(path)
    _refreshPathDescription(path)


def _deletePathFlags(path: Path) -> None:
    path.isExist  = False
    path.isFolder = False
    path.isFile   = False
    path.isTxt    = False
    path.isWritable   = False
    path.isDeletable  = False
    path.isModifiable = False


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
        path = _sanitizePath(path)
        return "/" if path == "" else path


def _sanitizePath(path: str) -> str:
    path = path.strip(".")
    path = _replaceWhileFound(path, "/../", "/")
    path = _replaceWhileFound(path, "/./", "/")
    return _replaceWhileFound(path, "//", "/")


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

INVALID_PATH = Path("/")
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


def createFoldersAlongPath(path: Path) -> None:
    if canWrite(path):
        pathArray = path.array
        elements = []
        for i in range(len(pathArray) - (1 if path.isFile else 0)):
            elements.append(pathArray[i])
            path = "/{}".format("/".join(elements))
            if not _doesExist(path):
                createFolder(createPath(elements))


def assertPathIsExist(path: Path, isExist = True) -> bool:
    if path.isExist != isExist:
        _logAssertionException("IsExist", path, "exist." if path.isExist else "does not exist.")
        return False


def assertPathIsFolder(path: Path, isFolder = True) -> bool:
    if path.isFolder != isFolder:
        _logAssertionException("IsFolder", path, "represents a folder." if path.isFolder else "does not represent a folder.")
        return False


def assertPathIsFile(path: Path, isFile = True) -> bool:
    if path.isFile != isFile:
        _logAssertionException("IsFile", path, "represents a file." if path.isFile else "does not represent a file.")
        return False


def assertPathIsTxt(path: Path, isTxt = True) -> bool:
    if path.isTxt != isTxt:
        _logAssertionException("IsTxt", path, "has '.txt' suffix." if path.isTxt else "has no '.txt' suffix.")
        return False


def assertPathIsCreatable(path: Path, isCreatable = True) -> bool:
    property = canCreate(path)
    if property != isCreatable:
        _logAssertionException("IsCreatable", path, "is creatable." if property else "is not creatable.")
        return False


def assertPathIsWritable(path: Path, isWritable = True) -> bool:
    property = canWrite(path)
    if property != isWritable:
        _logAssertionException("IsWritable", path, "is writable." if property else "is not writable.")
        return False


def assertPathIsDeletable(path: Path, isDeletable = True) -> bool:
    property = canDelete(path)
    if property != isDeletable:
        _logAssertionException("IsDeletable", path, "is deletable." if property else "is not deletable.")
        return False


def assertPathIsReadable(path: Path, isReadable = True) -> bool:
    property = canRead(path)
    if property != isReadable:
        _logAssertionException("IsReadable", path, "is readable." if property else "is not readable.")
        return False


def assertPathIsSavable(path: Path, isSavable = True) -> bool:
    property = canWrite(path) or canModify(path)
    if property != isSavable:
        _logAssertionException("IsSavable", path, "is savable." if property else "is not savable.")
        return False


def assertPathIsModifiable(path: Path, isModifiable = True) -> bool:
    property = canModify(path)
    if property != isModifiable:
        _logAssertionException("IsModifiable", path, "is modifiable." if property else "is not modifiable.")
        return False


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
        logger.append(AttributeError("ubot_data#getFilesOfPath\r\nPath '{}' doesn't exist.\r\n".format(path)))
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


def saveFile(path: Path, lines: object, isRecursive: bool = False) -> bool:
    if assertPathIsSavable(path):
        written = 0
        try:
            if isRecursive:
                createFoldersAlongPath(path)

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

            path.isExist = True
            _refreshPathDescription(path)
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

def dumpException(exception):
    return "{} {}".format(exception.__class__, exception.args)


################################
## REST/JSON related methods

_hostLink = "http://{}".format(config.get("ap", "ip"))
_rawLink  = "{}/raw".format(_hostLink)


def createRestReplyOf(*pathArray: str) -> tuple:
    try:
        return createRestReply(createPath(pathArray))
    except Exception as e:
        logger.append(e)
        return "403 Forbidden", "Request: Get JSON reply of path array '{}'. Cause: It is not acceptable."\
            .format(pathArray), {}


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
    isRoot = path.size == 1
    job    = "Request: Get the folder '{}'.".format(name)

    if assertPathIsFolder(path):
        subFolders    = getFoldersOf(path)
        folderLink    = "{}{}".format(_hostLink, name)
        folderRawLink = "{}{}".format(_rawLink,  name)

        return "200 OK", job, {
            "name": "root" if isRoot else path.array[0],
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
            "href": "{}{}".format(_hostLink, name[:name.rindex(".")]),
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

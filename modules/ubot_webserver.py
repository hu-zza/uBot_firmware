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

import ujson, uos, uselect, usocket

from machine import Timer

import ubot_config   as config
import ubot_data     as data
import ubot_logger   as logger
import ubot_motor    as motor
import ubot_template as template
import ubot_future   as future
import ubot_turtle   as turtle


_connection = 0
_connected  = False
_headerSent = False
_isCommand  = False
_quickPress = False
_quickDrive = False

_started = False
_timeout = config.get("web_server", "timeout")
_timer  = Timer(-1)
_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
_poller = uselect.poll()

_socket.bind(("", config.get("web_server", "port")))
_socket.listen(config.get("web_server", "backlog"))
_poller.register(_socket, uselect.POLLIN)

_incoming = ""
_request = {
    "address": None,
    "method": "",
    "rawPath": "",
    "path": data.INVALID_PATH,
    "contentLength": 0,
    "contentType": "",
    "accept": "",
    "body": "",
    "processing": "UNDEFINED"
}

_server = "uBot_firmware/{}".format(".".join([str(i) for i in config.get("system", "firmware")]))
_apiLink = config.get("constant", "api_link")
_response = {
        "meta": {
            "request": _request,
            "response": {
                "code": 0,
                "status": "",
                "message": ""
            }},
        "result": {}
}

_denyHtml = not config.get("web_server", "html_enabled")
_denyJson = not config.get("web_server", "json_enabled")

_open_quick   = config.get("web_server", "open_quick")
_open_command = config.get("web_server", "open_command")

_log_event    = config.get("web_server", "log_event")
_log_request  = config.get("web_server", "log_request")
_log_response = config.get("web_server", "log_response")
_log__reply   = config.get("web_server", "log__reply")

allowedMethods     = {"GET", "POST", "PUT", "DELETE"}
allowedHtmlMethods = {"GET", "POST"}
allowedJsonMethods = {"GET", "POST", "PUT", "DELETE"}
_hasJsonBody       = {"POST", "PUT"}

_srv = tuple(name for name in uos.listdir("/srv") if not name.endswith("_meta"))

tmp = ([], [])
for name in _srv:
    tmp[name.startswith("_panel_")].append("/{}".format(name[7:-5] if name.startswith("_panel_") else name))

_files  = tuple(tmp[0])
_panels = tuple(tmp[1])
del tmp

_headerEnd = ("        <title>{}</title>\r\n"
              "    </head>\r\n"
              "    <body class='{}'>\r\n")

_bodyEnd   = ("    </body>\r\n"
              "</html>\r\n\r\n")


_simpleEnd = ("        <title>μBot | {title}</title>\r\n"
              "    </head>\r\n"
              "    <body>\r\n"
              "        <h1>{title}</h1>\r\n"
              "        {body}\r\n"
              "    </body>\r\n"
              "</html>\r\n\r\n")


def _getFileMetadata(fileName: str) -> tuple:
    try:
        with open("/srv/{}_meta".format(fileName.strip("/")), "r") as file:
            return tuple(line.strip() for line in file)
    except Exception as e:
        logger.append("ubot_webserver#_getFileMetadata\r\nFile '{}' can not found.".format(fileName))
        logger.append(e)
        return "0", "text/html; charset=UTF-8"

_headLength = int(_getFileMetadata("_panel___head.html")[0])


################################
## CONFIG

def _unavailableJsonSender(*args) -> None:
    raise Exception("ubot_webserver#_unavailableJsonSender\r\nThe '_jsonSender' is unavailable, processing had stopped.")

_jsonSender = _unavailableJsonSender

def setJsonSender(method) -> None:
    global _jsonSender
    _jsonSender = method


def setJsonCallback(method: str, jsonFunction) -> None:
    global _jsonFunctionMap

    if isAllowed(method, allowedJsonMethods):
        _jsonFunctionMap[method] = jsonFunction


################################
## PUBLIC METHODS

def start() -> None:
    global _started

    if not _started and config.get("web_server", "active"):
        _timer.init(period = config.get("web_server", "period"), mode = Timer.PERIODIC, callback = _poll)
        _started = True


def stop() -> None:
    global _started

    if _started:
        _timer.deinit()
        _started = False


def isAllowed(methodName: str, methodSet: set = None) -> bool:
    if methodSet is None:
        methodSet = allowedMethods

    return methodName in methodSet


def isProcessing() -> bool:
    return _connected


################################
## PRIVATE, HELPER METHODS

def _logRequest() -> None:
    if _log_event:
        logger.append("{}\t{}".format(_request.get("method"), _request.get("rawPath")))

    if _log_request:
        logger.append(_request)


def _logResponse(response: dict) -> None:
    if _log_event:
        metaResponse = response.get("meta").get("response")
        logger.append("{}\t{}".format(metaResponse.get("status").replace(" ", "\t", 1), metaResponse.get("message")))

    if _log_response:
        logger.append(response)


def _poll(timer: Timer) -> None:
    global _connected

    try:
        if _canWork():
            _connected = True
            if _canWork():
                result = _poller.poll(_timeout)

                if result:
                    _clearOldRequestData()
                    _processIncoming(result[0][0])
            else:
                _connected = False
    except Exception as e:
        logger.append(e)
    finally:
        _connected = False


def _canWork() -> bool:
    return not future.isProcessing() and \
           not motor.isProcessing()


def _clearOldRequestData() -> None:
    global _request

    _request["method"] = ""
    _request["rawPath"] = ""
    _request["path"] = data.INVALID_PATH
    _request["contentLength"] = 0
    _request["contentType"] = ""
    _request["accept"] = ""
    _request["body"] = ""
    _request["processing"] = "UNDEFINED"


def _processIncoming(incoming: object) -> None:
    global _incoming, _connection, _headerSent, _isCommand, _quickPress, _quickDrive
    _incoming = incoming

    try:
        _readIncoming()

        if _quickPress:
            _processWithPriorityMethod(_processPressQuickly)
        elif _quickDrive:
            _processWithPriorityMethod(_processDriveQuickly)
        else:
            _chooseProcessingMethod()
            _createPath()
            _processBody()

    except Exception as e:
        logger.append(e)
        _reply("400 Bad Request", "The server could not understand the request due to invalid syntax.")
    finally:
        _headerSent = False
        _isCommand  = False
        _quickPress = False
        _quickDrive = False
        _connection.close()


def _readIncoming() -> None:
    global _connection, _request

    _connection, _request["address"] = _incoming.accept()
    _socketFile = _connection.makefile("rwb", 0)

    while True:
        line = _socketFile.readline()

        if not line:
            break
        elif line == b"\r\n":
            if 0 < _request.get("contentLength"):
                _request["body"] = str(_socketFile.read(_request["contentLength"]), "utf-8")
            break

        _processHeaderLine(str(line, "utf-8"))


def _processHeaderLine(line: str) -> None:
    global _request, _isCommand, _quickPress, _quickDrive

    line = line.lower()

    if _request.get("method") == "":
        firstSpace = line.find(" ")
        pathEnd = line.find(" http")

        _request["method"]  = line[0:firstSpace].upper()
        rawPath = line[firstSpace + 1:pathEnd]
        _request["rawPath"] = rawPath

        length = len(rawPath)
        if 8 < length:
            _isCommand = rawPath.startswith("/command/")
            if length < 19:
                _quickPress = rawPath.startswith("/command/press_")
                _quickDrive = rawPath.startswith("/command/drive_") and length < 17

    if 0 <= line.find("content-length:"):
        lengthString = line[15:].strip()
        _request["contentLength"] = int(lengthString) if lengthString.isdigit() else 0

    if 0 <= line.find("content-type:"):
        _request["contentType"] = line[13:].strip()

    if 0 <= line.find("accept:"):
        _request["accept"] = line[7:].strip()


def _processWithPriorityMethod(function) -> None:
    if _open_quick:
        function()
    else:
        _chooseProcessingMethod()
        if _request.get("processing") == "JSON":
            function()
        else:
            _createPath()
            _processBody()


def _processPressQuickly() -> None:
    global _headerSent
    _connection.write("HTTP/1.1 202 Accepted\r\nContent-Type: application/json; charset=UTF-8\r\nContent-Length: 131\r\n"
                      "Connection: close\r\n\r\n{\"meta\": {\"response\": {\"code\": 202, \"status\": \"202 Accepted\", "
                      "\"message\": \"[DONE] [QUICK] Request: Press a button.\"}}, \"result\": {}}")
    _headerSent = True
    turtle.press(int(_request.get("rawPath").rstrip("/")[15:]))


def _processDriveQuickly() -> None:
    global _headerSent
    _connection.write("HTTP/1.1 202 Accepted\r\nContent-Type: application/json; charset=UTF-8\r\nContent-Length: 132\r\n"
                      "Connection: close\r\n\r\n{\"meta\": {\"response\": {\"code\": 202, \"status\": \"202 Accepted\", "
                      "\"message\": \"[DONE] [QUICK] Request: Drive the μBot.\"}}, \"result\": {}}")
    _headerSent = True
    turtle.skipSignal(1, 1)
    turtle.move(ord(_request.get("rawPath")[15]) - 32)  # Upperchar


def _chooseProcessingMethod() -> None:
    global _request

    accept = _request.get("accept")
    contentType = _request.get("contentType")
    union = accept + contentType

    if _request.get("rawPath") in _files:
        _request["processing"] = "FILE"
    elif "text/html" in union:
        _request["processing"] = "HTML"
    elif "application/json" in union or "*/*" in accept:
        _request["processing"] = "JSON"
    else:
        _request["processing"] = "UNDEFINED"


def _createPath() -> None:
    _request["path"] = data.createPath(_request.get("rawPath"))
    data.preparePathIfSpecial(_request.get("path"))


def _processBody() -> None:
    _logRequest()

    if isAllowed(_request.get("method")):
        try:
            _processingMap.setdefault(_request.get("processing"), _unsupportedTypeHandler)()
        except Exception as e:
            logger.append(e)
            _reply("500 Internal Server Error", "A fatal error occurred during processing the {} {} request."
                   .format(_request.get("processing"), _request.get("method")), data.dumpException(e))
    else:
        _reply("405 Method Not Allowed",
               "The following HTTP request methods are allowed: {}.".format(", ".join(allowedMethods)))


def _unsupportedTypeHandler() -> None:
    _reply("415 Unsupported Media Type", "'Content-Type' / 'Accept' should be 'text/html' or 'application/json'.")


def _processHtmlQuery() -> None:
    if _denyHtml:
        result = _unavailableSupplierFunction()
        _reply(result[0], result[1])
    elif isAllowed(_request.get("method"), allowedHtmlMethods):
        if _isCommand and _open_command:
            _processJsonQuery()
        else:
            _htmlFunctionMap[_request.get("method")]()
    else:
        _reply("405 Method Not Allowed", "The following HTTP request methods are allowed with text/html "
                                         "content type: {}.".format(", ".join(allowedHtmlMethods)))


def _unavailableSupplierFunction(*args) -> tuple:
    return "503 Service Unavailable", "This service is not yet available.", {}


def _processHtmlGetQuery() -> None:
    path = _resolveLinks(_request.get("rawPath"))

    if path in _panels and not path.startswith("__"):
        _replyWithHtmlPanel(path)
    elif path in template.title:
        _replyWithHtmlTemplate(path)
    else:
        path = _request.get("path")

        if "raw" in path.args:
            _replyWithHtmlRaw(path)
        else:
            _reply("404 Not Found", "Request: Get the page / file '{}'.".format(path))

_links = {
    "/":             "/go",
    "/professional": "/pro",
    "/turtlecode":   "/turtle"
}

def _resolveLinks(path: str) -> str:
    if path in _links:
        return _links.get(path)
    else:
        return path


def _replyWithHtmlPanel(path: str) -> None:
    path = "_panel_{}.html".format(path[1:])

    _sendHeader("200 OK", _headLength + int(_getFileMetadata(path)[0]))
    _sendPanel("__head.html")
    _sendPanel(path)
    _logResponse(_getBasicReplyMap("200 OK", "Request: Get the page '{}'.".format(path)))


def _sendPanel(panelFilename: str) -> None:
    try:
        if not panelFilename.startswith("_panel_"):
            panelFilename = "_panel_{}".format(panelFilename)

        with open("/srv/{}".format(panelFilename)) as file:
            for line in file:
                _connection.write(line)
    except Exception as e:
        logger.append("ubot_webserver#_sendPanel\r\nPanel '{}' can not found.".format(panelFilename))
        logger.append(e)


def _replyWithHtmlTemplate(path: str) -> None:
    _sendHeader()
    _sendPanel("__head.html")
    _connection.write(_headerEnd.format(template.title.get(path), "general"))

    for part in template.parts.get(path):
        _connection.write(part())

    if path.startswith("/debug"):
        _includeDebugDashboard()

    _connection.write(_bodyEnd)
    _logResponse(_getBasicReplyMap("200 OK", "Request: Get the page '{}'.".format(path)))


def _includeDebugDashboard() -> None:
    ip = config.get("ap", "ip")
    _connection.write("        <h3>Information panels</h3>\r\n")
    for panelTitle in sorted(template.debugPanels.keys()):
        _connection.write("            <a href='http://{0}{1}' target='_blank'>{2}</a><br>\r\n"
                          .format(ip, template.debugPanels.get(panelTitle), panelTitle))
    _connection.write("        <br><br><hr><hr>\r\n")
    _connection.write("        <h3>Log files</h3>\r\n")
    _host = "http://{}/raw".format(ip)
    _filenameBase = "/log/{{}}/{:010d}.txt".format(config.get("system", "power_ons"))
    _fallbackBase = "/log/{}/0000000000.txt"
    _connection.write("            <table class='data'>\r\n")
    for category in logger.getLogCategories():
        _connection.write("                <tr><td><strong>{}:</strong></td>".format(category))

        _currentLog = _filenameBase.format(category)
        _fallbackLog = _fallbackBase.format(category)

        _connection.write("<td><a href='{}{}' target='_blank'>current ({} B)</a></td>"
                          .format(_host, _currentLog, uos.stat(_currentLog)[6]))

        _connection.write("<td><a href='{}{}' target='_blank'>fallback ({} B)</a></td></tr>\r\n"
                          .format(_host, _fallbackLog, uos.stat(_fallbackLog)[6]))
    _connection.write("            </table>\r\n")


def _replyWithHtmlRaw(path: data.Path) -> None:
    _sendHeader()
    _sendPanel("__head.html")
    _connection.write(_headerEnd.format("μBot Raw &nbsp;| &nbsp; {}".format(path), "raw"))
    _sendRaw(path.path)
    _connection.write(_bodyEnd)
    _logResponse(_getBasicReplyMap("200 OK", "Request: Get the folder / file '{}'.".format(path)))


def _sendHeader(status: str = "200 OK", length: int = None, allow: bool = None) -> None:
    global _headerSent

    if not _headerSent:
        contentType = "text/html; charset=UTF-8"
        allowSet = ", ".join(allowedHtmlMethods)
        cache = "no-cache"

        if _request.get("processing") == "JSON":
            contentType = "application/json; charset=UTF-8"
            allowSet = ", ".join(allowedJsonMethods)
            cache = "no-cache"
        if _request.get("processing") == "FILE":
            length, contentType = _getFileMetadata(_request.get("rawPath"))
            allowSet = "GET"
            cache = "public, max-age=31536000, immutable"

        contentLength = "" if length is None else "Content-Length: {}\r\n".format(length)

        if allow is None:
            allow = allowSet

        _connection.write("HTTP/1.1 {}\r\nContent-Type: {}\r\n{}Content-Encoding: identity\r\n"
                          "Transfer-Encoding: identity\r\nServer: {}\r\nAllow: {}\r\nCache-Control: {}\r\n"
                          "Connection: close\r\n\r\n".format(status, contentType, contentLength, _server, allow, cache))
        _headerSent = True


def _processHtmlPostQuery() -> None:
    _reply("501 Not Implemented", "This service is not implemented yet.")


def _processJsonQuery() -> None:
    if _denyJson:
        result = _unavailableSupplierFunction()
        _reply(result[0], result[1], result[2])
    elif isAllowed(_request.get("method"), allowedJsonMethods):
        _startJsonProcessing()
    else:
        methods = ", ".join(allowedJsonMethods)
        _reply("405 Method Not Allowed", "The following HTTP request methods are allowed with application/json "
                                         "content type: {}.".format(methods))


def _startJsonProcessing() -> None:
    _jsonSender(_request.get("path"), _request.get("body"))
    result = _jsonFunctionMap[_request.get("method")]()
    _reply(result[0], result[1], result[2])


def _processFileQuery() -> None:
    path = _request.get("rawPath")
    _reply("200 OK", "Request: Get the file '{}'.".format(path), path)


def _reply(responseStatus: str, message: str, result: object = None) -> None:
    """ Try to reply with a text/html or application/json
        if the connection is alive, then closes it. """
    try:
        processing = _request.get("processing")
        if processing == "FILE":
            reply  = "/srv/{}".format(result)
            length = 0
            _updateReply(responseStatus, message, {})
        else:
            reply  = _replyMap.setdefault(_request.get("processing"), _createHtmlReply)(responseStatus, message, result)
            length = len(reply) + _headLength

        if _connected:
            _sendHeader(responseStatus, length)

            if processing == "FILE":
                with open(reply, "rb") as file:
                    for line in file:
                        _connection.sendall(line)
            else:
                _sendPanel("__head.html")
                _connection.write(reply)

        _logResponse(_response)
    except Exception as e:
        if _log__reply:
            logger.append(e)


def _createHtmlReply(responseStatus: str, message: str, result: dict = None) -> str:
    _updateReply(responseStatus, message, result)

    if responseStatus == "404 Not Found":
        message = _getHelperLinks()

    return _simpleEnd.format(title = responseStatus, body = message)


def _createJsonReply(responseStatus: str, message: str, result: dict = None) -> str:
    _updateReply(responseStatus, message, result)
    return ujson.dumps(_response)


def _updateReply(responseStatus: str, message: str, result: dict = None) -> None:
    global _response
    _response = _getBasicReplyMap(responseStatus, message, result)


def _getBasicReplyMap(responseStatus: str, message: str, result = None) -> dict:
    statusCode = int(responseStatus[:3])

    if not isinstance(result, dict):
        result = {} if result is None else {"value": result}

    replyMap = {
        "meta": {
            "request": _request,
            "response": {
                "code": statusCode,
                "status": responseStatus,
                "message": _getMessageWithFlags(message, statusCode)
            }},
        "result": result
    }
    replyMap["meta"]["request"]["path"] = str(_request.get("path"))
    return replyMap


def _getMessageWithFlags(message: str, statusCode: int) -> str:
    flags = "{}"

    if 100 <= statusCode < 200:
        flags = "[INFO] {}"
    elif 200 <= statusCode < 300:
        flags = "[DONE] {}"
    elif 300 <= statusCode < 400:
        flags = "[LINK] {}"
    elif 400 <= statusCode < 600:
        flags = "[FAIL] {{}}  // More info: {}".format(_apiLink)

    return flags.format(message)


def _getHelperLinks() -> str:
    helperLinks = "        <ul class='links'>\r\n"
    helperLinks += "            <li>Sitemap</li>\r\n"
    for key in sorted(template.title.keys()):
        if key == "/" or key[1] != "_":
            helperLinks += "            <li><a href='{key}'>{title}</a><br><small>{host}{key}</small></li>\r\n".format(
                host = config.get("ap", "ip"), key = key, title = template.title.get(key)
            )
    helperLinks += "        </ul>\r\n"
    return helperLinks


def _sendRaw(path: str) -> None:
    """ If the path links to a dir, sends a linked list, otherwise tries to send the content of the target entity. """
    try:
        if path[-1] == "/":  # Folder -> A practical, cosy, and a bit dirty constraint for simple relative URL handling.
            _connection.write(("        <table>\r\n"
                               "            <thead>\r\n"
                               "                <tr><th scope='col'>Filename</th><th scope='col'>File size</th></tr>\r\n"
                               "            </thead>\r\n"
                               "            <tbody>\r\n"
                               "                <tr><td><a href='..'>..</a></td><td></td></tr>"))

            try:
                for filename in uos.listdir(path):
                    _connection.write("                <tr>")

                    try:
                        stat = uos.stat("{}{}".format(path, filename))

                        if stat[0] == 0x04000:  # Folder
                            _connection.write(
                                "<td><a href='{filename}/'>{filename}/</a></td><td>-</td>".format(filename = filename))

                        elif stat[0] == 0x08000:  # File
                            _connection.write(
                                "<td><a href='{filename}'>{filename}</a></td><td>{fileSize:,} B</td>".format(
                                    filename = filename, fileSize = stat[6]))

                        else:
                            _connection.write("<td colspan='2'>{}</td>".format(filename))

                    except Exception:
                        _connection.write("<td class='info' colspan='2'>This entity cannot be listed.</td>")
                    _connection.write("</tr>\r\n")

                if len(uos.listdir(path)) == 0:
                    _connection.write(
                        "                <tr><td class='info' colspan='2'>This directory is empty.</td></tr>\r\n")

            except Exception:
                _connection.write("<td class='info' colspan='2'>[Errno 2] ENOENT : No such directory.</td>")

            _connection.write(("            </tbody>\r\n"
                               "        </table>\r\n"))
        else:
            _connection.write("        <pre>\r\n")
            try:
                with open(path) as file:
                    for line in file:
                        _connection.write(line)
            except Exception:
                _connection.write("[Errno 2] ENOENT : No such file.\r\n")
            _connection.write("        </pre>\r\n")
    except Exception:
        _connection.write("[Errno 2] ENOENT : No such file or directory.\r\n")


################################
## MAPPINGS

_htmlFunctionMap = {
    "GET"    : _processHtmlGetQuery,
    "POST"   : _processHtmlPostQuery
}

_jsonFunctionMap = {
    "GET"    : _unavailableSupplierFunction,
    "POST"   : _unavailableSupplierFunction,
    "PUT"    : _unavailableSupplierFunction,
    "DELETE" : _unavailableSupplierFunction
}

_processingMap = {
    "HTML"   : _processHtmlQuery,
    "JSON"   : _processJsonQuery,
    "FILE"   : _processFileQuery,
}

_replyMap = {
    "HTML"   : _createHtmlReply,
    "JSON"   : _createJsonReply
}

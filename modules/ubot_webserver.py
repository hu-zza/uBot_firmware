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


_connection = 0
_headerSent = False

_started = False
_period = config.get("web_server", "period")
_timeout = config.get("web_server", "timeout")
_timer = Timer(-1)
_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
_poller = uselect.poll()

_socket.bind(("", 80))
_socket.listen(5)
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

_major, _minor, _patch = config.get("system", "firmware")
_server = "uBot_firmware/{}.{}.{}".format(_major, _minor, _patch)
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

_jsonSender = None

_denyHtml = not config.get("web_server", "html_enabled")
_denyJson = not config.get("web_server", "json_enabled")
_log_event    = config.get("web_server", "log_event")
_log_request  = config.get("web_server", "log_request")
_log_response = config.get("web_server", "log_response")
_log_reset    = config.get("web_server", "log_reset")

allowedMethods     = {"GET", "POST", "PUT", "DELETE"}
allowedHtmlMethods = {"GET", "POST"}
allowedJsonMethods = {"GET", "POST", "PUT", "DELETE"}
_hasJsonBody       = {"POST", "PUT"}



################################
## CONFIG


def setJsonSender(method):
    global _jsonSender
    _jsonSender = method

def setJsonCallback(method, jsonFunction):
    global _jsonFunctionMap

    if isAllowed(method, allowedJsonMethods):
        _jsonFunctionMap[method] = jsonFunction


################################
## PUBLIC METHODS

def start():
    global _started

    if not _started and config.get("web_server", "active"):
        _timer.init(period = _period, mode = Timer.PERIODIC, callback = _poll)
        _started = True


def stop():
    global _started

    if _started:
        _timer.deinit()
        _started = False


def isAllowed(methodName, methodSet = None):
    if methodSet is None:
        methodSet = allowedMethods

    return methodName in methodSet


################################
## PRIVATE, HELPER METHODS

def _logRequest():
    if _log_event:
        logger.append("{}\t{}".format(_request.get("method"), _request.get("rawPath")))

    if _log_request:
        logger.append(_request)


def _logResponse(response):
    if _log_event:
        metaResponse = response.get("meta").get("response")
        logger.append("{}\t{}".format(metaResponse.get("status").replace(" ", "\t", 1), metaResponse.get("message")))

    if _log_response:
        logger.append(response)


def _poll(timer):
    try:
        if not motor.isProcessing():
            result = _poller.poll(_timeout)

            if result:
                _clearOldRequestData()
                _processIncoming(result[0][0])
    except Exception as e:
        logger.append(e)


def _clearOldRequestData():
    global _request

    _request["method"] = ""
    _request["rawPath"] = ""
    _request["path"] = data.INVALID_PATH
    _request["contentLength"] = 0
    _request["contentType"] = ""
    _request["accept"] = ""
    _request["body"] = ""
    _request["processing"] = "UNDEFINED"


def _processIncoming(incoming):
    global _incoming, _connection, _headerSent
    _incoming = incoming

    try:
        _readIncoming()
        _processBody()
    except Exception as e:
        logger.append(e)
        _reply("400 Bad Request", "The server could not understand the request due to invalid syntax.")
    finally:
        _connection.close()
        _connection = 0
        _headerSent = False


def _readIncoming():
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
    _chooseProcessingMethod()


def _processHeaderLine(line):
    global _request

    line = line.lower()

    if _request.get("method") == "":
        firstSpace = line.find(" ")
        pathEnd = line.find(" http")

        _request["method"]  = line[0:firstSpace].upper()

        rawPath = line[firstSpace + 1:pathEnd]
        _request["rawPath"] = rawPath
        _request["path"] = data.createPath(rawPath)
        data.preparePathIfSpecial(_request.get("path"))

    if 0 <= line.find("content-length:"):
        lengthString = line[15:].strip()
        _request["contentLength"] = int(lengthString) if lengthString.isdigit() else 0
        
    if 0 <= line.find("content-type:"):
        _request["contentType"] = line[13:].strip()
        
    if 0 <= line.find("accept:"):
        _request["accept"] = line[7:].strip()


def _chooseProcessingMethod():
    global _request

    accept = _request.get("accept")
    contentType = _request.get("contentType")
    union = accept + contentType

    if "text/html" in union:
        _request["processing"] = "HTML"
    elif "application/json" in union or "*/*" in accept:
        _request["processing"] = "JSON"
    else:
        _request["processing"] = "UNDEFINED"


def _processBody():
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


def _unsupportedTypeHandler():
    _reply("415 Unsupported Media Type", "'Content-Type' / 'Accept' should be 'text/html' or 'application/json'.")


def _processHtmlQuery():
    if _denyHtml:
        result = _unavailableSupplierFunction()
        _reply(result[0], result[1])
    elif isAllowed(_request.get("method"), allowedHtmlMethods):
        _htmlFunctionMap[_request.get("method")]()
    else:
        _reply("405 Method Not Allowed", "The following HTTP request methods are allowed with text/html "
                                         "content type: {}.".format(", ".join(allowedHtmlMethods)))


def _unavailableSupplierFunction(a = None, b = None, c = None):
    return "503 Service Unavailable", "This service is not yet available.", {}


def _processHtmlGetQuery():
    path = _request.get("rawPath")

    if path in template.title:
        _replyWithHtmlTemplate(path)
    else:
        path = _request.get("path")

        if "raw" in path.args:
            _replyWithHtmlRaw(path)
        else:
            _reply("404 Not Found", "Request: Get the page / file '{}'.".format(path))


def _replyWithHtmlTemplate(path: str) -> None:
    _sendHeader()
    _connection.write(template.getPageHeadStart().format(template.title.get(path)))

    for style in template.style.get(path):
        _connection.write(style())

    _connection.write(template.getPageHeadEnd())

    for part in template.parts.get(path):
        _connection.write(part())

    if path.startswith("/debug"):                                                                     # TODO: Extracting
        _connection.write("        <h3>Information panels</h3>\r\n")

        for panelTitle in sorted(template.debugPanels.keys()):
            _connection.write("            <a href='http://{0}{1}' target='_blank'>{2}</a><br>\r\n"
                              .format(config.get("ap", "ip"), template.debugPanels.get(panelTitle), panelTitle))

        _connection.write("        <br><br><hr><hr>\r\n")
        _connection.write("        <h3>Log files</h3>\r\n")

        _powerOns     = config.get("system", "power_ons")
        _host         = "http://{}/raw".format(config.get("ap", "ip"))
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
    _connection.write(template.getPageFooter())
    _logResponse(_getBasicReplyMap("200 OK", "Request: Get the page '{}'.".format(path)))


def _replyWithHtmlRaw(path: data.Path) -> None:
    _sendHeader()
    _connection.write(template.getPageHeadStart().format("μBot Raw &nbsp;| &nbsp; {}".format(path)))
    _connection.write(template.getGeneralStyle())
    _connection.write(template.getRawStyle())
    _connection.write(template.getPageHeadEnd())
    _sendRaw(path.path)
    _connection.write(template.getPageFooter())
    _logResponse(_getBasicReplyMap("200 OK", "Request: Get the file '{}'.".format(path)))


def _sendHeader(status = "200 OK", length = None, allow = None):
    global _headerSent

    if not _headerSent:
        reply = "text/html"
        allowSet = ", ".join(allowedHtmlMethods)

        if _request.get("processing") == "JSON":
            reply = "application/json"
            allowSet = ", ".join(allowedJsonMethods)

        if allow is None:
            allow = allowSet

        _connection.write("HTTP/1.1 {}\r\n".format(status))
        if length is not None:
            _connection.write("Content-Length: {}\r\n".format(length))
        _connection.write("Content-Type: {}; charset=UTF-8\r\n".format(reply))
        _connection.write("Content-Encoding: identity\r\n")
        _connection.write("Transfer-Encoding: identity\r\n")
        _connection.write("Server: {}\r\n".format(_server))
        _connection.write("Allow: {}\r\n".format(allow))
        _connection.write("Cache-Control: no-cache\r\n")                                   # TODO: Make caching possible
        _connection.write("Connection: close\r\n\r\n")
        _headerSent = True


def _processHtmlPostQuery():
    _reply("501 Not Implemented", "This service is not implemented yet.")


def _processJsonQuery():
    if _denyJson:
        result = _unavailableSupplierFunction()
        _reply(result[0], result[1], result[2])
    elif isAllowed(_request.get("method"), allowedJsonMethods):
        _startJsonProcessing()
    else:
        methods = ", ".join(allowedJsonMethods)
        _reply("405 Method Not Allowed", "The following HTTP request methods are allowed with application/json "
                                         "content type: {}.".format(methods))


def _startJsonProcessing():
    _jsonSender(_request.get("path"), _request.get("body"))
    result = _jsonFunctionMap[_request.get("method")]()
    _reply(result[0], result[1], result[2])


def _reply(responseStatus, message, result = None):
    """ Try to reply with a text/html or application/json
        if the connection is alive, then closes it. """
    try:
        reply = _replyMap.setdefault(_request.get("processing"), _createHtmlReply)(responseStatus, message, result)

        if _connection != 0:
            _sendHeader(responseStatus, len(reply))
            _connection.write(reply)                                                    # TODO: written bytes check, etc

        _logResponse(_response)
    except Exception as e:
        if _log_reset:
            logger.append(e)


def _createHtmlReply(responseStatus, message, result = None):
    _updateReply(responseStatus, message, result)

    if responseStatus == "404 Not Found":
        message = _getHelperLinks()

    style = template.getGeneralStyle() + template.getSimpleStyle()
    return template.getSimplePage().format(title = responseStatus, style = style, body = message)


def _createJsonReply(responseStatus, message, result = None):
    _updateReply(responseStatus, message, result)
    return ujson.dumps(_response)



def _updateReply(responseStatus, message, result = None):
    global _response
    _response = _getBasicReplyMap(responseStatus, message, result)


def _getBasicReplyMap(responseStatus, message, result = None):
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


def _getMessageWithFlags(message, statusCode):
    result = message

    if 100 <= statusCode < 200:
        result = "[INFO] " + message
    elif 200 <= statusCode < 300:
        result = "[DONE] " + message
    elif 300 <= statusCode < 400:
        result = "[LINK] " + message
    elif 400 <= statusCode < 600:
        result = "[FAIL] {}  // More info: {}".format(message, config.get("constant", "api_link"))

    return result


def _getHelperLinks():
    helperLinks = "        <ul class='links'>\r\n"
    helperLinks += "            <li>Sitemap</li>\r\n"
    for key in sorted(template.title.keys()):
        if key == "/" or key[1] != "_":
            helperLinks += "            <li><a href='{key}'>{title}</a><br><small>{host}{key}</small></li>\r\n".format(
                host = config.get("ap", "ip"), key = key, title = template.title.get(key)
            )
    helperLinks += "        </ul>\r\n"
    return helperLinks


def _sendRaw(path):
    """ If the path links to a dir, sends a linked list, otherwise tries to send the content of the target entity. """
    try:
        if path[-1] == "/":           # Folder -> A practical, cosy, and a bit dirty constraint for simple URL handling.
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
    "GET":  _processHtmlGetQuery,
    "POST": _processHtmlPostQuery
}

_jsonFunctionMap = {
    "GET":    _unavailableSupplierFunction,
    "POST":   _unavailableSupplierFunction,
    "PUT":    _unavailableSupplierFunction,
    "DELETE": _unavailableSupplierFunction
}

_processingMap = {
    "HTML": _processHtmlQuery,
    "JSON": _processJsonQuery
}

_replyMap = {
    "HTML": _createHtmlReply,
    "JSON": _createJsonReply
}

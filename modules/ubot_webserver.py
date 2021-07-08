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
import ubot_logger   as logger
import ubot_motor    as motor
import ubot_template as template


_connection = 0
_address = 0

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
_inMethod = ""
_inPath = ""
_inContentLength = 0
_inContentType = ""
_inAccept = ""
_inBody = ""

_denyHtml = not config.get("web_server", "html_enabled")
_denyJson = not config.get("web_server", "json_enabled")

allowedMethods     = {"GET", "POST", "PUT", "DELETE"}
allowedHtmlMethods = {"GET", "POST"}
allowedJsonMethods = {"GET", "POST", "PUT", "DELETE"}
_hasJsonBody       = {"POST", "PUT"}


################################
## CONFIG

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

def _logRequest(request):
    logger.append("{}\t{}".format(request.get("method"), request.get("path")))
    logger.append(request)


def _logResponse(response):
    meta = response.get("meta")
    logger.append("{}\t{}".format(meta.get("status").replace(" ", "\t", 1), meta.get("message")))
    logger.append(response)


def _poll(timer):
    try:
        if not motor.isProcessing():
            result = _poller.poll(_timeout)

            if result:
                _processIncoming(result[0][0])
    except Exception as e:
        logger.append(e)


def _processIncoming(incoming):
    global _incoming
    _incoming = incoming

    try:
        _readIncoming()
        _processBody()
    finally:
        _connection.close()


def _readIncoming():
    global _connection, _address, _inMethod, _inBody

    _connection, _address = _incoming.accept()
    requestFile = _connection.makefile("rwb", 0)
    _inMethod = ""

    while True:
        line = requestFile.readline()

        if not line:
            break
        elif line == b"\r\n":
            if 0 < _inContentLength:
                _inBody = str(requestFile.read(_inContentLength), "utf-8")
            break
        
        _processHeaderLine(str(line, "utf-8"))


def _processHeaderLine(line):
    global _inMethod, _inPath, _inContentLength, _inContentType, _inAccept
    
    if _inMethod == "":
        firstSpace = line.find(" ")
        pathEnd = line.find(" HTTP")

        _inMethod = line[0:firstSpace].upper()
        _inPath = line[firstSpace + 1:pathEnd].lower()
        
    if 0 <= line.lower().find("content-length:"):
        _inContentLength = int(line[15:].strip())
        
    if 0 <= line.lower().find("content-type:"):
        _inContentType = line[13:].strip().lower()
        
    if 0 <= line.lower().find("accept:"):
        _inAccept = line[7:].strip().lower()


def _processBody():
    _logRequest(
        {"path":   _inPath,
         "method": _inMethod,
         "type":   _inContentType,
         "accept": _inAccept,
         "body":   _inBody
         })

    if isAllowed(_inMethod):
        if "text/html" in _inContentType or "text/html" in _inAccept:
            _processHtmlQuery()
        elif "application/json" in _inContentType or "application/json" in _inAccept or "*/*" in _inAccept:
            _processJsonQuery()
        else:
            _reply("HTML", "415 Unsupported Media Type",
                   "'Content-Type' / 'Accept' should be 'text/html' or 'application/json'.")
    else:
        _reply("HTML", "405 Method Not Allowed",
               "The following HTTP request methods are allowed: {}.".format(", ".join(allowedMethods)))


def _processHtmlQuery():
    if _denyHtml:
        result = _unavailableSupplierFunction()
        _reply("HTML", result[0], result[1])
    elif isAllowed(_inMethod, allowedHtmlMethods):
        _htmlFunctionMap[_inMethod]()
    else:
        _reply("HTML", "405 Method Not Allowed", "The following HTTP request methods are allowed with text/html "
                                                 "content type: {}.".format(", ".join(allowedHtmlMethods)))


def _unavailableSupplierFunction(a = None, b = None, c = None):
    return "503 Service Unavailable", "This service is not yet available.", {}


def _processHtmlGetQuery():
    try:
        if _inPath in template.title:
            _replyWithHtmlTemplate()
        elif _inPath[:5] == "/raw/":
            _replyWithHtmlRaw()
        else:
            _reply("HTML", "404 Not Found", "Request: Get the page / file '{}'.".format(_inPath))
    except Exception as e:
        _reply("HTML", "500 Internal Server Error", "A fatal error occurred during processing the HTML GET request.", e)


def _replyWithHtmlTemplate():
    _sendHeader()
    _connection.write(template.getPageHeadStart().format(template.title.get(_inPath)))

    for style in template.style.get(_inPath):
        _connection.write(style())

    _connection.write(template.getPageHeadEnd())

    for part in template.parts.get(_inPath):
        _connection.write(part())

    if _inPath == "/debug":                                                                           # TODO: Extracting
        _connection.write("        <h3>Information panels</h3>\r\n")

        for panelTitle in sorted(template.debugPanels.keys()):
            _connection.write("            <a href='http://{0}{1}' target='_blank'>{2}</a><br>\r\n"
                              .format(config.get("ap", "ip"), template.debugPanels.get(panelTitle), panelTitle))

        _connection.write("        <br><br><hr><hr>\r\n")
        _connection.write("        <h3>Log files</h3>\r\n")

        _powerOns     = config.get("system", "power_ons")
        _host         = "http://{}/raw".format(config.get("ap", "ip"))
        _fileNameBase = "/log/{{}}/{:010d}.txt".format(config.get("system", "power_ons"))
        _fallbackBase = "/log/{}/0000000000.txt"

        _connection.write("            <table class='data'>\r\n")
        for category in logger.getLogCategories():
            _connection.write("                <tr><td><strong>{}:</strong></td>".format(category))

            _currentLog = _fileNameBase.format(category)
            _fallbackLog = _fallbackBase.format(category)

            _connection.write("<td><a href='{}{}' target='_blank'>current ({} B)</a></td>"
                              .format(_host, _currentLog, uos.stat(_currentLog)[6]))

            _connection.write("<td><a href='{}{}' target='_blank'>fallback ({} B)</a></td></tr>\r\n"
                              .format(_host, _fallbackLog, uos.stat(_fallbackLog)[6]))

        _connection.write("            </table>\r\n")
    _connection.write(template.getPageFooter())
    _logResponse(_getBasicReplyMap("200 OK", "Request: Get the page '{}'.".format(_inPath)))


def _replyWithHtmlRaw():
    _sendHeader()
    _connection.write(template.getPageHeadStart().format("&microBot Raw &nbsp;| &nbsp; " + _inPath[4:]))
    _connection.write(template.getGeneralStyle())
    _connection.write(template.getRawStyle())
    _connection.write(template.getPageHeadEnd())
    _sendRaw(_inPath[4:])
    _connection.write(template.getPageFooter())
    _logResponse(_getBasicReplyMap("200 OK", "Request: Get the file '{}'.".format(_inPath[4:])))


def _sendHeader(returnFormat = "HTML", status = "200 OK", allow = None):
    reply = "text/plain"
    allowSet = ", ".join(allowedMethods)

    if returnFormat == "HTML":
        reply = "text/html"
        allowSet = ", ".join(allowedHtmlMethods)
    elif returnFormat == "JSON":
        reply = "application/json"
        allowSet = ", ".join(allowedJsonMethods)

    if allow is None:
        allow = allowSet

    _connection.write("HTTP/1.1 {}\r\n".format(status))
    _connection.write("Content-Type: {}\r\n".format(reply))
    _connection.write("Allow: {}\r\n".format(allow))
    _connection.write("Connection: close\r\n\r\n")


def _processHtmlPostQuery():
    _reply("HTML", "501 Not Implemented", "This service is not implemented yet.")


def _processJsonQuery():
    if _denyJson:
        result = _unavailableSupplierFunction()
        _reply("JSON", result[0], result[1], result[2])
    elif isAllowed(_inMethod, allowedJsonMethods):
        if _isSpecialJsonRequest():
            _handleSpecialJsonRequest()
        else:
            _startJsonProcessing()
    else:
        methods = ", ".join(allowedJsonMethods)
        _reply("JSON", "405 Method Not Allowed", "The following HTTP request methods are allowed with application/json "
                                                 "content type: {}.".format(methods))


def _isSpecialJsonRequest():
    return False


def _handleSpecialJsonRequest():
    pass


def _startJsonProcessing():
    global _inBody

    try:
        arr = _inPath.split("/")
        arr += [""] * (11 - len(arr))                    # add placeholders to prevent IndexError
        arr = tuple(arr[1:])                             # arr[0] is always empty string because of leading slash
        isPresent = tuple([item != "" for item in arr])

        _inBody = ujson.loads(_inBody) if _inMethod in _hasJsonBody else {}

        result = _jsonFunctionMap[_inMethod](arr, isPresent, _inBody)
        _reply("JSON", result[0], result[1], result[2])
    except Exception as e:
        _reply("JSON", "400 Bad Request", "The request body could not be parsed and processed.", e)


def _reply(returnFormat, responseStatus, message, result = None):
    """ Try to reply with a text/html or application/json
        if the connection is alive, then closes it. """

    try:
        replyMap = _getBasicReplyMap(responseStatus, message, result)

        _sendHeader(returnFormat, responseStatus)

        reply = ""
        if returnFormat == "HTML":
            if responseStatus == "404 Not Found":
                message = _getHelperLinks()

            style = template.getGeneralStyle() + template.getSimpleStyle()
            reply = template.getSimplePage().format(title = responseStatus, style = style, body = message)
        elif returnFormat == "JSON":
            reply = ujson.dumps(replyMap)

        _connection.write(reply)                                                        # TODO: written bytes check, etc
        _logResponse(replyMap)
    except Exception as e:
        logger.append(e)


def _getBasicReplyMap(responseStatus, message, result = None):
    statusCode = int(responseStatus[:3])

    replyMap = {
        "meta": {
            "code": statusCode,
            "status": responseStatus,
            "message": _getMessageWithFlags(message, statusCode)},
        "result": {} if result is None else result
    }
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
                host=config.get("ap", "ip"), key=key, title=template.title.get(key)
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
                for fileName in uos.listdir(path):
                    _connection.write("                <tr>")

                    try:
                        stat = uos.stat("{}{}".format(path, fileName))

                        if stat[0] == 0x04000:  # Folder
                            _connection.write(
                                "<td><a href='{fileName}/'>{fileName}/</a></td><td>-</td>".format(fileName = fileName))

                        elif stat[0] == 0x08000:  # File
                            _connection.write(
                                "<td><a href='{fileName}'>{fileName}</a></td><td>{fileSize:,} B</td>".format(
                                    fileName = fileName, fileSize = stat[6]))

                        else:
                            _connection.write("<td colspan='2'>{}</td>".format(fileName))

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

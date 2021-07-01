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

import gc, network, ujson, uos, uselect, usocket

from machine import Timer

import ubot_config   as config
import ubot_logger   as logger
import ubot_motor    as motor
import ubot_template as template


_ap = network.WLAN(network.AP_IF)

_jsonFunction = 0
_jsonGetFunction = 0
_jsonPostFunction = 0
_jsonPutFunction = 0
_jsonDeleteFunction = 0
_connection = 0
_address = 0

_started = False
_period = config.get("webServer", "period")
_timeout = config.get("webServer", "timeout")
_timer = Timer(-1)
_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
_poller = uselect.poll()

_socket.bind(("", 80))
_socket.listen(5)
_poller.register(_socket, uselect.POLLIN)



################################
## CONFIG

def setJsonCallback(method, jsonFunction):
    global _jsonGetFunction
    global _jsonPostFunction
    global _jsonPutFunction
    global _jsonDeleteFunction

    if method == "GET":
        _jsonGetFunction = jsonFunction
    elif method == "POST":
        _jsonPostFunction = jsonFunction
    elif method == "PUT":
        _jsonPutFunction = jsonFunction
    elif method == "DELETE":
        _jsonDeleteFunction = jsonFunction


################################
## PUBLIC METHODS

def start():
    global _started

    if not _started and config.get("webServer", "active"):
        _timer.init(period=_period, mode=Timer.PERIODIC, callback=_poll)
        _started = True


def stop():
    global _started

    if _started:
        _timer.deinit()
        _started = False


################################
## PRIVATE, HELPER METHODS

def _poll(timer):
    try:
        if not motor.isProcessing():
            result = _poller.poll(_timeout)

            if result:
                _processIncoming(result[0][0])
    except Exception as e:
        logger.append(e)


def _processIncoming(incoming):
    global _connection
    global _address

    method = ""
    path = ""
    contentLength = 0
    contentType = ""
    accept = ""
    body = ""

    _connection, _address = incoming.accept()
    requestFile = _connection.makefile("rwb", 0)

    try:
        while True:
            line = requestFile.readline()

            if not line:
                break
            elif line == b"\r\n":
                if 0 < contentLength:
                    body = str(requestFile.read(contentLength), "utf-8")
                break

            line = str(line, "utf-8")

            if method == "":
                firstSpace = line.find(" ")
                pathEnd = line.find(" HTTP")

                method = line[0:firstSpace].upper()
                path = line[firstSpace + 1:pathEnd].lower()

            if 0 <= line.lower().find("content-length:"):
                contentLength = int(line[15:].strip())

            if 0 <= line.lower().find("content-type:"):
                contentType = line[13:].strip().lower()

            if 0 <= line.lower().find("accept:"):
                accept = line[7:].strip().lower()

        logger.append("HTTP request:  {}  {}".format(method, path))

        if method in ("GET", "POST", "PUT", "DELETE"):
                if "text/html" in contentType or "text/html" in accept:
                    _processHtmlQuery(method, path, body)
                elif "application/json" in contentType or "application/json" in accept or "*/*" in accept:
                    _processJsonQuery(method, path, body)
                else:
                    _reply("HTML", "415 Unsupported Media Type",
                           "'Content-Type' / 'Accept' should be 'text/html' or 'application/json'. "
                           "More info: https://zza.hu/uBot_API")
        else:
            _reply("HTML", "405 Method Not Allowed",
                   "The following HTTP request methods are allowed: GET, POST, PUT and DELETE. "
                   "More info: https://zza.hu/uBot_API")
    finally:
        _connection.close()


def _processHtmlQuery(method, path, body):
    if method == "GET":
        _processHtmlGetQuery(path)
    elif method == "POST":
        _processHtmlPostQuery(path, body)
    else:
        _reply("HTML", "405 Method Not Allowed",
               "Only GET and POST HTTP request methods are allowed with text/html content type. "
               "More info: https://zza.hu/uBot_API", "GET, POST")


def _processHtmlGetQuery(path):
    try:
        if path in template.title:
            _connection.write("HTTP/1.1 200 OK\r\n")
            _connection.write("Content-Type: text/html\r\n")
            _connection.write("Connection: close\r\n\r\n")
            _connection.write(template.getPageHeadStart().format(template.title.get(path)))

            for style in template.style.get(path):
                _connection.write(style())

            _connection.write(template.getPageHeadEnd())

            for part in template.parts.get(path):
                _connection.write(part())

            if path == "/debug":
                _connection.write("        <br><br><hr><hr>\n")
                _connection.write("        <h3>Information panels</h3>\n")

                for panelTitle in sorted(template.debugPanels.keys()):
                    _connection.write(
                        "            <a href='http://{0}{1}' target='_blank'>{2}</a><br>\n".format(
                            _ap.ifconfig()[0], template.debugPanels.get(panelTitle), panelTitle))

                powerOnCount = config.get("system", "powerOnCount")
                _connection.write("        <br><br><hr><hr>\n")
                _connection.write("        <h3>Log files</h3>\n")

                for category in logger.getLogCategories():
                    _connection.write("            <h4>{}</h4>\n".format(category))

                    _connection.write(
                        "            <a href='http://{0}/raw/log/{1}/{2:010d}.txt' target='_blank'>{2:010d}&nbsp;&nbsp;"
                        "&nbsp;// current</a><br>\n".format(_ap.ifconfig()[0], category, powerOnCount))

                    _connection.write(
                        "            <a href='http://{0}/raw/log/{1}/0000000000.txt' target='_blank'>0000000000&nbsp;"
                        "&nbsp;&nbsp;// fallback</a><br><br>\n".format(_ap.ifconfig()[0], category))

                _connection.write("        </ul>\n")

            _connection.write(template.getPageFooter())
            logger.append("HTTP response: 200 OK")
        elif path[:5] == "/raw/":
            _connection.write("HTTP/1.1 200 OK\r\n")
            _connection.write("Content-Type: text/html\r\n")
            _connection.write("Connection: close\r\n\r\n")
            _connection.write(template.getPageHeadStart().format("&microBot Raw &nbsp;| &nbsp; " + path[4:]))
            _connection.write(template.getGeneralStyle())
            _connection.write(template.getRawStyle())
            _connection.write(template.getPageHeadEnd())
            _sendRaw(path[4:])
            _connection.write(template.getPageFooter())
            logger.append("HTTP response: 200 OK")
        else:
            helperLinks = "        <ul class='links'>\n"
            helperLinks += "            <li>Sitemap</li>\n"

            for key in sorted(template.title.keys()):
                if key == "/" or key[1] != "_":
                    helperLinks += "            <li><a href='{key}'>{title}</a><br><small>{host}{key}</small></li>\n".format(
                        host=_ap.ifconfig()[0], key=key, title=template.title.get(key)
                    )

            helperLinks += "        </ul>\n"
            _reply("HTML", "404 Not Found", helperLinks)
    except Exception as e:
        logger.append(e)
    finally:
        _connection.close()


def _processHtmlPostQuery(path, body):
    _reply("HTML", "501 Not Implemented", "This service is not implemented yet. More info: https://zza.hu/uBot_API")


def _processJsonQuery(method, path, body):
    global _jsonFunction

    if method in ("GET", "POST", "PUT", "DELETE"):
        if method == "GET":
            _jsonFunction = _jsonGetFunction
        elif method == "POST":
            _jsonFunction = _jsonPostFunction
        elif method == "PUT":
            _jsonFunction = _jsonPutFunction
        else:
            _jsonFunction = _jsonDeleteFunction

        _startJsonProcessing(path, body if method in ("POST", "PUT") else "{}")
    else:
        _reply("HTML", "405 Method Not Allowed",
               "The following HTTP request methods are allowed with application/json content type: "
               "GET, POST, PUT and DELETE. More info: https://zza.hu/uBot_API")


def _startJsonProcessing(path, body):
    try:
        arr = path.split("/")
        arr += [""] * (11 - len(arr))                    # add placeholders to prevent IndexError
        arr = tuple(arr[1:])                             # arr[0] is always empty string because of leading slash
        isPresent = tuple([item != "" for item in arr])

        result = _jsonFunction(arr, isPresent, ujson.loads(body))
        _reply("JSON", result[0], result[1], result[2])
    except Exception as e:
        logger.append(e)
        _reply("JSON", "400 Bad Request", "The request body could not be parsed and processed. "
                                          "More info: https://zza.hu/uBot_API")


def _reply(returnFormat, httpCode, message, data = None, allow = "GET, POST, PUT, DELETE"):
    """ Try to reply with a text/html or application/json
        if the connection is alive, then closes it. """

    try:
        _connection.write("HTTP/1.1 " + httpCode + "\r\n")

        reply = "text/plain"
        if returnFormat == "HTML":
            reply = "text/html"
        elif returnFormat == "JSON":
            reply = "application/json"

        _connection.write("Content-Type: {}\r\n".format(reply))
        _connection.write("Allow: {}\r\n".format(allow))
        _connection.write("Connection: close\r\n\r\n")

        if returnFormat == "HTML":
            style = template.getGeneralStyle() + template.getSimpleStyle()
            reply = template.getSimplePage().format(title=httpCode, style=style, body=message)
        elif returnFormat == "JSON":
            reply = ujson.dumps(
                {"meta": {"dateTime": config.datetime(), "code": int(httpCode[:3]), "status": httpCode,
                          "message": message},
                 "data": data})

        _connection.write(reply)                                                        # TODO: written bytes check, etc
        logger.append("HTTP response: {}  {}".format(httpCode, message))
    except Exception:
        print("Exception @ ubot_webserver#_reply")
    finally:
        _connection.close()


def _sendRaw(path):
    """ If the path links to a dir, sends a linked list, otherwise tries to send the content of the target entity. """
    try:
        if path[-1] == "/":        # Directory -> A practical, cosy, and a bit dirty constraint for simple URL handling.
            _connection.write(("        <table>\n"
                               "            <thead>\n"
                               "                <tr><th scope='col'>Filename</th><th scope='col'>File size</th></tr>\n"
                               "            </thead>\n"
                               "            <tbody>\n"
                               "                <tr><td><a href='..'>..</a></td><td></td></tr>"))

            try:
                for fileName in uos.listdir(path):
                    _connection.write("                <tr>")

                    try:
                        stat = uos.stat("{}{}".format(path, fileName))

                        if stat[0] == 0x04000:  # Directory
                            _connection.write(
                                "<td><a href='{fileName}/'>{fileName}/</a></td><td>-</td>".format(fileName=fileName))

                        elif stat[0] == 0x08000:  # File
                            _connection.write(
                                "<td><a href='{fileName}'>{fileName}</a></td><td>{fileSize:,} B</td>".format(
                                    fileName=fileName, fileSize=stat[6]))

                        else:
                            _connection.write("<td colspan='2'>{}</td>".format(fileName))

                    except Exception:
                        _connection.write("<td class='info' colspan='2'>This entity cannot be listed.</td>")
                    _connection.write("</tr>\n")

                if len(uos.listdir(path)) == 0:
                    _connection.write(
                        "                <tr><td class='info' colspan='2'>This directory is empty.</td></tr>\n")

            except Exception:
                _connection.write("<td class='info' colspan='2'>[Errno 2] ENOENT : No such directory.</td>")

            _connection.write(("            </tbody>\n"
                               "        </table>\n"))
        else:
            _connection.write("        <pre>\n")
            try:
                with open(path) as file:
                    for line in file:
                        _connection.write(line)
            except Exception:
                _connection.write("[Errno 2] ENOENT : No such file.\n")
            _connection.write("        </pre>\n")
    except Exception:
        _connection.write("[Errno 2] ENOENT : No such file or directory.\n")

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

import gc, ujson, uos, uselect, usocket

from machine import Timer

import ubot_config   as config
import ubot_logger   as logger
import ubot_motor    as motor
import ubot_template as template


_jsonFunction  = 0
_connection    = 0
_address       = 0

_started       = False
_period        = config.get("webServer", "period")
_timeout       = config.get("webServer", "timeout")
_timer         = Timer(-1)
_socket        = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
_poller        = uselect.poll()

_socket.bind(("", 80))
_socket.listen(5)
_poller.register(_socket, uselect.POLLIN)



################################
## CONFIG

def setJsonCallback(jsonFunction):
    global _jsonFunction

    _jsonFunction = jsonFunction



################################
## PUBLIC METHODS

def start():
    global _started
    global _processing

    if not _started and config.get("webServer", "active"):
        _timer.init(period = _period, mode = Timer.PERIODIC, callback = _poll)
        _started    = True
        _processing = True


def stop():
    global _started
    global _processing

    if _started:
        _timer.deinit()
        _started    = False
        _processing = False



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

    method        = ""
    path          = ""
    contentLength = 0
    contentType   = ""
    body          = ""

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
                pathEnd    = line.find(" HTTP")

                method = line[0:firstSpace]
                path   = line[firstSpace+1:pathEnd]

            if 0 <= line.lower().find("content-length:"):
                contentLength = int(line[15:].strip())

            if 0 <= line.lower().find("content-type:"):
                contentType = line[13:].strip()

        if method == "GET":
            _processGetQuery(path)
        elif method == "POST":
            if contentType == "application/json":
                _processPostQuery(body)
            else:
                _reply("HTML", "400 Bad Request", "'Content-Type' should be 'application/json'.")
        else:
            _reply("HTML", "405 Method Not Allowed", "Only two HTTP request methods (GET and POST) are allowed.")
    finally:
        _connection.close()


def _processGetQuery(path):
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
                logFiles = (
                    ("Exceptions",  "log/exception/"),
                    ("Events",      "log/event/"),
                    ("Objects",     "log/object/")
                )

                for logFile in logFiles:
                    _connection.write("        <br><br><hr><hr>\n")
                    _connection.write("        <h3>{}</h3>\n".format(logFile[0]))
                    _sendRaw("{}{:010d}.txt".format(logFile[1], config.get("system", "powerOnCount")))
                    _connection.write("        <br><hr><br>\n")
                    _sendRaw("{}0000000000.txt".format(logFile[1]))

            _connection.write(template.getPageFooter())
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
        else:
            helperLinks = "        <ul class='links'>\n"
            helperLinks += "            <li>Sitemap</li>\n"

            for key in sorted(template.title.keys()):
                if key == "/" or key[1] != "_":
                    helperLinks += "            <li><a href='{key}'>{title}</a><br><small>{host}{key}</small></li>\n".format(
                        host = "192.168.11.1", key = key, title = template.title.get(key)
                    )

            helperLinks += "        </ul>\n"
            _reply("HTML", "404 Not Found", helperLinks)
    except Exception as e:
        logger.append(e)
    finally:
        _connection.close()


def _processPostQuery(body):
    try:
        json = ujson.loads(body)

        if json.get("estimatedExecutionTime") and 10 < json.get("estimatedExecutionTime"):
            _reply("JSON", "200 OK", "JSON parsed, execution in progress.")

        _reply("JSON", "200 OK", _jsonFunction(json))
    except Exception as e:
        logger.append(e)
        _reply("JSON", "400 Bad Request", "The request body could not be parsed and processed.")


def _reply(returnFormat, httpCode, message):
    """ Try to reply with a text/html or application/json
        if the connection is alive, then closes it. """

    try:
        _connection.write("HTTP/1.1 " + httpCode + "\r\n")

        if returnFormat == "HTML":
            reply = "text/html"
        elif returnFormat == "JSON":
            reply = "application/json"

        _connection.write("Content-Type: {0}\r\n".format(reply))
        _connection.write("Connection: close\r\n\r\n")

        if returnFormat == "HTML":
            style = template.getGeneralStyle() + template.getSimpleStyle()
            reply = template.getSimplePage().format(title = httpCode, style = style, body = message)
        elif returnFormat == "JSON":
            reply = ujson.dumps({"code" : httpCode, "message" : message, "dateTime": config.datetime()})

        _connection.write(reply)
    except Exception:
        print("The connection has been closed.")
    finally:
        _connection.close()


def _sendRaw(path):
    """ If the path links to a dir, sends a linked list, otherwise tries to send the content of the target entity. """
    try:
        if path[-1] == "/":                                 # Directory (practical, however stat() would be more elegant)
            _connection.write(("        <table>\n"
                               "            <thead>\n"
                               "                <tr><th scope='col'>Filename</th><th scope='col'>File size</th></tr>\n"
                               "            </thead>\n"
                               "            <tbody>\n"))

            try:
                for fileName in uos.listdir(path):
                    _connection.write("                <tr>")

                    try:
                        stat = uos.stat("{}{}".format(path, fileName))

                        if stat[0] == 0x04000:              # Directory
                            _connection.write("<td><a href='{fileName}/'>{fileName}/</a></td><td>-</td>".format(fileName = fileName))

                        elif stat[0] == 0x08000:            # File
                            _connection.write("<td><a href='{fileName}'>{fileName}</a></td><td>{fileSize:,} B</td>".format(fileName = fileName, fileSize = stat[6]))

                        else:
                            _connection.write("<td colspan='2'>{}</td>".format(fileName))

                    except Exception:
                        _connection.write("<td class='info' colspan='2'>This entity cannot be listed.</td>")
                    _connection.write("</tr>\n")

                if len(uos.listdir(path)) == 0:
                    _connection.write("                <tr><td class='info' colspan='2'>This directory is empty.</td></tr>\n")

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

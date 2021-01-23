import gc, ujson, usocket

from machine import RTC

import ubot_exception        as exception
import ubot_webpage_template as template


_socket       = 0
_dateTime     = 0
_config       = 0
_jsonFunction = 0
_connection   = 0
_address      = 0



################################
## CONFIG

def config(socket, dateTime, config, jsonFunction):
    global _socket
    global _dateTime
    global _config
    global _jsonFunction

    _socket       = socket
    _dateTime     = dateTime
    _config       = config
    _jsonFunction = jsonFunction

    template.config(config, dateTime)



################################
## PUBLIC METHODS

def start():
    global _config

    _config['webServerActive'] = True

    if _config.get("apActive"):
        while _config.get("webServerActive"):
            try:
                _processSockets()
            except Exception as e:
                exception.append(e)


def stop(message):
    global _config

    if _config.get("webServerActive"):
        try:
            _reply("JSON", "200 OK", [message])
            _config['webServerActive'] = False
        except Exception as e:
            exception.append(e)



################################
## PRIVATE, HELPER METHODS

def _processSockets():
    global _connection
    global _address

    method        = ""
    path          = ""
    contentLength = 0
    contentType   = ""
    body          = ""

    _connection, _address  = _socket.accept()
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
            _reply("HTML", "405 Method Not Allowed", "Only two HTTP request methods (GET and PUT) are allowed.")
    finally:
        _connection.close()


def _processGetQuery(path):
    try:
        if path in template.title:
            _connection.send("HTTP/1.1 200 OK\r\n")
            _connection.send("Content-Type: text/html\r\n")
            _connection.send("Connection: close\r\n\r\n")
            _connection.sendall(template.getPageHeadStart().format(template.title.get(path)))

            for style in template.style.get(path):
                _connection.sendall(style())

            _connection.sendall(template.getPageHeadEnd())

            for part in template.parts.get(path):
                _connection.sendall(part())

            if path == "/debug":
                _sendRaw("log/exception/{:010d}.txt".format(_config.get("powerOnCount")))

            _connection.sendall(template.getPageFooter())
        elif path[:5] == "/raw/":
            _connection.send("HTTP/1.1 200 OK\r\n")
            _connection.send("Content-Type: text/html\r\n")
            _connection.send("Connection: close\r\n\r\n")
            _connection.sendall(template.getPageHeadStart().format("&microBot Raw | " + path[5:]))
            _connection.sendall(template.getPageHeadEnd())
            _sendRaw(path[5:])
            _connection.sendall(template.getPageFooter())
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
        exception.append(e)
    finally:
        _connection.close()


def _processPostQuery(body):
    try:
        json = ujson.loads(body)

        if json.get("estimatedExecutionTime") != None:
            if 10 < json.get("estimatedExecutionTime"):
                _reply("JSON", "200 OK", "JSON parsed, execution in progress.")

        _reply("JSON", "200 OK", _jsonFunction(json))
    except Exception as e:
        exception.append(e)
        _reply("JSON", "400 Bad Request", "The request body could not be parsed and processed.")


def _reply(returnFormat, httpCode, message):
    """ Try to reply with a text/html or application/json
        if the connection is alive, then closes it. """

    try:
        _connection.send("HTTP/1.1 " + httpCode + "\r\n")

        if returnFormat == "HTML":
            str = "text/html"
        elif returnFormat == "JSON":
            str = "application/json"

        _connection.send("Content-Type: " + str + "\r\n")
        _connection.send("Connection: close\r\n\r\n")

        if returnFormat == "HTML":
            style = template.getGeneralStyle() + template.getSimpleStyle()
            str   = template.getSimplePage().format(title = httpCode, style = style, body = message)
        elif returnFormat == "JSON":
            str   = ujson.dumps({"code" : httpCode, "message" : message, "dateTime": _dateTime.datetime()})

        _connection.sendall(str)
    except Exception:
        print("The connection has been closed.")
    finally:
        _connection.close()

def _sendRaw(path):
    _connection.send("        <pre>\n")
    with open(path) as file:
        for line in file:
            _connection.sendall(line)

    _connection.send("        </pre>\n")

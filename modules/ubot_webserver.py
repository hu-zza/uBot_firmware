import gc, ujson, usocket

from machine import RTC

import ubot_webpage_template as template


_socket       = 0
_dateTime     = 0
_config       = 0
_exceptions   = 0
_jsonFunction = 0
_connection   = 0
_address      = 0



################################
## CONFIG

def config(socket, dateTime, config, exceptionList, jsonFunction):
    global _socket
    global _dateTime
    global _config
    global _exceptions
    global _jsonFunction

    _socket       = socket
    _dateTime     = dateTime
    _config       = config
    _exceptions   = exceptionList
    _jsonFunction = jsonFunction

    template.config(exceptionList)



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
                _exceptions.append((_dateTime.datetime(), e))


def stop(message):
    global _config

    if _config.get("webServerActive"):
        try:
            _reply("JSON", "200 OK", [message])
            _config['webServerActive'] = False
        except Exception as e:
            _exceptions.append((_dateTime.datetime(), e))



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
        _connection.send("HTTP/1.1 200 OK\r\n")
        _connection.send("Content-Type: text/html\r\n")
        _connection.send("Connection: close\r\n\r\n")
        _connection.sendall(template.getPageHeadStart().format(template.title.get(path)))
        _connection.sendall(template.getGeneralStyle())
        _connection.sendall(template.getPageHeadEnd())

        for part in template.parts.get(path):
            _connection.sendall(part())

        _connection.sendall(template.getPageFooter())
    except Exception as e:
        _exceptions.append((_dateTime.datetime(), e))
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
        _exceptions.append((_dateTime.datetime(), e))
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
            str = template.getSimplePage().format(title = httpCode, style = template.getSimpleStyle(), body = message)
        elif returnFormat == "JSON":
            str = ujson.dumps({"code" : httpCode, "message" : message})

        _connection.sendall(str)
    except Exception:
        print("The connection has been closed.")
    finally:
        _connection.close()

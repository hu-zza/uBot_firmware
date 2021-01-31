import gc, ujson, uos, usocket

import ubot_config   as config
import ubot_logger   as logger
import ubot_template as template


_jsonFunction = 0
_connection   = 0
_address      = 0
_socket       = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
_socket.bind(("", 80))
_socket.listen(5)


################################
## CONFIG

def setJsonCallback(jsonFunction):
    global _jsonFunction

    _jsonFunction = jsonFunction



################################
## PUBLIC METHODS

def start():
    config.set("webServer", "active", True)

    if config.get("ap", "active"):
        while config.get("webServer", "active"):
            try:
                _processSockets()
            except Exception as e:
                logger.append(e)


def stop(message):
    if config.get("webServer", "active"):
        try:
            _reply("JSON", "200 OK", [message])
            config.set("webServer", "active", False)
        except Exception as e:
            logger.append(e)



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
            _connection.write(template.getPageHeadStart().format("&microBot Raw | " + path[5:]))
            _connection.write(template.getPageHeadEnd())
            _sendRaw(path[5:])
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

        if json.get("estimatedExecutionTime") != None:
            if 10 < json.get("estimatedExecutionTime"):
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
            str = "text/html"
        elif returnFormat == "JSON":
            str = "application/json"

        _connection.write("Content-Type: " + str + "\r\n")
        _connection.write("Connection: close\r\n\r\n")

        if returnFormat == "HTML":
            style = template.getGeneralStyle() + template.getSimpleStyle()
            str   = template.getSimplePage().format(title = httpCode, style = style, body = message)
        elif returnFormat == "JSON":
            str   = ujson.dumps({"code" : httpCode, "message" : message, "dateTime": config.datetime()})

        _connection.write(str)
    except Exception:
        print("The connection has been closed.")
    finally:
        _connection.close()


def _sendRaw(path):
    _connection.write("        <pre>\n")

    if path[-1] == "/":
        for fileName in uos.listdir(path):
            _connection.write("{}<br>\n".format(fileName))
    else:
        with open(path) as file:
            for line in file:
                _connection.write(line)

    _connection.write("        </pre>\n")

def checkButtons():
    if INP.value() == 1:
        INP.init(Pin.OUT)
        INP.off()           # pseudo pull-down
        INP.init(Pin.IN)

    if INP.value() == 1:
        if COUNTER_ACC != -1:
            COUNTER_ACC += 7

        COUNTER_ACC += COUNTER_POS

    CLK.on()

    COUNTER_POS += 1

    if 9 < COUNTER_POS:
        PRESSED_BTNS.append(COUNTER_ACC)
        COUNTER_ACC = -1
        COUNTER_POS = 0

    CLK.off()

def chk():
    checkButtons()

def getDebugTable(method, path, length = 0, type = "-", body = "-"):
    length = str(length)

    return """<table>
    <tr><td>Method: </td><td>""" + method + """</td></tr>
    <tr><td>Path: </td><td>"""   + path   + """</td></tr>
    <tr><td>Length: </td><td>""" + length + """</td></tr>
    <tr><td>Type: </td><td>"""   + type   + """</td></tr>
    <tr><td>Body: </td><td>"""   + body   + """</td></tr>
    </table>"""


def reply(returnFormat, httpCode, message, title = None):
    """ Try to reply with a text/html or application/json
        if the connection is alive, then closes it.
    """

    try:
        connection.send("HTTP/1.1 " + httpCode + "\r\n")

        if returnFormat == "HTML":
            str = "text/html"
        elif returnFormat == "JSON":
            str = "application/json"

        connection.send("Content-Type: " + str + "\r\n")
        connection.send("Connection: close\r\n\r\n")

        if returnFormat == "HTML":
            if title == None:
                title = httpCode
            str  = "<html><head><title>" + title + "</title></head>"
            str += "<body><h1>" + httpCode + "</h1><p>" + message + "</p></body></html>\r\n\r\n"
        elif returnFormat == "JSON":
            str = ujson.dumps({"code" : httpCode, "message" : message})

        connection.sendall(str)
    except:
        print("The connection has been closed.")
    finally:
        connection.close()

def togglePin(pin):
    pin.value(1 - pin.value())


def processJson(json):
    #item = json.get("datetime")


    for command in json.get("commands"):
        if command in PIN:
            togglePin(PIN.get(command))
        elif command[0:5] == "SLEEP":
            utime.sleep_ms(int(command[5:].strip()))


def processGetQuery():
    reply("HTML", "200 OK", getDebugTable(method, path), "uBot Debug Page")


def processPostQuery():

    try:
        json = ujson.loads(body)
        reply("JSON", "200 OK", ";-)")
        processJson(json)
    except:
        reply("JSON", "400 Bad Request", "The request body could not be parsed as JSON.")


########################################################################################################################
########################################################################################################################

COMMANDS = []

COUNTER_POS  = 0
COUNTER_ACC  = -1
PRESSED_BTNS = []

T.init(period = 10, mode = Timer.PERIODIC, callback = lambda t:chk())


while True:
    method = ""
    path = ""
    contentLength = 0
    contentType = ""
    body = ""

    connection, address = S.accept()
    requestFile         = connection.makefile("rwb", 0)

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
            processGetQuery()
        elif method == "POST":
            if contentType == "application/json":
                processPostQuery()
            else:
                reply("HTML", "400 Bad Request", "'Content-Type' should be 'application/json'.")
        else:
            reply("HTML", "405 Method Not Allowed", "Only two HTTP request methods (GET and PUT) are allowed.")
    finally:
        connection.close()

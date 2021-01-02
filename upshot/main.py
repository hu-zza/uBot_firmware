def advanceCounter():
    global COUNTER_POS

    CLK.on()
    COUNTER_POS += 1

    if 9 < COUNTER_POS:
        COUNTER_POS = 0

    CLK.off()


def checkButtons():
    global COUNTER_POS
    global PRESSED_BTNS
    pressed = -1

    for i in range(10):

        # pseudo pull-down
        if INP.value() == 1:        # DEPRECATED: New PCB design (2.1) will resolve this.
            INP.init(Pin.OUT)       # DEPRECATED: New PCB design (2.1) will resolve this.
            INP.off()               # DEPRECATED: New PCB design (2.1) will resolve this.
            INP.init(Pin.IN)        # DEPRECATED: New PCB design (2.1) will resolve this.


        if INP.value() == 1:
            if pressed == -1:
                pressed = COUNTER_POS
            else:
                pressed += 7 + COUNTER_POS

        advanceCounter()

    PRESSED_BTNS.append(pressed)
    advanceCounter()                # shift "resting position"

    # safety belt XD
    if 200 < len(PRESSED_BTNS):
        PRESSED_BTNS = PRESSED_BTNS[:20]

    if CONFIG.get("_wdActive"):
        global WD
        WD.feed()


def tryCheckButtons():
    try:
        checkButtons()
    except Exception as e:
        if len(EXCEPTIONS) < 20:
            EXCEPTIONS.append((DT.datetime(), e))


def tryCheckWebserver():
    try:
        if CONFIG.get("_wdActive") and AP.active():             # TODO: Some more sophisticated checks needed.
            global WD
            WD.feed()
    except Exception as e:
        if len(EXCEPTIONS) < 20:
            EXCEPTIONS.append((DT.datetime(), e))



def getDebugTable(method, path, length = 0, type = "-", body = "-"):
    length = str(length)

    result = ""

    with open("stats.html") as file:
        for line in file:
            result += line

    allMem = gc.mem_free() + gc.mem_alloc()
    freePercent = gc.mem_free() * 100 // allMem


    exceptionList = "<table class=\"exceptions\"><colgroup><col><col><col></colgroup><tbody>"
    index = 0

    for (dt, exception) in EXCEPTIONS:
        exceptionList += "<tr><td> {} </td><td> {}. {}. {}. {}:{}:{}.{} </td><td> {} </td></tr>".format(
            index, dt[0], dt[1], dt[2], dt[4], dt[5], dt[6], dt[7], exception
        )
        index += 1

    exceptionList += "</tbody></table>"

    return result.format(
        method = method, path = path, length = length, type = type, body = body,
        freePercent = freePercent, freeMem = gc.mem_free(), allMem = allMem,
        pressed = PRESSED_BTNS, commands = COMMANDS, evals = EVALS, exceptions = exceptionList
    )


def reply(returnFormat, httpCode, message, title = None):
    """ Try to reply with a text/html or application/json
        if the connection is alive, then closes it.
    """

    try:
        CONN.send("HTTP/1.1 " + httpCode + "\r\n")

        if returnFormat == "HTML":
            str = "text/html"
        elif returnFormat == "JSON":
            str = "application/json"

        CONN.send("Content-Type: " + str + "\r\n")
        CONN.send("Connection: close\r\n\r\n")

        if returnFormat == "HTML":
            if title == None:
                title = httpCode
            str  = "<html><head><title>" + title + "</title><style>"
            str += "tr:nth-child(even) {background: #EEE}"
            str += ".exceptions col:nth-child(1) {width: 40px;}"
            str += ".exceptions col:nth-child(2) {width: 250px;}"
            str += ".exceptions col:nth-child(3) {width: 500px;}"
            str += "</style></head>"
            str += "<body><h1>" + httpCode + "</h1><p>" + message + "</p></body></html>\r\n\r\n"
        elif returnFormat == "JSON":
            str = ujson.dumps({"code" : httpCode, "message" : message})

        CONN.sendall(str)
    except Exception:
        print("The connection has been closed.")
    finally:
        CONN.close()


def togglePin(pin):
    pin.value(1 - pin.value())


def processJson(json):
    global CONFIG
    global AP
    global BUZZ
    global MOT
    results = []

    if json.get("dateTime") != None:
        DT.datetime(eval(json.get("dateTime")))
        saveDateTime()
        results.append("New dateTime has been set.")

    if json.get("commandList") != None:
        for command in json.get("commandList"):
            if command[0:5] == "SLEEP":
                sleep_ms(int(command[5:].strip()))
            elif command[0:5] == "BEEP_":
                BUZZ.beep(int(command[5:].strip()), 2, 4)
            elif command[0:5] == "MIDI_":
                BUZZ.midiBeep(int(command[5:].strip()), 2, 4)
            elif command[0:5] == "EXEC_": ##############################################################################
                exec(command[5:])
            elif command[0:5] == "EVAL_": ##############################################################################
                EVALS.append(eval(command[5:]))


    if json.get("service") != None:
            for command in json.get("service"):
                if command == "START UART":
                    uart = UART(0, 115200)
                    uos.dupterm(uart, 1)
                    CONFIG['uart'] = True
                    results.append("UART has started.")
                elif command == "STOP UART":
                    uos.dupterm(None, 1)
                    CONFIG['uart'] = False
                    results.append("UART has stopped.")
                elif command == "START WEBREPL":
                    webrepl.start()
                    CONFIG['webRepl'] = True
                    results.append("WebREPL has started.")
                elif command == "STOP WEBREPL":
                    webrepl.stop()
                    CONFIG['webRepl'] = False
                    results.append("WebREPL has stopped.")
                elif command == "STOP WEBSERVER":
                    stopWebServer("WebServer has stopped.")
                elif command == "CHECK DATETIME":
                    results.append(str(DT.datetime()))
                elif command == "SAVE CONFIG":
                    saveConfig()
                    results.append("Configuration has saved.")

    if len(results) == 0:
        results = ["Processing has completed without any result."]

    reply("JSON", "200 OK", results)


def processGetQuery(path):
    reply("HTML", "200 OK", getDebugTable("GET", path), "uBot Debug Page")


def processPostQuery(body):

    try:
        json = ujson.loads(body)

        if json.get("execute") == True:
            reply("JSON", "200 OK", "JSON parsed, execution in progress.")

        processJson(json)
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))
        reply("JSON", "400 Bad Request", "The request body could not be parsed and processed.")


def processSockets():
    global CONN
    global ADDR

    method = ""
    path = ""
    contentLength = 0
    contentType = ""
    body = ""

    CONN, ADDR  = S.accept()
    requestFile = CONN.makefile("rwb", 0)

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
            processGetQuery(path)
        elif method == "POST":
            if contentType == "application/json":
                processPostQuery(body)
            else:
                reply("HTML", "400 Bad Request", "'Content-Type' should be 'application/json'.")
        else:
            reply("HTML", "405 Method Not Allowed", "Only two HTTP request methods (GET and PUT) are allowed.")
    finally:
        CONN.close()


def startWebServer():
    global CONFIG
    global EXCEPTIONS

    if CONFIG.get("webServer"):
        try:
            AP.active(True)
            CONFIG['_apActive'] = True
        except Exception as e:
            EXCEPTIONS.append((DT.datetime(), e))


        while CONFIG.get("webServer"):
            try:
                processSockets()
            except Exception as e:
                EXCEPTIONS.append((DT.datetime(), e))


def stopWebServer(message):
    global CONFIG
    global EXCEPTIONS

    try:
        CONFIG['webServer'] = False
        CONFIG['_apActive'] = False
        reply("JSON", "200 OK", [message])
        AP.active(False)
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))



if CONFIG.get("turtleHat"):
    TIMER.init(period = 20, mode = Timer.PERIODIC, callback = lambda t:tryCheckButtons())
else:
    TIMER.init(period = 1000, mode = Timer.PERIODIC, callback = lambda t:tryCheckWebserver())


startWebServer()

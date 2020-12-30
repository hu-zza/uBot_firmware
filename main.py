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
        if INP.value() == 1:
            INP.init(Pin.OUT)
            INP.off()           # needed explicitly
            INP.init(Pin.IN)


        if INP.value() == 1:
            if pressed == -1:
                pressed = COUNTER_POS
            else:
                pressed += 7 + COUNTER_POS

        advanceCounter()

    PRESSED_BTNS.append(pressed)
    advanceCounter()                # shift "resting position"

    # safety belt XD
    if 500 < len(PRESSED_BTNS):
        PRESSED_BTNS = PRESSED_BTNS[:100]



def beep(freq = 262, duration = 3, pause = 10, count = 1):
    for i in range(count):
        MSG.off()

        if BEEP_MODE:
            BEE.freq(freq)
            BEE.duty(512)

            rest = round((1000000 / freq) * (freq * duration / 10 ))
            sleep_us(rest)

            BEE.duty(0)
        else:
            MSG.on()
            sleep_ms(duration * 100)
            MSG.off()

        sleep_ms(pause * 10)


def midiBeep(noteOn = 60, duration = 3, pause = 10, count = 1):
    f = round(440 * pow(2, (noteOn - 69) / 12))
    beep(f, duration, pause, count)



def getDebugTable(method, path, length = 0, type = "-", body = "-"):
    length = str(length)

    result = ""

    with open("stats.html") as file:
        for line in file:
            result += line

    allMem = gc.mem_free() + gc.mem_alloc()
    freePercent = gc.mem_free() * 100 // allMem

    return result.format(
        method = method, path = path, length = length, type = type, body = body,
        freePercent = freePercent, freeMem = gc.mem_free(), allMem = allMem,
        pressed = PRESSED_BTNS, commands = COMMANDS, exceptions = EXCEPTIONS
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
            str  = "<html><head><title>" + title + "</title></head>"
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
    #item = json.get("datetime")


    for command in json.get("commands"):
        if command in PIN:
            togglePin(PIN.get(command))
        elif command[0:5] == "SLEEP":
            sleep_ms(int(command[5:].strip()))
        elif command[0:5] == "BEEP_":
            beep(int(command[5:].strip()), 2, 4)
        elif command[0:5] == "MIDI_":
            midiBeep(int(command[5:].strip()), 2, 4)
        elif command[0:5] == "EXEC_": ##################################################################################
            exec(command[5:])
        elif command[0:5] == "EVAL_": ##################################################################################
            eval(command[5:])


def processGetQuery(path):
    reply("HTML", "200 OK", getDebugTable("GET", path), "uBot Debug Page")


def processPostQuery(body):

    try:
        json = ujson.loads(body)
        reply("JSON", "200 OK", ";-)")
        processJson(json)
    except Exception:
        reply("JSON", "400 Bad Request", "The request body could not be parsed as JSON.")


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


########################################################################################################################
########################################################################################################################

T.init(period = 20, mode = Timer.PERIODIC, callback = lambda t:checkButtons())


while True:
    try:
        processSockets()
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))
        #if 10 < len(EXCEPTIONS):
        #    reset()

############
## IMPORTS

exceptions    = []
exitNotes     = []
missingConfig = False

try:
    import network, gc, uos, usocket, webrepl

    from machine        import Pin, PWM
    from sys            import print_exception
    from ubinascii      import hexlify
except Exception as e:
    exceptions.append(e)


# Start feedbackLed
try:
    feedbackLed = PWM(Pin(2), 15, 1010)
except Exception as e:
    exceptions.append(e)


try:
    import config as configPy
except Exception as e:
    missingConfig = True


############
## METHODS

def mkDir(path):
    try:
        uos.mkdir(path)
    except Exception as e:
        exceptions.append(e)


def recursiveRmdir(dirName):

    uos.chdir(dirName)

    for file in uos.listdir():
        type = "{0:07o}".format(uos.stat(file)[0])[:3]  # uos.stat(file)[0] -> ST_MODE

        if type == "010":                               # S_IFREG    0100000   regular file
            if dirName != "/":                          # \\
                uos.remove(file)                        #  \\
            elif file != ".setup":                      # .setup in root will be deleted later.
                uos.remove(file)
        elif type == "004":                             # S_IFDIR    0040000   directory
            if len(uos.listdir(file)) == 0:
                uos.remove(file)
            else:
                recursiveRmdir(file)

    if dirName != "/":
        uos.chdir("..")
        uos.remove(dirName)


def saveDictionaryToFile(dictionaryName):
    try:
        with open("etc/." + dictionaryName, "w") as file:
            dictionary = eval(dictionaryName)

            for key in sorted([k for k in dictionary.keys()]):
                value = dictionary.get(key)
                if isinstance(value, str):
                    file.write("{} = '{}'\n".format(key, value))
                else:
                    file.write("{} = {}\n".format(key, value))
    except Exception as e:
        exceptions.append(e)


def saveStringListToFile(path, stringList):
    try:
        with open(path, "w") as file:
            for item in stringList:
                file.write(item)
    except Exception as e:
        exceptions.append(e)


def saveToFile(path, content):
    try:
        saveStringListToFile(path, [str(content) + "\n"])
    except Exception as e:
        exceptions.append(e)



############
## CONFIG

# Enable automatic garbage collection.
try:
    gc.enable()
except Exception as e:
    exceptions.append(e)

# Copy the content of uBot driver files as raw
# text from the end of this file to .setup
try:
    separatorCount = 0
    copyToSetup    = False

    with open("boot.py") as boot, open(".setup", "w") as setup:
        for line in boot:
            if line == "#" * 120 + "\n":
                separatorCount += 1
                if separatorCount == 2:
                    copyToSetup = True
            else:
                separatorCount = 0

            if copyToSetup:
                setup.write(line)
except Exception as e:
    exceptions.append(e)


configDefaults = {

    # General settings, indicated in config.py too.

    "apEssid"         : "uBot__" + hexlify(network.WLAN().config('mac'), ':').decode()[9:],
    "apPassword"      : "uBot_pwd",
    "replPassword"    : "uBot_REPL",

    "uart"            : False,
    "webRepl"         : False,
    "webServer"       : True,

    "turtleHat"       : True,
    "beepMode"        : True,


    # These can also be configured manually (in config.py).
    # (But almost never will be necessary to do that.)

    "_pressLength"     : 5,
    "_firstRepeat"     : 25,

    "_initialDateTime" : ((2021, 1, 3), (0, 0)),

    "_apActive"        : True,
    "_wdActive"        : False,

    "_i2cActive"       : True,
    "_sda"             : 0,
    "_scl"             : 2,
    "_freq"            : 400000
}


"""
#   Protected variable settings in config.py
#
#   You can modify these configuration setting too.
#   But be aware, these are a bit more advanced than general ones.
#   So you need some knowledge / time / patience / ... ;-)


#   Button press configuration
#
#   The amount of time in millisecond = variable * timer interval (20 ms)
#   Note: The const() method accepts only integer numbers.

_pressLength = const(5)  # The button press is recognized only if it takes 100 ms or longer time.
_firstRepeat = const(25) # After the button press recognition this time (500 ms) must pass before you enter same command.


#   Initial datetime configuration

_initialDateTime = ((2021, 1, 2), (14, 30))     # Do not use leading zeros. Format: ((year, month, day), (hour, minute))

"""


## Config dictionary initialisation

config = {}

for key in configDefaults.keys():
    try:
        if missingConfig:
            config[key] = configDefaults.get(key)
        else:
            config[key] = eval("configPy." + key)
    except Exception as e:
        config[key] = configDefaults.get(key)


## Config dictionary validation

# If apEssid is an empty string, set to the default: uBot__xx:xx:xx (MAC address' last 3 octets )
if config.get("apEssid") == "":
    config["apEssid"] = configDefaults.get("apEssid")

# If apPassword is too short (less than 8 chars) or too long (more than 63 chars), set to the default.
length = len(config.get("apPassword"))
if  length < 8 or 63 < length:
    config["apPassword"] = configDefaults.get("apPassword")

# If replPassword is too short (less than 4 chars) or too long (more than 9 chars), set to the default.
length = len(config.get("replPassword"))
if  length < 4 or 9 < length:
    config["replPassword"] = configDefaults.get("replPassword")


## Filesystem initialisation

# Erase everything
try:
    recursiveRmdir("/")
except Exception as e:
    exceptions.append(e)


# Build folder structure
mkDir("etc")
mkDir("home")
mkDir("lib")
mkDir("tmp")
mkDir("etc/web")
mkDir("home/programs")
mkDir("tmp/programs")


# Save configDefaults dictionary to file
saveDictionaryToFile("configDefaults")


# Save config dictionary to file
saveDictionaryToFile("config")


# Save WebREPL's password from config dictionary to separate file
try:
    saveToFile("webrepl_cfg.py", "PASS = '{}'".format(configDefaults.get("replPassword")))
except Exception as e:
    exceptions.append(e)


# Save datetime from config dictionary to separate file
try:
    initDT   = config.get("_initialDateTime")
    datetime = (initDT[0][0], initDT[0][1], initDT[0][2], 0, initDT[1][0], initDT[1][1], 0, 0)
    saveToFile("etc/.datetime", datetime)
except Exception as e:
    exceptions.append(e)


# Create uBot driver files from the raw content which was copied from the end of this file to .setup
path   = ""
lines  = []

try:
    with open(".setup") as setup:
        for line in setup:
            if path != "":
                if line.startswith('"""'):
                    saveStringListToFile(path, lines)
                    path = ""
                    lines.clear()
                else:
                    lines.append(line)
            elif line.startswith('"""'):
                path = line[3:].strip()

    uos.remove(".setup")
except Exception as e:
    exceptions.append(e)



############
## AP

AP = network.WLAN(network.AP_IF)

AP.active(config.get("_apActive"))
AP.ifconfig(("192.168.11.1", "255.255.255.0", "192.168.11.1", "8.8.8.8"))
AP.config(authmode = network.AUTH_WPA_WPA2_PSK)

try:
    try:
        AP.config(essid = config.get("apEssid"))
    except Exception:
        AP.config(essid = configDefaults.get("apEssid"))
        exitNotes.append(
            "An error occur during setting apEssid ('{}'). Fallback to the default: '{}'".format(
                config.get("apEssid"), configDefaults.get("apEssid")
            )
        )
except Exception as e:
    exceptions.append(e)

try:
    try:
        AP.config(password = config.get("apPassword"))
    except Exception:
        AP.config(password = configDefaults.get("apPassword"))
        exitNotes.append(
            "An error occur during setting apPassword ('{}'). Fallback to the default: '{}'".format(
                config.get("apPassword"), configDefaults.get("apPassword")
            )
        )
except Exception as e:
    exceptions.append(e)



############
## FEEDBACK

# The setup process ignores:
#                             - the value of config.get("webRepl") and starts the WebREPL.
#                             - the value of config.get("webServer") and starts the webserver.
#                             - the value of config.get("uart"), so REPL is available on UART0:
#                                                                                                 TX: GPIO1, RX: GPIO3,
#                                                                                                 baudrate: 115200
# This is maybe helpful for the successful installing.

try:
    webrepl.start()
except Exception as e:
    exceptions.append(e)


try:
    socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    socket.bind(("", 80))
    socket.listen(5)
except Exception as e:
    exceptions.append(e)

try:
    if len(exceptions) == 0:
        feedbackLed.freq(1)
        feedbackLed.duty(1022)
    else:
        feedbackLed.freq(4)
        feedbackLed.duty(950)
except Exception as e:
    exceptions.append(e)


# Feedback page template
template =     ("<!DOCTYPE html><html><head><title>&micro;Bot setup report</title>"
                "<style>{}</style></head>"
                "<body><h1>{}</h1>{}<br><br><h3>Note:</h3>{}</body></html>")

style =        ("tr:nth-child(even) {background: #EEE}"
                ".exceptions col:nth-child(1) {width: 40px;}"
                ".exceptions col:nth-child(2) {width: 500px;}")

notes = "<ul>"
for n in exitNotes:
    message += "<li>{}</li>".format(n)
notes += "</ul>"

if len(exceptions) == 0:
    title   = "Successful installation"
    message = "Restart the robot and have fun! ;-)"
else:
    title   = "Exceptions"
    message = "<table class='exceptions'><colgroup><col><col></colgroup><tbody>"
    index = 0

    for e in exceptions:
        message += "<tr><td> {} </td><td> {} </td></tr>".format(index, e)
        index += 1

    message += "</tbody></table>"


# Handle HTTP GET requests, serve the feedback page
try:
    while True:
        connection, address = socket.accept()
        response = template.format(style, title, message, notes)

        connection.send("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n")
        connection.write(response)
        connection.close()
except Exception as e:
    exceptions.append(e)



########################################################################################################################
########################################################################################################################
# Content of files to create during setup
#
# Formatting rules:
#
# Comments should start at the beginning of the line with a hash mark.
# Only first and last line can begin with three quotation marks.
#
# First line: Three quotation marks + path with filename + LF.
#             Leading and trailing whitespaces will be omitted by strip().
#
# Last line: Only three quotation marks (and LF of course).



#                                                                                      This will replace setup's boot.py
"""                                                                                                              boot.py
def saveDateTime():
    try:
        with open("etc/.datetime", "w") as file:
            file.write(str(DT.datetime()) + "\n")
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))


def saveConfig():
    try:
        with open("etc/.config", "w") as file:

            for key in sorted([k for k in CONFIG.keys()]):
                value = CONFIG.get(key)
                if isinstance(value, str):
                    file.write("{} = '{}'\n".format(key, value))
                else:
                    file.write("{} = {}\n".format(key, value))
    except Exception as e:
        EXCEPTIONS.append(e)



###########
## IMPORTS

import esp, network, gc, ujson, uos, usocket, webrepl

from lib.buzzer  import Buzzer
from lib.motor   import Motor

from machine     import Pin, PWM, RTC, Timer, UART, WDT, reset
from micropython import const
from ubinascii   import hexlify
from uio         import FileIO
from utime       import sleep, sleep_ms, sleep_us
from sys         import print_exception

try:
    feedbackException = ""
    from lib.feedback import Feedback
except Exception as e:
    feedbackException = e


###########
## CONFIG

DT = RTC()

EXCEPTIONS = []
CONFIG     = {}

CONN  = ""
ADDR  = ""

COUNTER_POS  = 0
PRESSED_BTNS = []
COMMANDS     = []
EVALS        = []


try:
    with open("etc/.datetime") as file:
        DT.datetime(eval(file.readline().strip()))
except Exception as e:
    EXCEPTIONS.append((DT.datetime(), e))

START_DT = DT.datetime()

if feedbackException != "":
    EXCEPTIONS.append((DT.datetime(), feedbackException))

try:
    with open("etc/.config") as file:
        for line in file:
            sep = line.find("=")
            if -1 < sep:
                CONFIG[line[:sep].strip()] = eval(line[sep+1:].strip())
except Exception as e:
    EXCEPTIONS.append((DT.datetime(), e))



if CONFIG.get("_i2cActive"):
    try:
        F = Feedback(CONFIG.get("_freq"), Pin(CONFIG.get("_sda")), Pin(CONFIG.get("_scl")))
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))


###########
## GPIO

BUZZ = Buzzer(Pin(15), 262, 0, CONFIG.get("beepMode"))


if CONFIG.get("turtleHat"):
    CLK = Pin(13, Pin.OUT)  # GPIO pin. It is connected to the counter (CD4017) if physical switch CLOCK is on.
    INP = Pin(16, Pin.OUT)  # GPIO pin. Receives button presses from turtle HAT if physical switches: WAKE off, PULL down
                            # FUTURE: INP = Pin(16, Pin.IN)
    INP.off()               # DEPRECATED: New PCB design (2.1) will resolve this.
    INP.init(Pin.IN)        # DEPRECATED: New PCB design (2.1) will resolve this.
    CLK.off()
else:
    P13 = Pin(13, Pin.OUT)
    P16 = Pin(16, Pin.IN)   # MicroPython can not handle the pull-down resistor of the GPIO16: Use PULL physical switch.
    P13.off()


P12 = Pin(12, Pin.OUT)              # GPIO pin. On turtle HAT it can drive a LED if you switch physical switch on.
P14 = Pin(14, Pin.IN, Pin.PULL_UP)  # GPIO pin.
P12.off()


P4 = Pin(4, Pin.OUT)        # Connected to the 10th pin of the motor driver (SN754410). T1 terminal (M11, M14)
P5 = Pin(5, Pin.OUT)        # Connected to the 15th pin of the motor driver (SN754410). T1 terminal (M11, M14)
P4.off()
P5.off()

motorPins = [[P4, P5], [P4, P5]]

if not CONFIG.get("uart"):
    motorPins[0][0] = P1 = Pin(1, Pin.OUT) # Connected to the  2nd pin of the motor driver (SN754410). T0 terminal (M3, M6)
    motorPins[0][1] = P3 = Pin(3, Pin.OUT) # Connected to the  7th pin of the motor driver (SN754410). T0 terminal (M3, M6)
    P1.off()
    P3.off()

MOT = Motor(motorPins[0][0], motorPins[0][1], motorPins[1][0], motorPins[1][1])

if not CONFIG.get("_i2cActive"):
    P0 = Pin(0, Pin.IN)
    P2 = Pin(2, Pin.IN)


###########
## AP

AP = network.WLAN(network.AP_IF)

AP.active(CONFIG.get("_apActive"))
AP.ifconfig(("192.168.11.1", "255.255.255.0", "192.168.11.1", "8.8.8.8"))
AP.config(authmode = network.AUTH_WPA_WPA2_PSK)

try:
    AP.config(essid = CONFIG.get("apEssid"))
except Exception as e:
    EXCEPTIONS.append((DT.datetime(), e))

try:
    AP.config(password = CONFIG.get("apPassword"))
except Exception as e:
    EXCEPTIONS.append((DT.datetime(), e))


###########
## SOCKET

S = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
S.bind(("", 80))
S.listen(5)


###########
## GENERAL

gc.enable()
esp.osdebug(0)
esp.sleep_type(esp.SLEEP_NONE)

TIMER = Timer(-1)


if CONFIG.get("_wdActive"):
    WD = WDT()


# The REPL is attached by default to UART0, detach if not needed.
if not CONFIG.get("uart"):
    uos.dupterm(None, 1)

if CONFIG.get("webRepl"):
    try:
        webrepl.start()
    except Exception as e:
        EXCEPTIONS.append((DT.datetime(), e))
"""



#                                                                                           The main file of uBot driver
"""                                                                                                              main.py
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
    # Try to reply with a text/html or application/json
    # if the connection is alive, then closes it.

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
"""



#                                                                                     Motor feedback, "strategy pattern"
"""                                                                                                          feedback.py
from machine    import I2C
from lib.smbus  import SMBus
from lib.lsm303 import LSM303

class Feedback():

    def __init__(self, freq, SDA, SCL):
        self._I2C = I2C(freq=freq, sda=SDA, scl=SCL)
        self._MAP = self._I2C.scan()

        if 0 < len(self._MAP):
            self._LSM303 = LSM303(SMBus(freq=freq, sda=SDA, scl=SCL))

    def _test(self):
        if 0 < len(self._MAP):
            while True:
                accel_data = self._LSM303.read_accel()
                mag_data   = self._LSM303.read_mag()
                print(
                    [round(v, 2) for v in accel_data],
                    [round(v, 2) for v in mag_data]
                )
                sleep_ms(100)
"""



#                                                                   Extends PWM class to control the buzzer conveniently
"""                                                                                                        lib/buzzer.py
from machine import Pin, PWM
from utime   import sleep_ms, sleep_us

class Buzzer(PWM):

    def __init__(self, pin, freq, duty, beepMode):
        super().__init__(pin, freq, duty)
        self._pin = pin
        self._beepMode = beepMode

    def beep(self, freq = 262, duration = 3, pause = 10, count = 1):

        for i in range(count):
            self._pin.off()

            if self._beepMode:
                self.freq(freq)
                self.duty(512)

                rest = round((1000000 / freq) * (freq * duration / 10 ))
                sleep_us(rest)

                self.duty(0)
            else:
                self._pin.on()
                sleep_ms(duration * 100)
                self._pin.off()

            sleep_ms(pause * 10)


    def midiBeep(self, noteOn = 60, duration = 3, pause = 10, count = 1):
        f = round(440 * pow(2, (noteOn - 69) / 12))
        self.beep(f, duration, pause, count)
"""



#                                                                                                LSM303 controller class
"""                                                                                                        lib/lsm303.py
# lsm303-python by Jack Whittaker

# [https://github.com/jackw01/lsm303-python]


# MIT License

# Copyright (c) 2020 Jack

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# MODIFIED: imports
#import smbus
#import struct
from ustruct import unpack
#import time

# MODIFIED ALL: const()
# MODIFIED: 0x19 -> 0x18 ... because of the non-genuine chip maybe
LSM303_ADDRESS_ACCEL                      = const(0x18) # 0011000x

LSM303_REGISTER_ACCEL_CTRL_REG1_A         = const(0x20)
#LSM303_REGISTER_ACCEL_CTRL_REG2_A         = const(0x21)
#LSM303_REGISTER_ACCEL_CTRL_REG3_A         = const(0x22)
LSM303_REGISTER_ACCEL_CTRL_REG4_A         = const(0x23)
#LSM303_REGISTER_ACCEL_CTRL_REG5_A         = const(0x24)
#LSM303_REGISTER_ACCEL_CTRL_REG6_A         = const(0x25)
#LSM303_REGISTER_ACCEL_REFERENCE_A         = const(0x26)
#LSM303_REGISTER_ACCEL_STATUS_REG_A        = const(0x27)
LSM303_REGISTER_ACCEL_OUT_X_L_A           = const(0x28)
#LSM303_REGISTER_ACCEL_OUT_X_H_A           = const(0x29)
#LSM303_REGISTER_ACCEL_OUT_Y_L_A           = const(0x2A)
#LSM303_REGISTER_ACCEL_OUT_Y_H_A           = const(0x2B)
#LSM303_REGISTER_ACCEL_OUT_Z_L_A           = const(0x2C)
#LSM303_REGISTER_ACCEL_OUT_Z_H_A           = const(0x2D)
#LSM303_REGISTER_ACCEL_FIFO_CTRL_REG_A     = const(0x2E)
#LSM303_REGISTER_ACCEL_FIFO_SRC_REG_A      = const(0x2F)
#LSM303_REGISTER_ACCEL_INT1_CFG_A          = const(0x30)
#LSM303_REGISTER_ACCEL_INT1_SOURCE_A       = const(0x31)
#LSM303_REGISTER_ACCEL_INT1_THS_A          = const(0x32)
#LSM303_REGISTER_ACCEL_INT1_DURATION_A     = const(0x33)
#LSM303_REGISTER_ACCEL_INT2_CFG_A          = const(0x34)
#LSM303_REGISTER_ACCEL_INT2_SOURCE_A       = const(0x35)
#LSM303_REGISTER_ACCEL_INT2_THS_A          = const(0x36)
#LSM303_REGISTER_ACCEL_INT2_DURATION_A     = const(0x37)
#LSM303_REGISTER_ACCEL_CLICK_CFG_A         = const(0x38)
#LSM303_REGISTER_ACCEL_CLICK_SRC_A         = const(0x39)
#LSM303_REGISTER_ACCEL_CLICK_THS_A         = const(0x3A)
#LSM303_REGISTER_ACCEL_TIME_LIMIT_A        = const(0x3B)
#LSM303_REGISTER_ACCEL_TIME_LATENCY_A      = const(0x3C)
#LSM303_REGISTER_ACCEL_TIME_WINDOW_A       = const(0x3D)

LSM303_ADDRESS_MAG                        = const(0x1E) # 0011110x
LSM303_REGISTER_MAG_CRA_REG_M             = const(0x00)
LSM303_REGISTER_MAG_CRB_REG_M             = const(0x01)
LSM303_REGISTER_MAG_MR_REG_M              = const(0x02)
LSM303_REGISTER_MAG_OUT_X_H_M             = const(0x03)
#LSM303_REGISTER_MAG_OUT_X_L_M             = const(0x04)
#LSM303_REGISTER_MAG_OUT_Z_H_M             = const(0x05)
#LSM303_REGISTER_MAG_OUT_Z_L_M             = const(0x06)
#LSM303_REGISTER_MAG_OUT_Y_H_M             = const(0x07)
#LSM303_REGISTER_MAG_OUT_Y_L_M             = const(0x08)
#LSM303_REGISTER_MAG_SR_REG_Mg             = const(0x09)
#LSM303_REGISTER_MAG_IRA_REG_M             = const(0x0A)
#LSM303_REGISTER_MAG_IRB_REG_M             = const(0x0B)
#LSM303_REGISTER_MAG_IRC_REG_M             = const(0x0C)
#LSM303_REGISTER_MAG_TEMP_OUT_H_M          = const(0x31)
#LSM303_REGISTER_MAG_TEMP_OUT_L_M          = const(0x32)

MAG_GAIN_1_3                              = const(0x20) # +/- 1.3
#MAG_GAIN_1_9                              = const(0x40) # +/- 1.9
#MAG_GAIN_2_5                              = const(0x60) # +/- 2.5
#MAG_GAIN_4_0                              = const(0x80) # +/- 4.0
#MAG_GAIN_4_7                              = const(0xA0) # +/- 4.7
#MAG_GAIN_5_6                              = const(0xC0) # +/- 5.6
#MAG_GAIN_8_1                              = const(0xE0) # +/- 8.1

#MAG_RATE_0_7                              = const(0x00) # 0.75 H
#MAG_RATE_1_5                              = const(0x01) # 1.5 Hz
#MAG_RATE_3_0                              = const(0x62) # 3.0 Hz
#MAG_RATE_7_5                              = const(0x03) # 7.5 Hz
#MAG_RATE_15                               = const(0x04) # 15 Hz
#MAG_RATE_30                               = const(0x05) # 30 Hz
#MAG_RATE_75                               = const(0x06) # 75 Hz
#MAG_RATE_220                              = const(0x07) # 210 Hz

ACCEL_MS2_PER_LSB = 0.00980665 # meters/second^2 per least significant bit

GAUSS_TO_MICROTESLA = 100.0

class LSM303(object):
    "LSM303 3-axis accelerometer/magnetometer"

    def __init__(self, i2c, hires=True):
        "Initialize the sensor"
        self._bus = i2c

        # Enable the accelerometer - all 3 channels
        self._bus.write_i2c_block_data(LSM303_ADDRESS_ACCEL,
                                       LSM303_REGISTER_ACCEL_CTRL_REG1_A,
                                       [0b01000111])

        # Select hi-res (12-bit) or low-res (10-bit) output mode.
        # Low-res mode uses less power and sustains a higher update rate,
        # output is padded to compatible 12-bit units.
        if hires:
            self._bus.write_i2c_block_data(LSM303_ADDRESS_ACCEL,
                                           LSM303_REGISTER_ACCEL_CTRL_REG4_A,
                                           [0b00001000])
        else:
            self._bus.write_i2c_block_data(LSM303_ADDRESS_ACCEL,
                                           LSM303_REGISTER_ACCEL_CTRL_REG4_A,
                                           [0b00000000])

        # Enable the magnetometer
        self._bus.write_i2c_block_data(LSM303_ADDRESS_MAG,
                                       LSM303_REGISTER_MAG_MR_REG_M,
                                       [0b00000000])

        self.set_mag_gain(MAG_GAIN_1_3)

    def read_accel(self):
        "Read raw acceleration in meters/second squared"
        # Read as signed 12-bit little endian values
        accel_bytes = self._bus.read_i2c_block_data(LSM303_ADDRESS_ACCEL,
                                                    LSM303_REGISTER_ACCEL_OUT_X_L_A | 0x80,
                                                    6)
        # MODIFIED : struct.unpack -> method import + unpack()
        accel_raw = unpack('<hhh', bytearray(accel_bytes))

        return (
            (accel_raw[0] >> 4) * ACCEL_MS2_PER_LSB,
            (accel_raw[1] >> 4) * ACCEL_MS2_PER_LSB,
            (accel_raw[2] >> 4) * ACCEL_MS2_PER_LSB,
        )

    def set_mag_gain(self, gain):
        "Set magnetometer gain"
        self._gain = gain
        if gain == MAG_GAIN_1_3:
            self._lsb_per_gauss_xy = 1100
            self._lsb_per_gauss_z = 980
#        elif gain == MAG_GAIN_1_9:
#            self._lsb_per_gauss_xy = 855
#            self._lsb_per_gauss_z = 760
#        elif gain == MAG_GAIN_2_5:
#            self._lsb_per_gauss_xy = 670
#            self._lsb_per_gauss_z = 600
#        elif gain == MAG_GAIN_4_0:
#            self._lsb_per_gauss_xy = 450
#            self._lsb_per_gauss_z = 400
#        elif gain == MAG_GAIN_4_7:
#            self._lsb_per_gauss_xy = 400
#            self._lsb_per_gauss_z = 355
#        elif gain == MAG_GAIN_5_6:
#            self._lsb_per_gauss_xy = 330
#            self._lsb_per_gauss_z = 295
#        elif gain == MAG_GAIN_8_1:
#            self._lsb_per_gauss_xy = 230
#            self._lsb_per_gauss_z = 205

        self._bus.write_i2c_block_data(LSM303_ADDRESS_MAG,
                                       LSM303_REGISTER_MAG_CRB_REG_M,
                                       [self._gain])

    def set_mag_rate(self, rate):
        "Set magnetometer rate"
        self._bus.write_i2c_block_data(LSM303_ADDRESS_MAG,
                                       LSM303_REGISTER_MAG_CRA_REG_M,
                                       [(rate & 0x07) << 2])

    def read_mag(self):
        "Read raw magnetic field in microtesla"
        # Read as signed 16-bit big endian values
        mag_bytes = self._bus.read_i2c_block_data(LSM303_ADDRESS_MAG,
                                                  LSM303_REGISTER_MAG_OUT_X_H_M,
                                                  6)
        # MODIFIED : struct.unpack -> method import + unpack()
        mag_raw = unpack('>hhh', bytearray(mag_bytes))

        return (
            mag_raw[0] / self._lsb_per_gauss_xy * GAUSS_TO_MICROTESLA,
            mag_raw[2] / self._lsb_per_gauss_xy * GAUSS_TO_MICROTESLA,
            mag_raw[1] / self._lsb_per_gauss_z * GAUSS_TO_MICROTESLA,
        )

# MODIFIED: excluded method _test()
"""



#                                                                               Motor controlling, now it's a bit simple
"""                                                                                                         lib/motor.py
from machine import Pin
from utime   import sleep_ms

class Motor():

    def __init__(self, m3, m6, m11, m14):
        self._mot = [[m3, m6], [m11, m14]]

    def _setMotor(self, motor = 0, mode = 0):
        # Low-level motor setter

        # motor : integer parameter
        # 0     : (M3, M6)   T0 terminal / RIGHT MOTOR
        # 1     : (M11, M14) T1 terminal / LEFT MOTOR

        # mode  : integer parameter
        # 0     : (off, off)  -> STOP
        # 1     : (on, off)   -> FORWARD
        # 2     : (off, on)   -> BACKWARD

        if mode == 0:
            self._mot[motor][0].off()
            self._mot[motor][1].off()
        else:
            self._mot[motor][1 - mode].on()
            self._mot[motor][abs(mode - 2)].off()


    def _setController(self, modeRight, modeLeft):
            self._setMotor(0, modeRight)
            self._setMotor(1, modeLeft)


    def move(self, direction = 0, duration = 1000):

        if direction == 1:              # FORWARD
            self._setController(1, 1)
        elif direction == 2:            # RIGHT
            self._setController(1, 2)
        elif direction == 3:            # LEFT
            self._setController(2, 1)
        elif direction == 4:            # BACKWARD
            self._setController(2, 2)

        if direction != 0:
            sleep_ms(duration)
            self._setController(0, 0)
"""



#                                                                                     SMBus for the sake of LSM303 class
"""                                                                                                         lib/smbus.py
# micropython-smbus by Geoff Lee

# [https://github.com/gkluoe/micropython-smbus]


# MIT License

# Copyright (c) 2017 Geoff Lee

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


try:
    from machine import I2C
except ImportError:
    raise ImportError("Can't find the micropython machine.I2C class: "
                      "perhaps you don't need this adapter?")


class SMBus(I2C):
    # Provides an 'SMBus' module which supports some of the py-smbus
    # i2c methods, as well as being a subclass of machine.I2C
    # Hopefully this will allow you to run code that was targeted at
    # py-smbus unmodified on micropython.
	# Use it like you would the machine.I2C class:
    #     import usmbus.SMBus
    #     bus = SMBus(1, pins=('G15','G10'), baudrate=100000)
    #     bus.read_byte_data(addr, register)
    #     ... etc

    def read_byte_data(self, addr, register):
        # Read a single byte from register of device at addr
        # Returns a single byte
        return self.readfrom_mem(addr, register, 1)[0]

    def read_i2c_block_data(self, addr, register, length):
        # Read a block of length from register of device at addr
        # Returns a bytes object filled with whatever was read
        return self.readfrom_mem(addr, register, length)

    def write_byte_data(self, addr, register, data):
        # Write a single byte from buffer `data` to register of device at addr
        # Returns None
        # writeto_mem() expects something it can treat as a buffer
        if isinstance(data, int):
            data = bytes([data])
        # ADDED: for the compatibility with lsm303-python
        else:
            data = bytearray([data[0]])
        return self.writeto_mem(addr, register, data)

    def write_i2c_block_data(self, addr, register, data):
        # Write multiple bytes of data to register of device at addr
        # Returns None
        # writeto_mem() expects something it can treat as a buffer
        if isinstance(data, int):
            data = bytes([data])
        # ADDED: for the compatibility with lsm303-python
        else:
            data = bytearray([data[0]])
        return self.writeto_mem(addr, register, data)

    # The follwing haven't been implemented, but could be.
    def read_byte(self, *args, **kwargs):
        # Not yet implemented
        raise RuntimeError("Not yet implemented")

    def write_byte(self, *args, **kwargs):
        # Not yet implemented
        raise RuntimeError("Not yet implemented")

    def read_word_data(self, *args, **kwargs):
        # Not yet implemented
        raise RuntimeError("Not yet implemented")

    def write_word_data(self, *args, **kwargs):
        # Not yet implemented
        raise RuntimeError("Not yet implemented")
"""



#                                                                                                     General stylesheet
"""                                                                                                    etc/web/style.css
tr:nth-child(even) {background: #EEE}
.exceptions col:nth-child(1) {width: 40px;}
.exceptions col:nth-child(2) {width: 500px;}
"""



#                                                                                       Website with general debug infos
"""                                                                                                   etc/web/stats.html
<table>
    <tr>
		<td>Method: </td><td>{method}</td>
	</tr>
	<tr>
		<td>Path: </td><td>{path}</td>
	</tr>
	<tr>
		<td>Length: </td><td>{length}</td>
	</tr>
	<tr>
		<td>Type: </td><td>{type}</td>
	</tr>
	<tr>
		<td>Body: </td><td>{body}</td>
	</tr>
</table>
<br><br>
<table>
    <tr>
		<td>Memory: </td><td>{freePercent}% free ({freeMem}/{allMem})</td>
	</tr>
    <tr>
		<td>Pressed: </td><td>{pressed}</td>
	</tr>
    <tr>
		<td>Commands: </td><td>{commands}</td>
	</tr>
    <tr>
		<td>Evals: </td><td>{evals}</td>
	</tr>
</table>
<br><br><hr><hr>
<h3>Exceptions</h3>
{exceptions}
"""

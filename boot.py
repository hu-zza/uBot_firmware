############
## IMPORTS

exceptions = []

try:
    import network, gc, uos, usocket, webrepl

    from machine        import Pin, PWM
    from sys            import print_exception
    from ubinascii      import hexlify
except Exception as e:
    exceptions.append(e)


try:
    import config
except Exception as e:
    exceptions.append(e)



############
## METHODS

def recursiveRmdir(dirName):

    uos.chdir(dirName)

    for file in uos.listdir():
        type = "{0:07o}".format(uos.stat(file)[0])[:3]  # uos.stat(file)[0] -> ST_MODE

        if type == "010":                               # S_IFREG    0100000   regular file
            uos.remove(file)
        elif type == "004":                             # S_IFDIR    0040000   directory
            if len(uos.listdir(file)) == 0:
                uos.rmdir(file)
            else:
                recursiveRmdir(file)

    if dirName != "/":
        uos.chdir("..")
        uos.rmdir(dirName)



############
## CONFIG

# Start feedbackLed
try:
    feedbackLed = PWM(Pin(2), 15, 1010)
except Exception as e:
    exceptions.append(e)

# Enable automatic garbage collection.
try:
    gc.enable()
except Exception as e:
    exceptions.append(e)


configDefaults = {

    # General settings, indicated in config.py too.

    "apEssid"         : "",
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

    "_initialDateTime" : ((2021, 1, 2), (0, 0)),

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
        config[key] = eval("config." + key)
    except Exception as e:
        config[key] = configDefaults.get(key)


## Config dictionary validation

# If apEssid is an empty string, generate the default: uBot__xx:xx:xx (MAC address' last 3 octets )
if config.get("apEssid") == "":
    config["apEssid"] = "uBot__" + hexlify(network.WLAN().config('mac'), ':').decode()[9:]

# If apPassword is too short (less than 8 chars) or too long (more than 63 chars), set to default.
length = len(config.get("apPassword"))
if  length < 8 or 63 < length:
    config["apPassword"] = configDefaults.get("apPassword")

# If replPassword is too short (less than 4 chars) or too long (more than 9 chars), set to default.
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
try:
    uos.mkdir("etc")
    uos.mkdir("home")
    uos.mkdir("lib")
    uos.mkdir("tmp")
    uos.mkdir("etc/web")
    uos.mkdir("home/programs")
    uos.mkdir("tmp/programs")
except Exception as e:
    exceptions.append(e)


# Save WebREPL's password from config dictionary to separate file
try:
    with open("webrepl_cfg.py", "w") as file:
        file.write("PASS = '{}'\n".format(configDefaults.get("replPassword")))
except Exception as e:
    exceptions.append(e)


# Save datetime from config dictionary to separate file
try:
    initDT   = config.get("_initialDateTime")
    datetime = (initDT[0][0], initDT[0][1], initDT[0][2], 0, initDT[1][0], initDT[1][1], 0, 0)

    with open("etc/.datetime", "w") as file:
        file.write(str(datetime) + "\n")
except Exception as e:
    exceptions.append(e)


# Save config dictionary to file
try:
    with open("etc/.config", "w") as file:
        for key, value in config.items():
            # Exclude transients
            if key[0] != "_":
                if isinstance(value, str):
                    file.write("{} = '{}'\n".format(key, value))
                else:
                    file.write("{} = {}\n".format(key, value))
except Exception as e:
    exceptions.append(e)


# Save stylesheet
try:
    with open("etc/web/style.css", "w") as file:
        file.write( """
                    tr:nth-child(even) {background: #EEE}
                    .exceptions col:nth-child(1) {width: 40px;}
                    .exceptions col:nth-child(2) {width: 500px;}
                    """)
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
except Exception as e:
    exceptions.append(e)

try:
    try:
        AP.config(password = config.get("apPassword"))
    except Exception:
        AP.config(password = configDefaults.get("apPassword"))
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
template =  """
            <!DOCTYPE html>
            <html>
                <head>
                    <title>
                        μBot setup report
                    </title>
                    <link rel='stylesheet' href='/etc/web/style.css'>
                </head>
                <body>
                    <h1>{}</h1>
                    {}
                </body>
            </html>
            """


if len(exceptions) == 0:
    title = "Successful installation"
    exceptionList = ""
else:
    title = "Exceptions"
    exceptionList = """
                    <table class='exceptions'>
                        <colgroup><col><col></colgroup>
                        <tbody>
                    """
    index = 0

    for e in exceptions:
        exceptionList += """        <tr><td> {} </td><td> {} </td></tr>""".format(index, e)
        index += 1

    exceptionList += """
                        </tbody>
                    </table>
                    """

# Handle HTTP GET requests, serve the feedback page
try:
    while True:
        connection, address = socket.accept()
        response = template.format(title, exceptionList)

        connection.send("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n")
        connection.send(response)
        connection.close()
except Exception as e:
    exceptions.append(e)

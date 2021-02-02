import esp, network, uos, webrepl

from machine     import Pin, UART
from ubinascii   import hexlify
from utime       import sleep_ms

import ubot_config    as config
import ubot_logger    as logger
import ubot_buzzer    as buzzer

buzzer.keyBeep("started")

if config.get("feedback", "active"):
    import ubot_feedback  as feedback

if config.get("motor", "active"):
    import ubot_motor as motor

if config.get("turtle", "active"):
    import ubot_turtle as turtle

if config.get("webServer", "active"):
    import ubot_webserver as webserver



################################
## PUBLIC METHODS

def executeJson(json):
    if json.get("logging"):
        logger.append("Incoming JSON object. Title: {}".format(json.get("title")))
        logger.append(json)

    results = []

    if json.get("dateTime"):
        dateTime = json.get("dateTime")

        if len(dateTime) == 8:              # For classical tuple format
            config.datetime(dateTime)
        elif len(dateTime) == 2:            # For human readable format: (yyyy-mm-dd, hh:mm)
            date = dateTime[0].split("-")
            time = dateTime[1].split(":")
            config.datetime((int(date[0]), int(date[1]), int(date[2]), 0, int(time[0]), int(time[1]), 0, 0))

        results.append("New date and time has been set.")


    if json.get("command"):
        for command in json.get("command"):

            if command[:6] == "PRESS ":
                pressedList = command[6:].strip().split(":")
                for pressed in pressedList:
                    turtle.press(pressed)

            elif command[:5] == "STEP ":
                for char in command[5:].strip():
                    turtle.move(char)

            elif command[:5] == "BEEP ":
                beepArray = command[5:].strip().split(":")
                buzzer.beep(int(beepArray[0]), int(beepArray[1]), int(beepArray[2]), int(beepArray[3]))

            elif command[:5] == "MIDI ":
                beepArray = command[5:].strip().split(":")
                buzzer.midiBeep(int(beepArray[0]), int(beepArray[1]), int(beepArray[2]), int(beepArray[3]))

            elif command[:5] == "REST ":
                buzzer.rest(int(command[5:].strip()))

            elif command[:4] == "MOT ":
                motor.move(int(command[4]), int(command[6:].strip()))

            elif command[:6] == "SLEEP ":
                sleep_ms(int(command[6:].strip()))


    if json.get("program"):
        program = json.get("program")

        if program.get("function") == "LIST":
            if program.get("directory"):
                results.append(turtle.listPrograms(program.get("directory")))

        elif program.get("function") == "LOAD":
            if program.get("content"):
                turtle.loadProgram(program.get("content"))
                results.append("Program loaded successfully.")
            elif program.get("name") and program.get("directory"):
                turtle.loadProgramFromRom(program.get("name"), program.get("directory"))
                results.append("Program loaded successfully.")

        elif program.get("function") == "SAVE":
            if program.get("content"):
                if program.get("title"):
                    turtle.saveProgram(program.get("title"), program.get("content"))    # Saves the received program to /program/json/<title>
                    results.append("Program saved successfully.")
            else:                                                                       # Turtle style save: If title is set, it's named
                turtle.saveProgram(program.get("title"))                                # and saved in /program/json/<title>, otherwise acts
                results.append("Program saved successfully.")                           # like ADD button: /program/turtle/XXXXXXXXXX_YYY.txt

        if program.get("play"):
            turtle.press(64)


    if json.get("file"):
        if json.get("function") == "list":
            pass


    if json.get("service"):
            for command in json.get("service"):
                if command == "START UART":
                    config.set("uart", "active", True)
                    uos.dupterm(UART(0, 115200), 1)
                    results.append("UART has started.")

                elif command == "STOP UART":
                    config.set("uart", "active", False)
                    uos.dupterm(None, 1)
                    results.append("UART has stopped.")

                elif command == "START WEBREPL":
                    config.set("webRepl", "active", True)
                    webrepl.start()
                    results.append("WebREPL has started.")

                elif command == "STOP WEBREPL":
                    config.set("webRepl", "active", False)
                    webrepl.stop()
                    results.append("WebREPL has stopped.")

                elif command == "STOP WEBSERVER":
                    webserver.stop("WebServer has stopped.")

                elif command == "CALIBRATE FEEDBACK":
                    results.append("Calibration has started.")

                elif command == "CHECK DATETIME":
                    results.append(str(config.datetime()))


    if json.get("root"):
            for command in json.get("root"):

                if command[0:5] == "EXEC ":
                    exec(command[5:])
                    results.append("'{}' executed successfully.".format(command[5:]))

                elif command[0:5] == "EVAL ":
                    results.append("'{}' executed successfully, the result is: '{}'".format(command[5:], eval(command[5:])))


    if len(results) == 0:
        results = ["Processing has completed without any return value."]
    elif json.get("logging"):
        logger.append(results)

    return results



################################
## INITIALISATION

esp.osdebug(None)
esp.sleep_type(esp.SLEEP_NONE)


###########
## GPIO

if not config.get("turtle", "active"):
    P13 = Pin(13, Pin.OUT)
    P16 = Pin(16, Pin.IN)   # MicroPython can not handle the pull-down resistor of the GPIO16: Use PULL physical switch.
    P13.off()


P12 = Pin(12, Pin.OUT)              # GPIO pin. On μBot turtle it can drive a LED if you switch physical switch on.
P14 = Pin(14, Pin.IN, Pin.PULL_UP)  # GPIO pin.
P12.off()


if not config.get("i2c", "active"):
    P0 = Pin(0, Pin.IN)
    P2 = Pin(2, Pin.IN)


if config.get("motor", "active"):
    motor.config(
        (
            (0, 0) if config.get("uart", "active") else (1, 3), # Right motor - T0
            (4, 5)                                              # Left motor  - T1
        ),
        (
            (config.get("motor", "T0Period"),       config.get("motor", "T0Duration")),
            (config.get("motor", "T1Frequency"),    config.get("motor", "T1Duty")),
            (config.get("motor", "T1DutyFactor"),   config.get("motor", "T1MinDuty"), config.get("motor", "T1MaxDuty")),
             config.get("motor", "breathLength")
        )
    )

if config.get("turtle", "active"):
    motor.setBreath(config.get("turtle", "breathLength"))

###########
## AP

AP = network.WLAN(network.AP_IF)

AP.active(config.get("ap", "active"))
AP.ifconfig(("192.168.11.1", "255.255.255.0", "192.168.11.1", "8.8.8.8"))
AP.config(authmode = network.AUTH_WPA_WPA2_PSK)


try:
    AP.config(essid = config.get("ap", "essid"))
except Exception as e:
    logger.append(e)


try:
    AP.config(password = config.get("ap", "password"))
except Exception as e:
    logger.append(e)


###########
## GENERAL

if config.get("feedback", "active"):
    uos.dupterm(None, 1)                # The REPL is attached by default to UART0, detach if feedback is active.
    feedback.start()

    if config.get("uart", "active"):    # Prevent racing condition: Feedback has got the priority
        config.set("uart", "active", False)


if not config.get("uart", "active"):   # The REPL is attached by default to UART0, detach if it is not active.
    uos.dupterm(None, 1)


if config.get("webRepl", "active"):
    try:
        webrepl.start()
    except Exception as e:
        logger.append(e)


buzzer.keyBeep("ready")                 # After that point the main loop begins: webserver / <no alternative yet...>


if config.get("webServer", "active"):
    try:
        webserver.setJsonCallback(executeJson)
        webserver.start()
    except Exception as e:
        logger.append(e)

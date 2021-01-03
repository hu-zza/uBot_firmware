apEssid      = ""  # Set the WiFi (access point) name.          For example: apEssid = "uBot_01"
apPassword   = ""  # Set the WiFi (access point) password.      For example: apPassword = "uBot_pwd"      (8 - 63 chars)
replPassword = ""  # Set the WebREPL password.                  For example: replPassword = "uBot_REPL"   (4 - 9  chars)

########################################################################################################################
########################################################################################################################

uart      = False   # Enables the UART0                                           TX: GPIO1, RX: GPIO3, baudrate: 115200
webRepl   = True    # Enables the WebREPL on 192.168.11.1:8266         More info: https://github.com/micropython/webrepl
webServer = True    # Enables the HTTP request processing.      Needed for remote controll: app / webpage (192.168.11.1)
turtleHat = True    # Enables the turtle HAT by allocating GPIO pins to it and starting timer to map button presses.

"""
beepMode

If it's True enables the feedback beeps: The by oscillating GPIO 15 signal at LED blinks.
If it's False the feedback is a simple on-off cycle: The LED blinks normally, but the buzzer only ticks once.
You can mute the μBot by the switch 'BUZZER' (on the main PCB) too. The two switches are independent from each other.
"""
beepMode  = True

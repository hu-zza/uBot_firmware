essid = ""  # Set the WiFi name in the quotation marks.     For example: essid = "uBot_01"
passw = ""  # Set the WiFi password in the quotation marks. For example: passw = "uBot_01_pwd"

########################################################################################################################
########################################################################################################################

uart      = True    # Enables the UART0                                           TX: GPIO1, RX: GPIO3, baudrate: 115200
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


"""
The amount of time in millisecond = variable * timer interval (2) * channels count (10)

Note: The const() method accepts only integer numbers.
"""
pressLength = const(5)  # The button press is recognized only if it takes 100 ms or longer time.
firstRepeat = const(25) # After the button press recognition this time (500 ms) must pass before you enter same command.

ESSID = ""  # Set the WiFi name in the quotation marks.     For example: ESSID = "uBot_01"
PASSW = ""  # Set the WiFi password in the quotation marks. For example: PASSW = "uBot_01_pwd"

UART0      = True
WEB_REPL   = False
WEB_SERVER = True
BEEP_MODE  = True
                            # The amount of time in millisecond = variable * timer interval (2) * channels count (10)
PRESS_LENGTH = const(5)     # The button press is recognized only if it takes 100 ms or longer time.
FIRST_REPEAT = const(25)    # After the button press recognition this time (500 ms) must pass before you enter same command.

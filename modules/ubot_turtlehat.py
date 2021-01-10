from machine import Pin, Timer
from ubot_buzzer import Buzzer

_clockPin         = 0
_inputPin         = 0
_counterPosition  = 0
_pressLength      = 0
_maxError         = 0

_lastPressed      = 0
_firstRepeat      = 0

_pressedListIndex = 0
_pressedList      = 0
_pressedButtons   = 0

_timer            = 0
_buzzer           = 0


def _advanceCounter():
    global _counterPosition

    _clockPin.on()

    if 9 <= _counterPosition:
        _counterPosition = 0
    else:
        _counterPosition += 1

    _clockPin.off()


def _getPressedButton():
    global _pressedList
    global _pressedListIndex

    pressed = 0

    for i in range(10):
        # pseudo pull-down                 # DEPRECATED: New PCB design (2.1) will resolve this.
        if _inputPin.value() == 1:         # DEPRECATED: New PCB design (2.1) will resolve this.
            _inputPin.init(Pin.OUT)        # DEPRECATED: New PCB design (2.1) will resolve this.
            _inputPin.off()                # DEPRECATED: New PCB design (2.1) will resolve this.
            _inputPin.init(Pin.IN)         # DEPRECATED: New PCB design (2.1) will resolve this.

        if _inputPin.value() == 1:
            pressed += pow(2, _counterPosition)

        _advanceCounter()

    # shift counter's "resting position" to the closest pressed button to eliminate BTN LED flashing
    if 0 < pressed:
        while bin(1024 + pressed)[12 - _counterPosition] != "1":
            _advanceCounter()

    _pressedList[_pressedListIndex] = pressed
    _pressedListIndex += 1
    if len(_pressedList) <= _pressedListIndex:
            _pressedListIndex = 0

    errorCount = 0

    for i in range(len(_pressedList)):
        count = _pressedList.count(_pressedList[i])

        if _pressLength <= count:
            return _pressedList[i]

        errorCount += count
        if _maxError < errorCount:
            return 0


def _saveCommand():
    global _lastPressed

    try:
        pressed = _getPressedButton()

        if pressed == _lastPressed[0]:
            _lastPressed[1] += 1
        else:
            _lastPressed = [pressed, 1]

        if 0 < pressed and (_lastPressed[1] == 1 or _firstRepeat < _lastPressed[1]):
            _pressedButtons.append(pressed)
            _lastPressed[1] = 1
            _buzzer.midiBeep(64)
    except Exception as e:
        print(e)


def config(config, pressedButtons, buzzer):

    global _clockPin
    global _inputPin
    global _counterPosition
    global _pressLength
    global _maxError
    global _lastPressed
    global _firstRepeat
    global _pressedListIndex
    global _pressedList
    global _pressedButtons
    global _timer
    global _buzzer          

    _clockPin = Pin(config.get("turtleClockPin"), Pin.OUT)
    _clockPin.off()

    _inputPin = Pin(config.get("turtleInputPin"), Pin.OUT) # FUTURE: Pin(16, Pin.IN)
    _inputPin.off()                                        # DEPRECATED: New PCB design (2.1) will resolve this.
    _inputPin.init(Pin.IN)                                 # DEPRECATED: New PCB design (2.1) will resolve this.

    _counterPosition  = config.get("turtleCounterPos")
    _pressLength      = config.get("turtlePressLength")
    _maxError         = config.get("turtleMaxError")

    _lastPressed      = [0, 0]                             # [pressed button, elapsed (button check) cycles]
    _firstRepeat      = config.get("turtleFirstRepeat")

    _pressedListIndex = 0
    _pressedList      = [0] * (_pressLength + _maxError)
    _pressedButtons   = pressedButtons

    _timer            = Timer(-1)
    _buzzer           = buzzer

    _timer.init(period = config.get("turtleCheckPeriod"), mode = Timer.PERIODIC, callback = lambda t:_saveCommand())

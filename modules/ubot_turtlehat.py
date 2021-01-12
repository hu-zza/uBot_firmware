import sys
from machine import Pin, Timer
from ubot_buzzer import Buzzer

_clockPin         = 0           # [need config()] Advances the decade counter (U3).
_inputPin         = 0           # [need config()] Checks the returning signal from turtle HAT.
_counterPosition  = 0           #                 The position of the decade counter (U3).
_pressLength      = 0           # [need config()]
_maxError         = 0           # [need config()]

_lastPressed      = [0, 0]      #                 Inside: [last pressed button, elapsed (button check) cycles]
_firstRepeat      = 0           # [need config()]
_loopChecking     = 0           # [need config()]

_pressedListIndex = 0
_pressedList      = 0           # [need config()] Low-level:  The last N (_pressLength + _maxError) buttoncheck results.
_commandArray     = bytearray() #                 High-level: Abstract commands, result of processed button presses.
_commandPointer   = 0           #                 Pointer for _commandArray.
_programArray     = bytearray() #                 High-level: Result of one or more added _commandArray.
_programPointer   = 0           #                 Pointer for _programArray.
_programParts     = bytearray() #                 Positions by which _programArray can be split into _commandArray(s).

_loopInputMode    = False       #                 Special input mode for declaring a loop.
_loopCounterInput = False       #                 Special input mode for declaring the counter of the loop.
_loopCounter      = 0

_midiInputMode    = False       #                 Special input mode for declaring a MIDI tune.

_timer            = Timer(-1)   #                 Executes the repeated button checks.
_buzzer           = 0           # [need config()] Buzzer object for feedback.


def _addToCommandArray(command):
    global _commandArray
    global _commandPointer

    if _commandPointer < len(_commandArray):
        _commandArray[_commandPointer] = command
    else:
        _commandArray.append(command)

    _commandPointer += 1


def _undoCommand():
    global _commandPointer
    global _programPointer                    # I think this will be needed, if pass @ 55 became something useful... :-)

    if 0 < _commandPointer:
        _commandPointer -= 1
    else:
        if 0 < _programPointer:
            for i in range(12):
                _buzzer.midiBeep(60 + i, 100, 0, 1)
            pass  # Move last added _commandArray from _programArray to _commandArray variable, etc...
        else:
            _buzzer.midiBeep(60, 500, 150, 3)



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


def _getValidatedPressedButton():
    global _lastPressed

    pressed = _getPressedButton()

    if pressed == _lastPressed[0]:
        _lastPressed[1] += 1
    else:
        _lastPressed = [pressed, 1]

    if _lastPressed[1] == 1 or _firstRepeat < _lastPressed[1]:    # Lack of pressing returns same like a button press.
        _lastPressed[1] = 1                                       # In this case the returning value is 0.
        return pressed
    else:
        return 0                                                 # If validation is in progress, returns 0.


def _processingGeneralInput(pressed):
    global _loopInputMode

    if pressed == 1:                # FORWARD
        return 1
    elif pressed == 2:              # PAUSE
        return 9
    elif pressed == 4:              # REPEAT
        _loopInputMode = True
        _buzzer.setDefaultState(1)
        return 10
    elif pressed == 6:              # F1
        return 0
    elif pressed == 8:              # ADD
        return 0
    elif pressed == 10:             # F2
        return 0
    elif pressed == 12:             # F3
        return 0
    elif pressed == 16:             # RIGHT
        return 4
    elif pressed == 32:             # BACKWARD
        return 2
    elif pressed == 64:             # START / STOP
        return 0
    elif pressed == 128:            # LEFT
        return 3
    elif pressed == 256:            # UNDO
        if not _loopCounterInput:
            _undoCommand()
            if _commandArray[_commandPointer] == 10:
                _loopInputMode = False
                _buzzer.setDefaultState(0)
                _buzzer.midiBeep(71, 100, 25, 3)
                _buzzer.midiBeep(60, 500, 100, 1)
            else:
                _buzzer.midiBeep(71, 100, 25, 2)
        return 0
    elif pressed == 512:            # DELETE a.k.a. 'X'
        return 0
    elif pressed == 1023:           # USER                                              CAUSE OF THE HEAT?! TEST NEEDED!
        return 0
    else:
        return 0


def _modifyLoopCounter(value = 1):
    global _loopCounter

    if _loopCounter + value < 1:                    # Checks lower boundary.
        _loopCounter = 1
        _buzzer.midiBeep(60, 500, 150, 3)
    elif 255 < _loopCounter + value:                # Checks upper boundary.
        _loopCounter = 255
        _buzzer.midiBeep(60, 500, 150, 3)
    elif value == 0:                                # Reset the counter. Use case: forget the exact count and press 'X'.
        _loopCounter = 0
        _buzzer.midiBeep(71, 100, 25, 3)
        _buzzer.midiBeep(60, 500, 100, 1)
    else:                                           # General modification.
        _loopCounter += value
        _buzzer.midiBeep(71, 100, 0, 1)


def _checkLoopCounter():
    global _loopChecking

    if _loopChecking == 1:
        if _loopCounter <= 20:
            _buzzer.midiBeep(64, 100, 400, _loopCounter)
        else:
            _buzzer.midiBeep(64, 1500, 100, 2)
    elif _loopChecking == 2:
        _buzzer.midiBeep(64, 100, 400, _loopCounter)


def _processingLoopInput(pressed):
    global _loopInputMode
    global _loopCounterInput

    if _loopCounterInput:
        if pressed == 4:                # REPEAT
            _loopInputMode    = False
            _loopCounterInput = False
            _buzzer.setDefaultState(0)
            return 12
        elif pressed == 1:              # FORWARD
            _modifyLoopCounter(1)
        elif pressed == 16:             # RIGHT
            _modifyLoopCounter(1)
        elif pressed == 32:             # BACKWARD
            _modifyLoopCounter(-1)
        elif pressed == 128:            # LEFT
            _modifyLoopCounter(-1)
        elif pressed == 512:            # DELETE a.k.a. 'X'
            _modifyLoopCounter(0)
        else:
            _checkLoopCounter()
        return 0
    elif pressed == 4:                  # REPEAT
        _loopCounterInput = True
        _buzzer.midiBeep(71, 100, 50, 2)
        return 11
    else:
        return _processingGeneralInput(pressed)


def _processingMidiInput(pressed):
    return 0



def _addCommand():
    global _loopCounter

    try:
        pressed = _getValidatedPressedButton()

        if pressed == 0:
            result = 0                                        # Zero means, there is nothing to append to _commandArray.
        else:
            if _loopInputMode:
                result = _processingLoopInput(pressed)

                if result == 12:                              # If the loop has closed
                    if _loopCounter == 0:                     # Loop created accidentally, loop is no more needed, etc.
                        while _commandArray[_commandPointer] == 10:                  # Purge unnecessary half-baked loop
                            _undoCommand()
                        _buzzer.midiBeep(71, 100, 25, 3)
                        _buzzer.midiBeep(60, 500, 100, 1)
                        result = 0
                    else:                                                                    # Successful loop creating.
                        _addToCommandArray(_loopCounter)
                        _loopCounter = 0
                        _buzzer.midiBeep(60, 100, 50, 2)

            elif _midiInputMode:
                result = _processingMidiInput(pressed)

            else:
                result = _processingGeneralInput(pressed)


        if result != 0:
            _addToCommandArray(result)
            _buzzer.midiBeep(64, 100, 0, 1)
    except Exception as e:
        sys.print_exception(e)


def config(config, buzzer):

    global _clockPin
    global _inputPin
    global _pressLength
    global _maxError
    global _firstRepeat
    global _loopChecking
    global _pressedList
    global _buzzer

    _clockPin = Pin(config.get("turtleClockPin"), Pin.OUT)
    _clockPin.off()

    _inputPin = Pin(config.get("turtleInputPin"), Pin.OUT) # FUTURE: Pin(16, Pin.IN)
    _inputPin.off()                                        # DEPRECATED: New PCB design (2.1) will resolve this.
    _inputPin.init(Pin.IN)                                 # DEPRECATED: New PCB design (2.1) will resolve this.

    _pressLength  = config.get("turtlePressLength")
    _maxError     = config.get("turtleMaxError")
    _firstRepeat  = config.get("turtleFirstRepeat")
    _loopChecking = config.get("turtleLoopChecking")

    _pressedList  = [0] * (_pressLength + _maxError)
    _buzzer       = buzzer

    _timer.init(period = config.get("turtleCheckPeriod"), mode = Timer.PERIODIC, callback = lambda t:_addCommand())

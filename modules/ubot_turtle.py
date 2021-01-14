import sys
from machine import Pin, Timer
import ubot_buzzer as buzzer

_clockPin          = 0           # [need config()] Advances the decade counter (U3).
_inputPin          = 0           # [need config()] Checks the returning signal from turtle HAT.
_counterPosition   = 0           #                 The position of the decade counter (U3).
_pressLength       = 0           # [need config()]
_maxError          = 0           # [need config()]

_lastPressed       = [0, 0]      #                 Inside: [last pressed button, elapsed (button check) cycles]
_firstRepeat       = 0           # [need config()]
_loopChecking      = 0           # [need config()]

_pressedListIndex  = 0
_pressedList       = 0           # [need config()] Low-level:  The last N (_pressLength + _maxError) buttoncheck results.
_commandArray      = bytearray() #                 High-level: Abstract commands, result of processed button presses.
_commandPointer    = 0           #                 Pointer for _commandArray.
_programArray      = bytearray() #                 High-level: Result of one or more added _commandArray.
_programPointer    = 0           #                 Pointer for _programArray.
_programParts      = []          #                 Positions by which _programArray can be split into _commandArray(s).

_loopCounter       = 0           #

_functionDefined   = [False, False, False]

_blockStartIndex   = 0           #
_blockPrevStarts   = []          #
_currentMapping    = 0           #
_previousMappings  = []          #
_runningProgram    = False       #
_timer             = Timer(-1)   #                 Executes the repeated button checks.



################################
## BUTTON PRESS PROCESSING

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
            pressed += 1<<_counterPosition # pow(2, _counterPosition)

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



################################
## BUTTON PRESS INTERPRETATION

def _addCommand():
    try:
        pressed = _getValidatedPressedButton()

        if pressed == 0:                # result = 0 means, there is nothing to save to _commandArray.
            result = 0                  # Not only lack of buttonpress (pressed == 0) returns 0.
        elif _runningProgram:
            _startOrStop((0, False))    # Stop program execution.
        else:
            tupleWithCallable = _currentMapping.get(pressed)                # Dictionary based switch...case

            if tupleWithCallable == None:                                   # Default branch
                result = 0
            else:
                if tupleWithCallable[1] == ():
                    result = tupleWithCallable[0]()
                else:
                    result = tupleWithCallable[0](tupleWithCallable[1])

        if result != 0:
            if isinstance(result, int):
                _addToCommandArray(result)
            else:
                for r in result:
                    _addToCommandArray(result)
    except Exception as e:
        sys.print_exception(e)


def _addToCommandArray(command):
    global _commandArray
    global _commandPointer

    if _commandPointer < len(_commandArray):
        _commandArray[_commandPointer] = command
    else:
        _commandArray.append(command)

    _commandPointer += 1



################################
## STANDARDIZED FUNCTIONS


# COMMAND AND PROGRAM ARRAY

def _addToProgramArray():
    pass


# BLOCK

def _blockStarted(newMapping):
    global _blockStartIndex
    global _currentMapping

    _blockPrevStarts.append(_blockStartIndex)
    _blockStartIndex = _commandPointer
    _previousMappings.append(_currentMapping)
    _currentMapping  = newMapping
    buzzer.setDefaultState(1)
    buzzer.keyBeep("beepStarted")


def _blockCompleted(delete):
    global _commandPointer
    global _blockStartIndex
    global _currentMapping

    if delete:
        _commandPointer = _blockStartIndex

    buzzer.setDefaultState(0)
    _blockStartIndex = _blockPrevStarts.pop()
    _currentMapping  = _previousMappings.pop()

    if delete:
        buzzer.keyBeep("beepDeleted")
        return True
    else:
        buzzer.keyBeep("beepCompleted")
        return False



# LOOP

def _createLoop(arguments):                 # (creationState,)               10  [statements...] 11 [iteration count] 12
    global _currentMapping
    global _loopCounter

    if arguments[0] == 10:
        _blockStarted(_loopBeginMapping)
        _loopCounter = 0
        return 10
    elif arguments[0] == 11:
        _currentMapping = _loopCounterMapping
        buzzer.keyBeep("beepInputNeeded")
        return 11
    elif arguments[0] == 12:
        return ((_loopCounter, 12), 0)[_blockCompleted(_loopCounter == 0)]  # False == 0, and True == 1 (deleted)



def _modifyLoopCounter(arguments):          # (value,)     Increasing by this value, if value == 0, it resets he counter
    global _loopCounter

    if _loopCounter + arguments[0] < 1:             # Checks lower boundary.
        _loopCounter = 1
        buzzer.keyBeep("beepBoundary")
    elif 255 < _loopCounter + arguments[0]:         # Checks upper boundary.
        _loopCounter = 255
        buzzer.keyBeep("beepBoundary")
    elif arguments[0] == 0:                         # Reset the counter. Use case: forget the exact count and press 'X'.
        _loopCounter = 0
        buzzer.keyBeep("beepDeleted")
    else:                                           # General modification.
        _loopCounter += arguments[0]
        buzzer.keyBeep("beepInAndDecrease")


def _checkLoopCounter():
    global _loopChecking

    if _loopChecking == 1:
        if _loopCounter <= 20:
            buzzer.keyBeep("beepAttention")
            buzzer.midiBeep(64, 100, 400, _loopCounter)
        else:
            buzzer.keyBeep("beepTooLong")
    elif _loopChecking == 2:
        buzzer.keyBeep("beepAttention")
        buzzer.midiBeep(64, 100, 400, _loopCounter)


# FUNCTION

def _manageFunction(arguments):             # (functionId, onlyCall)
    global _functionDefined

    if arguments[1] or _functionDefined[arguments[0]]:      # Call function <- flag 'only call' is True or it is defined
        buzzer.keyBeep("beepProcessed")
        return (23, arguments[0], 24)
    elif _functionDefined[arguments[0]] == ():              # End of defining the function
        _blockCompleted()
        _functionDefined[arguments[0]] = True
        return (21, arguments[0], 22)
    else:                                                   # Beginning of defining the function
        _blockStarted(_functionMapping)
        _functionDefined[arguments[0]] = ()                 # In progress, so it isn't True or False.
        return 20



# GENERAL

def _beepAndReturn(arguments):              # (keyOfBeep, returningValue)
    buzzer.keyBeep(arguments[0])
    return arguments[1]


def _startOrStop(arguments):                # (blockLevel, starting)
    global _runningProgram

    _runningProgram = arguments[1]
    pass


def _undo(arguments):                       # (blockLevel,)
    global _commandPointer
    global _programPointer                # I think this will be needed, if section 53-55 became something useful... :-)

    if 0 < _commandPointer:
        _commandPointer -= 1
        return True
    else:
        if 0 < _programPointer:
            buzzer.keyBeep("beepLoaded")
            # Move last added _commandArray from _programArray to _commandArray variable, etc...
            return True
        else:
            buzzer.keyBeep("beepBoundary")
            return False
"""
# from _addCommand()

    elif pressed == 256:            # UNDO
        if not _loopCounterInput:
            undoResult = _undoCommand()
            if _commandArray[_commandPointer] == 10:
                _loopInputMode = False
                buzzer.setDefaultState(0)
                buzzer.keyBeep("beepDeleted")
            else:
                if undoResult:
                    buzzer.keyBeep("beepUndone")
        return 0
"""

def _delete(arguments):                     # (blockLevel,)
    global _commandPointer

    if arguments[0] == True:
        _blockCompleted(True)
    else:
        _commandPointer = 0


def _customMapping():
    pass





################################
## MAPPINGS

_defaultMapping = {
    1:    (_beepAndReturn,     ("beepProcessed", 1)),               # FORWARD
    2:    (_beepAndReturn,     ("beepProcessed", 9)),               # PAUSE
    4:    (_createLoop,        (10,)),                              # REPEAT
    6:    (_manageFunction,    (1, False)),                         # F1
    8:    (_addToProgramArray, ()),                                 # ADD
    10:   (_manageFunction,    (2, False)),                         # F2
    12:   (_manageFunction,    (3, False)),                         # F3
    16:   (_beepAndReturn,     ("beepProcessed", 4)),               # RIGHT
    32:   (_beepAndReturn,     ("beepProcessed", 2)),               # BACKWARD
    64:   (_startOrStop,       (False, True)),                      # START / STOP
    128:  (_beepAndReturn,     ("beepProcessed", 3)),               # LEFT
    256:  (_undo,              (False,)),                           # UNDO
    512:  (_delete,            (False,)),                           # DELETE
    1023: (_customMapping,     ())                                  # MAPPING
}

_loopBeginMapping = {
    1:    (_beepAndReturn,     ("beepProcessed", 1)),               # FORWARD
    2:    (_beepAndReturn,     ("beepProcessed", 9)),               # PAUSE
    4:    (_createLoop,        (11,)),                              # REPEAT
    6:    (_manageFunction,    (1, True)),                          # F1
    10:   (_manageFunction,    (2, True)),                          # F2
    12:   (_manageFunction,    (3, True)),                          # F3
    16:   (_beepAndReturn,     ("beepProcessed", 4)),               # RIGHT
    32:   (_beepAndReturn,     ("beepProcessed", 2)),               # BACKWARD
    64:   (_startOrStop,       (True, True)),                       # START / STOP
    128:  (_beepAndReturn,     ("beepProcessed", 3)),               # LEFT
    256:  (_undo,              (True,)),                            # UNDO
    512:  (_delete,            (True,))                             # DELETE
}


_loopCounterMapping = {
    1:    (_modifyLoopCounter, (1,)),                               # FORWARD
    4:    (_createLoop,        (12,)),                              # REPEAT
    16:   (_modifyLoopCounter, (1,)),                               # RIGHT
    32:   (_modifyLoopCounter, (-1,)),                              # BACKWARD
    64:   (_checkLoopCounter,  ()),                                 # START / STOP
    128:  (_modifyLoopCounter, (-1,)),                              # LEFT
    512:  (_modifyLoopCounter, (0,))                                # DELETE
}


_functionMapping = {
    1:    (_beepAndReturn,     ("beepProcessed", 1)),               # FORWARD
    2:    (_beepAndReturn,     ("beepProcessed", 9)),               # PAUSE
    4:    (_createLoop,        (10,)),                              # REPEAT
    6:    (_manageFunction,    (1, False)),                         # F1
    10:   (_manageFunction,    (2, False)),                         # F2
    12:   (_manageFunction,    (3, False)),                         # F3
    16:   (_beepAndReturn,     ("beepProcessed", 4)),               # RIGHT
    32:   (_beepAndReturn,     ("beepProcessed", 2)),               # BACKWARD
    64:   (_startOrStop,       (True, True)),                       # START / STOP
    128:  (_beepAndReturn,     ("beepProcessed", 3)),               # LEFT
    256:  (_undo,              (True,)),                            # UNDO
    512:  (_delete,            (True,))                             # DELETE
}



def config(config):
    global _clockPin
    global _inputPin
    global _pressLength
    global _maxError
    global _firstRepeat
    global _loopChecking
    global _pressedList
    global _currentMapping

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

    _currentMapping = _defaultMapping

    _timer.init(period = config.get("turtleCheckPeriod"), mode = Timer.PERIODIC, callback = lambda t:_addCommand())

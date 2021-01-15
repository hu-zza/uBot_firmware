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
            result = _startOrStop((0, False))    # Stop program execution.
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
            elif isinstance(result, tuple):
                for r in result:
                    _addToCommandArray(r)
            else:
                print("Wrong result: {}".format(result))
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
## HELPER METHODS FOR BLOCKS

def _blockStarted(newMapping):
    global _blockStartIndex
    global _currentMapping

    _blockPrevStarts.append(_blockStartIndex)
    _blockStartIndex = _commandPointer
    _previousMappings.append(_currentMapping)
    _currentMapping  = newMapping
    buzzer.setDefaultState(1)
    buzzer.keyBeep("beepStarted")


def _blockCompleted(deleteFlag):
    global _commandPointer
    global _blockStartIndex
    global _currentMapping

    if len(_previousMappings) != 0:
        if deleteFlag:
            _commandPointer = _blockStartIndex

        _blockStartIndex = _blockPrevStarts.pop()
        _currentMapping  = _previousMappings.pop()

        if len(_previousMappings) == 0:             # len(_previousMappings) == 0 means all blocks are closed.
            buzzer.setDefaultState(0)

        if deleteFlag:
            buzzer.keyBeep("beepDeleted")
            return True
        else:
            buzzer.keyBeep("beepCompleted")
            return False


def _getOpeningBoundary(commandPointer):
    values = (_commandArray[commandPointer], _commandArray[commandPointer - 2])

    if   values[0] == 41  and values[1] == 42:      # ")" and "*"
        return 40                                   # "("
    elif values[0] == 125 and values[1] == 124:     # "}" and "|"
        return 123                                  # "{"
    elif values[0] == 126 and values[1] == 126:     # "~" and "~"
        return 126                                  # "~"
    else:
        return 0


################################
## STANDARDIZED FUNCTIONS

# COMMAND AND PROGRAM ARRAY

def _addToProgramArray():
    return 0


# LOOP

def _createLoop(arguments):                 # (creationState,)                40 [statements...] 42 [iteration count] 41
    global _currentMapping
    global _loopCounter

    if arguments[0] == 40:
        _blockStarted(_loopBeginMapping)
        _loopCounter = 0
        return 40
    elif arguments[0] == 42:
        if _commandPointer - _blockStartIndex < 2:      # If the body of the loop is empty,
            _blockCompleted(True)                       # close and delete the complete block.
            return 0
        else:
            _currentMapping = _loopCounterMapping
            buzzer.keyBeep("beepInputNeeded")
            return 42
    elif arguments[0] == 41:
         # _blockCompleted deletes the loop if counter is zero, and returns with the result of the
         # deletion (True if deleted). This returning value is used as index: False == 0, and True == 1
         # Increase _loopCounter by 48 = human-friendly bytes: 48 -> "0", 49 -> "1", ...
        return ((_loopCounter + 48, 41), 0)[_blockCompleted(_loopCounter == 0)]


def _modifyLoopCounter(arguments):          # (value,)     Increasing by this value, if value == 0, it resets he counter
    global _loopCounter

    if _loopCounter + arguments[0] < 0:     # Checks lower boundary.
        _loopCounter = 0
        buzzer.keyBeep("beepBoundary")
    elif 255 < _loopCounter + arguments[0]: # Checks upper boundary.
        _loopCounter = 255
        buzzer.keyBeep("beepBoundary")
    elif arguments[0] == 0:                 # Reset the counter. Use case: forget the exact count and press 'X'.
        _loopCounter = 0
        buzzer.keyBeep("beepDeleted")
    else:                                   # General modification.
        _loopCounter += arguments[0]
        buzzer.keyBeep("beepInAndDecrease")
    return 0


def _checkLoopCounter():
    global _loopChecking

    if _loopChecking == 2 or (_loopChecking == 1 and _loopCounter <= 20):
        buzzer.keyBeep("beepAttention")
        buzzer.midiBeep(64, 100, 500, _loopCounter)
    else:
        buzzer.keyBeep("beepTooLong")
    buzzer.rest(1000)
    return 0


# FUNCTION

def _manageFunction(arguments):             # (functionId, onlyCall)                    123 [statements...] 124 [id] 125
    global _functionDefined                 #                           function call:  126 [id] 126
    id = arguments[0]

    # Calling the function if it is defined, or flag 'only call' is True and it is not under definition.
    if _functionDefined[id - 1] or (arguments[1] and _functionDefined[id - 1] != ()):
        buzzer.keyBeep("beepProcessed")
        return (126, arguments[0] + 48, 126)          # Increase by 48 = human-friendly bytes: 48 -> "0", 49 -> "1", ...
    elif _functionDefined[id - 1] == ():              # End of defining the function
        # If function contains nothing
        # (_commandPointer - _blockStartIndex < 2 -> Function start and end are adjacent.),
        # delete it by _blockCompleted() which return a boolean (True if deleted).
        # Save the opposite of this returning value in _functionDefined.
        _functionDefined[id - 1] = not _blockCompleted(_commandPointer - _blockStartIndex < 2)

        return (0, (124, arguments[0] + 48, 125))[_functionDefined[id - 1]] # False == 0, and True == 1 (function defined)

    else:                                             # Beginning of defining the function
        _blockStarted(_functionMapping)
        _functionDefined[id - 1] = ()                 # In progress, so it isn't True or False.
        return 123


# GENERAL

def _beepAndReturn(arguments):              # (keyOfBeep, returningValue)
    buzzer.keyBeep(arguments[0])
    return arguments[1]


def _startOrStop(arguments):                # (blockLevel, starting)
    global _runningProgram

    buzzer.keyBeep("beepProcessed")
    _runningProgram = arguments[1]
    return 0


def _undo(arguments):                       # (blockLevel,)
    global _commandPointer
    global _programPointer                  # I think this will be needed, if line 342 became something useful... :-)
    global _functionDefined

    # Sets the maximum range of undo in according to blockLevel flag.
    undoLowerBoundary = _blockStartIndex + 1 if arguments[0] else 0

    if undoLowerBoundary < _commandPointer:
        _commandPointer -= 1
        buzzer.keyBeep("beepUndone")

        # If toBeUndone is a block boundary, _getOpeningBoundary returns with its pair (the beginning of the block).
        boundary = _getOpeningBoundary(_commandPointer)

        if boundary != 0:
            if boundary == 123:                                    # If it undoes a function declaration.
                _functionDefined[_commandArray[_commandPointer - 1] - 49] = False   # not 48! functionId - 1 = index
            while True:                                            # General undo decreases the pointer by one, so this
                _commandPointer -= 1                               # do...while loop can handle identic boundary pairs.
                if _commandArray[_commandPointer] == boundary:
                    break
            buzzer.keyBeep("beepDeleted")

        if _commandPointer == undoLowerBoundary:
            buzzer.keyBeep("beepBoundary")
    else:
        if arguments[0] or 0 == _programPointer:      # Block level undo or no more loadable command from _programArray.
            buzzer.keyBeep("beepBoundary")
        else:
            buzzer.keyBeep("beepLoaded")
            # Move last added _commandArray from _programArray to _commandArray variable, etc...
    return 0


def _delete(arguments):                     # (blockLevel,)
    global _commandPointer
    global _programPointer
    global _functionDefined

    if arguments[0] == True:                # Block-level
        _blockCompleted(True)               # buzzer.keyBeep("beepDeleted") is called inside _blockCompleted(True)
        for i in range(3):                  # Delete mark of unfinished function, if there are any.
            if _functionDefined[i] == ():
                _functionDefined[i] = False
    else:                                   # Not block-level: the whole _commandArray is affected.
        buzzer.keyBeep("beepDeleted")
        if _commandPointer != 0:
            _commandPointer = 0
            # for .... if 124 X 125 -> _functionDefined[X] = False
        else:
            _programPointer = 0
            _functionDefined = [False, False, False]
            buzzer.keyBeep("beepBoundary")


    return 0


def _customMapping():
    buzzer.keyBeep("beepLoaded")
    return 0





################################
## MAPPINGS

_defaultMapping = {
    1:    (_beepAndReturn,     ("beepProcessed", 70)),              # FORWARD
    2:    (_beepAndReturn,     ("beepProcessed", 80)),              # PAUSE
    4:    (_createLoop,        (40,)),                              # REPEAT (start)
    6:    (_manageFunction,    (1, False)),                         # F1
    8:    (_addToProgramArray, ()),                                 # ADD
    10:   (_manageFunction,    (2, False)),                         # F2
    12:   (_manageFunction,    (3, False)),                         # F3
    16:   (_beepAndReturn,     ("beepProcessed", 82)),              # RIGHT
    32:   (_beepAndReturn,     ("beepProcessed", 66)),              # BACKWARD
    64:   (_startOrStop,       (False, True)),                      # START / STOP
    128:  (_beepAndReturn,     ("beepProcessed", 76)),              # LEFT
    256:  (_undo,              (False,)),                           # UNDO
    512:  (_delete,            (False,)),                           # DELETE
    1023: (_customMapping,     ())                                  # MAPPING
}

_loopBeginMapping = {
    1:    (_beepAndReturn,     ("beepProcessed", 70)),              # FORWARD
    2:    (_beepAndReturn,     ("beepProcessed", 80)),              # PAUSE
    4:    (_createLoop,        (42,)),                              # REPEAT (*)
    6:    (_manageFunction,    (1, True)),                          # F1
    10:   (_manageFunction,    (2, True)),                          # F2
    12:   (_manageFunction,    (3, True)),                          # F3
    16:   (_beepAndReturn,     ("beepProcessed", 82)),              # RIGHT
    32:   (_beepAndReturn,     ("beepProcessed", 66)),              # BACKWARD
    64:   (_startOrStop,       (True, True)),                       # START / STOP
    128:  (_beepAndReturn,     ("beepProcessed", 76)),              # LEFT
    256:  (_undo,              (True,)),                            # UNDO
    512:  (_delete,            (True,))                             # DELETE
}


_loopCounterMapping = {
    1:    (_modifyLoopCounter, (1,)),                               # FORWARD
    4:    (_createLoop,        (41,)),                              # REPEAT (end)
    16:   (_modifyLoopCounter, (1,)),                               # RIGHT
    32:   (_modifyLoopCounter, (-1,)),                              # BACKWARD
    64:   (_checkLoopCounter,  ()),                                 # START / STOP
    128:  (_modifyLoopCounter, (-1,)),                              # LEFT
    512:  (_modifyLoopCounter, (0,))                                # DELETE
}


_functionMapping = {
    1:    (_beepAndReturn,     ("beepProcessed", 70)),              # FORWARD
    2:    (_beepAndReturn,     ("beepProcessed", 80)),              # PAUSE
    4:    (_createLoop,        (40,)),                              # REPEAT (start)
    6:    (_manageFunction,    (1, True)),                          # F1
    10:   (_manageFunction,    (2, True)),                          # F2
    12:   (_manageFunction,    (3, True)),                          # F3
    16:   (_beepAndReturn,     ("beepProcessed", 82)),              # RIGHT
    32:   (_beepAndReturn,     ("beepProcessed", 66)),              # BACKWARD
    64:   (_startOrStop,       (True, True)),                       # START / STOP
    128:  (_beepAndReturn,     ("beepProcessed", 76)),              # LEFT
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

    _inputPin = Pin(config.get("turtleInputPin"), Pin.OUT) # FUTURE: _inputPin = Pin(16, Pin.IN)
    _inputPin.off()                                        # DEPRECATED: New PCB design (2.1) will resolve this.
    _inputPin.init(Pin.IN)                                 # DEPRECATED: New PCB design (2.1) will resolve this.

    _pressLength  = config.get("turtlePressLength")
    _maxError     = config.get("turtleMaxError")
    _firstRepeat  = config.get("turtleFirstRepeat")
    _loopChecking = config.get("turtleLoopChecking")

    _pressedList  = [0] * (_pressLength + _maxError)

    _currentMapping = _defaultMapping

    _timer.init(period = config.get("turtleCheckPeriod"), mode = Timer.PERIODIC, callback = lambda t:_addCommand())

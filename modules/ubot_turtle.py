from machine import Pin, Timer

import ubot_buzzer    as buzzer
import ubot_logger    as logger
import ubot_motor     as motor


_powerOnCount      = 0           # [need config()]

_clockPin          = 0           # [need config()] Advances the decade counter (U3).
_inputPin          = 0           # [need config()] Checks the returning signal from turtle HAT.
_checkPeriod       = 0           # [need config()]
_counterPosition   = 0           #                 The position of the decade counter (U3).
_pressLength       = 0           # [need config()]
_maxError          = 0           # [need config()]

_lastPressed       = [0, 0]      #                 Inside: [last pressed button, elapsed (button check) cycles]
_firstRepeat       = 0           # [need config()]
_loopChecking      = 0           # [need config()]
_moveLength        = 0           #
_turnLength        = 0           #
_breathLength      = 0           #

_stepSignal        = ""          # [need config()] Sound indicates the end of a step during execution: buzzer.keyBeep(_stepSignal)
_endSignal         = ""          # [need config()] Sound indicates the end of program execution:       buzzer.keyBeep(_endSignal)

_pressedListIndex  = 0           #
_pressedList       = 0           # [need config()] Low-level:  The last N (_pressLength + _maxError) buttoncheck results.
_commandArray      = bytearray() #                 High-level: Abstract commands, result of processed button presses.
_commandPointer    = 0           #                 Pointer for _commandArray.
_programArray      = bytearray() #                 High-level: Result of one or more added _commandArray.
_programParts      = [0]         #                 Positions by which _programArray can be split into _commandArray(s).

_loopCounter       = 0           #                 At loop creation this holds iteration count.

_functionPosition  = [-1, -1, -1]#                 -1 : not defined, -0.1 : under definition, 0+ : defined
                                 #                 If defined, this index refer to the first command of the function,
                                 #                 instead of its curly brace "{".

_blockStartIndex   = 0           #                 At block (loop, fn declaration) creation, this holds block start position.
_blockStartStack   = []          #
_currentMapping    = 0           #
_mappingsStack     = []          #
_processingProgram = False       #
_runningProgram    = False       #
_timer             = Timer(-1)   #                 Executes the repeated button checks.

_blockBoundaries   = ((40, 41), (123, 125), (126, 126)) # (("(", ")"), ("{", "}"), ("~", "~"))

################################
## CONFIG

def config(config):
    global _powerOnCount
    global _clockPin
    global _inputPin
    global _checkPeriod
    global _pressLength
    global _maxError
    global _firstRepeat
    global _loopChecking
    global _moveLength
    global _turnLength
    global _breathLength
    global _stepSignal
    global _endSignal
    global _pressedList
    global _currentMapping

    _powerOnCount = config.get("powerOnCount")

    _clockPin = Pin(config.get("turtleClockPin"), Pin.OUT)
    _clockPin.off()

    _inputPin = Pin(config.get("turtleInputPin"), Pin.OUT) # FUTURE: _inputPin = Pin(16, Pin.IN)
    _inputPin.off()                                        # DEPRECATED: New PCB design (2.1) will resolve this.
    _inputPin.init(Pin.IN)                                 # DEPRECATED: New PCB design (2.1) will resolve this.

    _checkPeriod  = config.get("turtleCheckPeriod")
    _pressLength  = config.get("turtlePressLength")
    _maxError     = config.get("turtleMaxError")
    _firstRepeat  = config.get("turtleFirstRepeat")
    _loopChecking = config.get("turtleLoopChecking")

    _moveLength   = config.get("turtleMoveLength")
    _turnLength   = config.get("turtleTurnLength")
    _breathLength = config.get("turtleBreathLength")

    _endSignal    = config.get("turtleEndSignal")
    _stepSignal   = config.get("turtleStepSignal")

    _pressedList  = [0] * (_pressLength + _maxError)

    _currentMapping = _defaultMapping

    _startButtonChecking()


################################
## PUBLIC METHODS

def move(direction):
    if isinstance(direction, str):
        direction = ord(direction)

    if direction == 70:                 # "F" - FORWARD
        motor.move(1, _moveLength)
    elif direction == 66:               # "B" - BACKWARD
        motor.move(4, _moveLength)
    elif direction == 76:               # "L" - LEFT (90°)
        motor.move(2, _turnLength)
    elif direction == 108:              # "l" - LEFT (45°)
        motor.move(2, _turnLength // 2) #                       Placeholder...
    elif direction == 82:               # "R" - RIGHT (90°)
        motor.move(3, _turnLength)
    elif direction == 114:              # "r" - RIGHT (45°)
        motor.move(3, _turnLength // 2) #                       Placeholder...
    elif direction == 80:               # "P" - PAUSE
        motor.move(0, _moveLength)


def press(pressed):                     # pressed = 1<<buttonOrdinal
    if isinstance(pressed, str):
        pressed = int(pressed)

    _logLastPressed(pressed)
    _addCommand(pressed)


def checkButtons():
    _addCommand(_getValidatedPressedButton())



################################################################
################################################################
##########
##########  PRIVATE, CLASS-LEVEL METHODS
##########


################################
## BUTTON PRESS PROCESSING

def _startButtonChecking():
    _timer.init(
        period = _checkPeriod,
        mode = Timer.PERIODIC,
        callback = lambda t:checkButtons()
    )


def _stopButtonChecking():
    _timer.deinit()


def _getValidatedPressedButton():
    global _lastPressed

    pressed = _getPressedButton()

    _logLastPressed(pressed)

    if _lastPressed[1] == 1 or _firstRepeat < _lastPressed[1]:    # Lack of pressing returns same like a button press.
        _lastPressed[1] = 1                                       # In this case the returning value is 0.
        return pressed
    else:
        return 0                                                 # If validation is in progress, returns 0.


def _logLastPressed(pressed):
    global _lastPressed
    if pressed == _lastPressed[0]:
        _lastPressed[1] += 1
    else:
        _lastPressed = [pressed, 1]


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


def _advanceCounter():
    global _counterPosition

    _clockPin.on()

    if 9 <= _counterPosition:
        _counterPosition = 0
    else:
        _counterPosition += 1

    _clockPin.off()



################################
## BUTTON PRESS INTERPRETATION

def _addCommand(pressed):
    global _processingProgram
    global _runningProgram

    try:
        if pressed == 0:                # result = 0 means, there is nothing to save to _commandArray.
            result = 0                  # Not only lack of buttonpress (pressed == 0) returns 0.
        elif _runningProgram:
            motor.stop()                                                    # Stop commands / program execution.
            _processingProgram = False
            _runningProgram    = False
            result = _beepAndReturn(("processed", 0))                   # Beep and skip the (result) processing.
        else:
            tupleWithCallable = _currentMapping.get(pressed)                # Dictionary based switch...case

            if tupleWithCallable == None:                                   # Default branch
                result = 0                                                  # Skip the (result) processing.
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
        logger.append(e)


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

    _blockStartStack.append(_blockStartIndex)
    _blockStartIndex = _commandPointer
    _mappingsStack.append(_currentMapping)
    _currentMapping  = newMapping
    buzzer.setDefaultState(1)
    buzzer.keyBeep("started")


def _blockCompleted(deleteFlag):
    global _commandPointer
    global _blockStartIndex
    global _currentMapping

    if len(_mappingsStack) != 0:
        if deleteFlag:
            _commandPointer = _blockStartIndex

        _blockStartIndex = _blockStartStack.pop()
        _currentMapping  = _mappingsStack.pop()

        if len(_mappingsStack) == 0:        # len(_mappingsStack) == 0 means all blocks are closed.
            buzzer.setDefaultState(0)

        if deleteFlag:
            buzzer.keyBeep("deleted")
            return True
        else:
            buzzer.keyBeep("completed")
            return False


def _getOppositeBoundary(commandPointer):
    bondary = _commandArray[commandPointer]

    for bondaryPair in _blockBoundaries:
        if bondary == bondaryPair[0]:
            return bondaryPair[1]
        elif bondary == bondaryPair[1]:
            return bondaryPair[0]
    return -1


def _isTagBoundary(commandPointer):
    return _commandArray[commandPointer] == _getOppositeBoundary(commandPointer)



################################
## HELPER METHODS FOR LOGS

def _logExecuted():
    fileName = "{:010d}.txt".format(_powerOnCount)

    try:
        with open("log/datetime/" + fileName, "a") as file:
            file.write("{}\n".format(config.datetime()))
    except Exception as e:
        logger.append(e)

    try:
        with open("log/commands/" + fileName, "a") as file:
            file.write("{}\n".format(_commandArray[:_commandPointer].decode()))
    except Exception as e:
        logger.append(e)

    try:
        with open("log/program/" + fileName, "a") as file:
            file.write("{}\n".format(_programArray[:_programParts[-1]].decode()))
    except Exception as e:
        logger.append(e)



################################
## STANDARDIZED FUNCTIONS

def _start(arguments):                # (blockLevel,)
    global _processingProgram
    global _runningProgram

    buzzer.keyBeep("processed")
    _processingProgram = True
    _runningProgram    = True
    _stopButtonChecking()

    if arguments[0] or 0 < _commandPointer: # Executing the body of a block or the _commandArray
        _toPlay        = _commandArray
        _upperBoundary = _commandPointer
    else:                                   # Executing the _programArray
        _toPlay        = _programArray
        _upperBoundary = _programParts[-1]

    _pointer      =  _blockStartIndex + 1 if arguments[0] else 0
    _pointerStack = []
    _counterStack = []

    config.saveDateTime()
    _logExecuted()

    motor.setCallback(lambda: _callbackEnd(),  0, False)
    motor.setCallback(lambda: _callbackStep(), 1, False)

    #counter = 0                             #      Debug
    #print("_toPlay[:_pointer]", "_toPlay[_pointer:]", "\t\t\t", "counter", "_pointer", "_toPlay[_pointer]") # Debug

    while _processingProgram:
        remaining = _upperBoundary - 1 - _pointer #      Remaining bytes in _toPlay bytearray. 0 if _toPlay[_pointer] == _toPlay[-1]
        checkCounter = False

        #if _pointer < _upperBoundary:          #      Debug
        #    print(_toPlay[:_pointer].decode(), _toPlay[_pointer:].decode(), "\t\t\t", counter, _pointer, _toPlay[_pointer])

        if remaining < 0:                       #      If everything is executed, exits.
            _processingProgram = False


        elif _toPlay[_pointer] == 40:           # "("  The block-level previews are excluded. (Those starts from first statement.)

            _pointerStack.append(_pointer)      #      Save the position of the loop's starting parentheses: "("

            while _pointer < _upperBoundary and _toPlay[_pointer] != 42: # "*"  Jump to the end of the loop's body.
                _pointer += 1

            remaining = _upperBoundary - 1 - _pointer

            if 2 <= remaining and _toPlay[_pointer] == 42:       # If the loop is complete and the pointer is at the end of its body.
                _counterStack.append(_toPlay[_pointer + 1] - 48) # Counter was increased at definition by 48. b'0' == 48
                checkCounter = True
            else:                               #      Maybe it's an error, so stop execution.
                _processingProgram = False


        elif _toPlay[_pointer] == 42:           # "*"  End of the body of the loop.
            _counterStack[-1] -= 1              #      Decrease the loop counter.
            checkCounter = True


        elif _toPlay[_pointer] == 123:          # "{"  Start of a function.

            while _pointer < _upperBoundary and _toPlay[_pointer] != 125: # "}" Jump to the function's closing curly brace.
                _pointer += 1

            if _toPlay[_pointer] != 125:        #      Means the _pointer < _upperBoundary breaks the while loop.
                _processingProgram = False


        elif _toPlay[_pointer] == 124:          # "|"  End of the currently executed function.
            _pointer = _pointerStack.pop()      #      Jump back to where the function call occurred.


        elif _toPlay[_pointer] == 126:          # "~"
            if 2 <= remaining and _toPlay[_pointer + 2] == 126: # Double-check: 1. Enough remaining to close function call; 2. "~"
                _pointerStack.append(_pointer + 2)      # Save the returning position as the second tilde: "~"
                _index = _toPlay[_pointer + 1] - 49     # Not 48! functionId - 1 = array index
                _jumpTo = -1                            # Declared with -1 because of the check "_pointer != _jumpTo".
                if _index < len(_functionPosition):     # If the _functionPosition contains the given function index.
                    _jumpTo = _functionPosition[_index]
                    if 0 <= _jumpTo:                    # If the retrieved value from _functionPosition is a real position.
                        _pointer = _jumpTo
                if _pointer != _jumpTo:                 # This handles both else branch of previous two if statements:
                    del _pointerStack[-1]               # The function call failed, there is no need for "jump back" index.
                    _pointer += 2                       # Jump to the second tilde: "~" (Skip the whole function call.)
            else:                                       # Maybe it's an error, so stop execution.
                _processingProgram = False


        else:
            move(_toPlay[_pointer])             #      Try to execute the command as move. It can fail without exception.


        if checkCounter:
            if 0 < _counterStack[-1]:           #      If the loop counter is greater than 0.
                _pointer = _pointerStack[-1]    #      Jump back to the loop starting position.
            else:
                del _pointerStack[-1]           #      Delete the loop's starting position from stack.
                del _counterStack[-1]           #      Delete the loop's counter from stack.
                _pointer += 2                   #      Jump to the loop's closing parentheses: ")"

        #if _pointer < _upperBoundary:           #      Debug
        #    print(_toPlay[:_pointer].decode(), _toPlay[_pointer:].decode(), "\t\t\t", counter, _pointer, _toPlay[_pointer], "\n")
        #counter += 1                            #      Debug

        _pointer += 1

    _processingProgram = False
    _startButtonChecking()
    return 0


# COMMAND AND PROGRAM ARRAY

def _addToProgramArray():
    global _commandPointer
    global _programArray

    for i in range(_commandPointer):
        if _programParts[-1] + i < len(_programArray):
            _programArray[_programParts[-1] + i] = _commandArray[i]
        else:
            _programArray.append(_commandArray[i])

    _programParts.append(_programParts[-1] + _commandPointer)
    _commandPointer = 0
    buzzer.keyBeep("added")
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
            buzzer.keyBeep("inputNeeded")
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
        buzzer.keyBeep("boundary")
    elif 255 < _loopCounter + arguments[0]: # Checks upper boundary.
        _loopCounter = 255
        buzzer.keyBeep("boundary")
    elif arguments[0] == 0:                 # Reset the counter. Use case: forget the exact count and press 'X'.
        _loopCounter = 0
        buzzer.keyBeep("deleted")
    else:                                   # General modification.
        _loopCounter += arguments[0]
        buzzer.keyBeep("inAndDecrease")
    return 0


def _checkLoopCounter():
    global _loopChecking

    if _loopChecking == 2 or (_loopChecking == 1 and _loopCounter <= 20):
        buzzer.keyBeep("attention")
        buzzer.midiBeep(64, 100, 500, _loopCounter)
    else:
        buzzer.keyBeep("tooLong")
    buzzer.rest(1000)
    return 0


# FUNCTION

def _manageFunction(arguments):             # (functionId, onlyCall)                    123 [statements...] 124 [id] 125
    global _functionPosition                #                           function call:  126 [id] 126
    index = arguments[0] - 1                # functionId - 1 == Index in _functionPosition

    if index < 0 or len(_functionPosition) < index: # The given index is out of array.
        buzzer.keyBeep("boundary")
        return 0                            # Ignore and return.
    elif len(_functionPosition) == index:      # The given index is out of array. However, it's subsequent:
        _functionPosition.append(-1)        # Extending the array and continue.

    # Calling the function if it is defined, or flag 'only call' is True and it is not under definition.
    # In the second case, position -1 (undefined) is fine. (lazy initialization)
    if 0 <= _functionPosition[index] or (arguments[1] and _functionPosition[index] != -0.1):
        buzzer.keyBeep("processed")
        return (126, arguments[0] + 48, 126)        # Increase by 48 = human-friendly bytes: 48 -> "0", 49 -> "1", ...
    elif _functionPosition[index] == -0.1:          # End of defining the function
        # Save index to _functionPosition, because _blockStartIndex will be destroyed during _blockCompleted().
        _functionPosition[index] = len(_programArray) + _blockStartIndex

        # If function contains nothing
        # (_commandPointer - _blockStartIndex < 2 -> Function start and end are adjacent.),
        # delete it by _blockCompleted() which return a boolean (True if deleted).
        # If this returning value is True, retain len(_programArray) + _blockStartIndex, else overwrite it with -1.
        if _blockCompleted(_commandPointer - _blockStartIndex < 2):
            _functionPosition[index] = -1

        return (0, (124, arguments[0] + 48, 125))[0 <= _functionPosition[index]] # False == 0, and True == 1 (defined)

    else:                                             # Beginning of defining the function
        _blockStarted(_functionMapping)
        _functionPosition[index] = -0.1              # In progress, so it isn't -1 (undefined) or 0+ (defined).
        return 123


# GENERAL

def _beepAndReturn(arguments):              # (keyOfBeep, returningValue)
    buzzer.keyBeep(arguments[0])
    return arguments[1]


def _undo(arguments):                       # (blockLevel,)
    global _commandPointer
    global _commandArray
    global _functionPosition

    # Sets the maximum range of undo in according to blockLevel flag.
    undoLowerBoundary = _blockStartIndex + 1 if arguments[0] else 0

    if undoLowerBoundary < _commandPointer:                         # If there is anything that can be undone.
        _commandPointer -= 1
        buzzer.keyBeep("undone")

        # _getOppositeBoundary returns -1 if byte at _commandPointer is not boundary or its pair.
        boundary = _getOppositeBoundary(_commandPointer)

        if boundary != -1:
            if boundary == 123:                                    # "{" If it undoes a function declaration, unregister:
                _functionPosition[_commandArray[_commandPointer - 1] - 49] = -1 # Not 48! functionId - 1 = array index
            while True:                                            # General undo decreases the pointer by one, so this
                _commandPointer -= 1                               # do...while loop can handle identic boundary pairs.
                if _commandArray[_commandPointer] == boundary or _commandPointer == undoLowerBoundary:
                    break

            if not _isTagBoundary(_commandPointer):                # Tags (like function calling) need no keyBeep().
                buzzer.keyBeep("deleted")

        if _commandPointer == undoLowerBoundary:
            buzzer.keyBeep("boundary")
    else:
        if arguments[0] or _programParts == [0]:   # If block-level undo or no more loadable command from _programArray.
            buzzer.keyBeep("boundary")
        else:
            _commandPointer = _programParts[-1] - _programParts[-2]
            _commandArray   = _programArray[_programParts[-2] : _programParts[-1]]
            del _programParts[-1]
            buzzer.keyBeep("loaded")
    return 0


def _delete(arguments):                     # (blockLevel,)
    global _commandPointer
    global _programParts
    global _functionPosition

    if arguments[0] == True:                # Block-level: delete only the unfinished block.
        _blockCompleted(True)               # buzzer.keyBeep("deleted") is called inside _blockCompleted(True)
        for i in range(len(_functionPosition)): # Maybe there are user defined functions, so not range(3).
            if _functionPosition[i] == -0.1:    # If this function is unfinished.
                _functionPosition[i] = -1       # Set as undefined.
    else:                                   # Not block-level: the whole array is affected.
        if _commandPointer != 0:            # _commandArray isn't "empty", so "clear" it.
            for i in range(_commandPointer - 3):                            # Unregister functions defined in deleted range.
                if _commandArray[i] == 124 and _commandArray[i + 2] == 125: # "|" and "}"
                    _functionPosition[_commandArray[i + 1] - 49] = -1       # Not 48! functionId - 1 = array index
            _commandPointer = 0             # "Clear" _commandArray.
            buzzer.keyBeep("deleted")
        elif _programParts != [0]:          # _commandArray is "empty", but _programArray is not, "clear" it.
            _functionPosition = [-1] * len(_functionPosition)   # User may want to use higher ids first (from the
                                                                # previously used ones). So it is not [-1, -1, -1]
            _programParts = [0]             # "Clear" _programArray.
            buzzer.keyBeep("deleted")

    if _commandPointer == 0 and _programParts == [0]: # If _commandArray and _programArray are "empty".
        buzzer.keyBeep("boundary")

    return 0


def _customMapping():
    buzzer.keyBeep("loaded")
    return 0



################################
## CALLBACK FUNCTIONS

def _callbackStep():
    if _stepSignal != "":
        buzzer.keyBeep(_stepSignal)
    checkButtons()


def _callbackEnd():
    global _runningProgram

    _runningProgram    = False

    if _endSignal != "":
        buzzer.keyBeep(_endSignal)



################################
## MAPPINGS

_defaultMapping = {
    1:    (_beepAndReturn,     ("processed", 70)),                  # FORWARD
    2:    (_beepAndReturn,     ("processed", 80)),                  # PAUSE
    4:    (_createLoop,        (40,)),                              # REPEAT (start)
    6:    (_manageFunction,    (1, False)),                         # F1
    8:    (_addToProgramArray, ()),                                 # ADD
    10:   (_manageFunction,    (2, False)),                         # F2
    12:   (_manageFunction,    (3, False)),                         # F3
    16:   (_beepAndReturn,     ("processed", 82)),                  # RIGHT
    32:   (_beepAndReturn,     ("processed", 66)),                  # BACKWARD
    64:   (_start,             (False,)),                           # START / STOP (start)
    128:  (_beepAndReturn,     ("processed", 76)),                  # LEFT
    256:  (_undo,              (False,)),                           # UNDO
    512:  (_delete,            (False,)),                           # DELETE
    1023: (_customMapping,     ())                                  # MAPPING
}


_loopBeginMapping = {
    1:    (_beepAndReturn,     ("processed", 70)),                  # FORWARD
    2:    (_beepAndReturn,     ("processed", 80)),                  # PAUSE
    4:    (_createLoop,        (42,)),                              # REPEAT (*)
    6:    (_manageFunction,    (1, True)),                          # F1
    10:   (_manageFunction,    (2, True)),                          # F2
    12:   (_manageFunction,    (3, True)),                          # F3
    16:   (_beepAndReturn,     ("processed", 82)),                  # RIGHT
    32:   (_beepAndReturn,     ("processed", 66)),                  # BACKWARD
    64:   (_start,             (True,)),                            # START / STOP (block-level start)
    128:  (_beepAndReturn,     ("processed", 76)),                  # LEFT
    256:  (_undo,              (True,)),                            # UNDO
    512:  (_delete,            (True,))                             # DELETE
}


_loopCounterMapping = {
    1:    (_modifyLoopCounter, (1,)),                               # FORWARD
    4:    (_createLoop,        (41,)),                              # REPEAT (end)
    16:   (_modifyLoopCounter, (1,)),                               # RIGHT
    32:   (_modifyLoopCounter, (-1,)),                              # BACKWARD
    64:   (_checkLoopCounter,  ()),                                 # START / STOP (check counter)
    128:  (_modifyLoopCounter, (-1,)),                              # LEFT
    512:  (_modifyLoopCounter, (0,))                                # DELETE
}


_functionMapping = {
    1:    (_beepAndReturn,     ("processed", 70)),                  # FORWARD
    2:    (_beepAndReturn,     ("processed", 80)),                  # PAUSE
    4:    (_createLoop,        (40,)),                              # REPEAT (start)
    6:    (_manageFunction,    (1, True)),                          # F1
    10:   (_manageFunction,    (2, True)),                          # F2
    12:   (_manageFunction,    (3, True)),                          # F3
    16:   (_beepAndReturn,     ("processed", 82)),                  # RIGHT
    32:   (_beepAndReturn,     ("processed", 66)),                  # BACKWARD
    64:   (_start,             (True,)),                            # START / STOP (block-level start)
    128:  (_beepAndReturn,     ("processed", 76)),                  # LEFT
    256:  (_undo,              (True,)),                            # UNDO
    512:  (_delete,            (True,))                             # DELETE
}

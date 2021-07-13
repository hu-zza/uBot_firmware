"""
    uBot_firmware   // The firmware of the μBot, the educational floor robot. (A MicroPython port to ESP8266 with additional modules.)

    This file is part of uBot_firmware.
    [https://zza.hu/uBot_firmware]
    [https://git.zza.hu/uBot_firmware]


    MIT License

    Copyright (c) 2020-2021 Szabó László András // hu-zza

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

from machine import Pin, Timer

import ubot_config as config
import ubot_buzzer as buzzer
import ubot_logger as logger
import ubot_motor  as motor
import ubot_data   as data


MAIN_FOLDER    = data.Path("program")
_powerOns      = config.get("system", "power_ons")
_namedFolder   = config.get("turtle", "named_folder")
_turtleFolder  = config.get("turtle", "turtle_folder")
_moveChars     = config.get("turtle", "move_chars")
_turtleChars   = config.get("turtle", "turtle_chars")
_savedCount    = 0

_clockPin = Pin(13, Pin.OUT)                                # Advances the decade counter (U3).
_clockPin.off()
                                                            # Checks the returning signal from turtle HAT.
_inputPin = Pin(16, Pin.OUT)                                # FUTURE: _inputPin = Pin(16, Pin.IN)
_inputPin.off()                                             # DEPRECATED: New PCB design (2.1) will resolve this.
_inputPin.init(Pin.IN)                                      # DEPRECATED: New PCB design (2.1) will resolve this.

_checkPeriod  = config.get("turtle", "check_period")
_counterPosition = 0                                        # The position of the decade counter (U3).

_pressLength  = config.get("turtle", "press_length")
_maxError     = config.get("turtle", "max_error")
_lastPressed  = [0, 0]                                      # Inside: [last pressed button, elapsed (button check) cycles]
_firstRepeat  = config.get("turtle", "first_repeat")

_loopChecking = config.get("turtle", "loop_checking")

_moveLength   = config.get("turtle", "move_length")
_turnLength   = config.get("turtle", "turn_length")
_halfTurn     = _turnLength // 2
_breathLength = config.get("turtle", "breath_length")

_endSignalEnabled    = True
_endSignalSkipCount  = 0
_stepSignalEnabled   = True
_stepSignalSkipCount = 0

_endSignal    = config.get("turtle", "end_signal")          # Sound indicates the end of a step during execution: buzzer.keyBeep(_endSignal)
_stepSignal   = config.get("turtle", "step_signal")         # Sound indicates the end of program execution:       buzzer.keyBeep(_stepSignal)

_pressedListIndex = 0
_pressedList  = [0] * (_pressLength + _maxError)            # Low-level:  The last N (_pressLength + _maxError) button check results.

_commandArray   = bytearray()                               # High-level: Abstract commands, result of processed button presses.
_commandPointer = 0                                         # Pointer for _commandArray.
_programArray   = bytearray()                               # High-level: Result of one or more added _commandArray.
_programParts   = [0]                                       # Positions by which _programArray can be split into _commandArray(s).

_temporaryCommandPointer = 0                                # For stateless run
_temporaryProgramArray   = bytearray()                      # with the capability of
_temporaryProgramParts   = [0]                              # restore unsaved stuff.

_loopCounter    = 0                                         # At loop creation this holds iteration count.

_functionPosition = [-1, -1, -1]                            # -1 : not defined, -0.1 : under definition, 0+ : defined
                                                            # If defined, this index the first command of the function,
                                                            # refer to the first command of the function, instead of its curly brace "{".

_blockStartIndex   = 0                                      # At block (loop, fn declaration) creation, this holds block start position.
_blockStartStack   = []
_mappingsStack     = []
_processingProgram = False
_runningProgram    = False
_timer             = Timer(-1)                              # Executes the repeated button checks.

_blockBoundaries   = ((40, 41), (123, 125), (126, 126))     # (("(", ")"), ("{", "}"), ("~", "~"))


################################
## PUBLIC METHODS


def isBusy():
    return _processingProgram or _runningProgram


def getValidMoveChars():
    return _moveChars


def getValidTurtleChars():
    return _turtleChars


def checkButtons(timer = None):
    _addCommand(_getValidatedPressedButton())


def press(pressed):  # pressed = 1<<buttonOrdinal
    if isinstance(pressed, str):
        pressed = int(pressed)

    _logLastPressed(pressed)
    _addCommand(pressed)


def move(direction):
    if isinstance(direction, str):
        direction = ord(direction)

    movementTuple = _moveCharMapping.get(direction)
    if movementTuple is not None:
        motor.add(movementTuple)


def skipSignal(stepCount = 1, endCount = 0):
    global _stepSignalSkipCount, _endSignalSkipCount

    _stepSignalSkipCount += stepCount
    _endSignalSkipCount += endCount

def getProgramsCount():
    return sum(len(getProgramListOf(folder)) for folder in getProgramFolders())


def getProgramFolders():
    return data.getFoldersOf(MAIN_FOLDER)


def doesFolderExist(folder: str) -> bool:
    path = getPathOf(folder)
    return path.isExist and path.isFolder


def createFolder(folder: str) -> bool:
    return data.createFolder(getPathOf("program", folder))


def getProgramListOf(folder):
    return data.getFileNameListOf("program", folder, "txt")


def doesProgramExist(folder, title):
    path = getPathOf(folder, title)
    return path.isExist and path.isFile


def getProgramCode(folder: str, title: str) -> str:
    return "".join(data.getFile(getPathOf(folder, title), False))


def getPathOf(folder: str, title = "") -> data.Path:
    return data.createPathOf("program", folder, title)


def runProgram(folder, title):
    if doesProgramExist(folder, title):
        retainInTemporary()
        loadProgram(folder, title)
        press(64)
        loadFromTemporary()
        return True
    else:
        return False


def loadProgram(folder, title):
    clearMemory()
    if doesProgramExist(folder, title):
        loadProgramFromString(getProgramCode(folder, title))
        return True
    else:
        return False


def loadProgramFromString(turtleCode):
    global _programArray, _programParts

    clearMemory()
    try:
        array = turtleCode.encode()
        _programArray = array
        _programParts = [len(array)]
        return True
    except Exception as e:
        logger.append(e)
        return False


def saveLoadedProgram(folder = "", title = ""):
    return saveProgram(_namedFolder if folder == "" else folder, title, getProgramArray())


def saveProgram(folder: str = "", title: str = "", program: str = "") -> str:
    global _savedCount

    folder = _namedFolder if folder == "" else folder.lower()
    path   = _generateFullPathForAutoSave() if title == "" else data.createPathOf("program", folder, title)
    result = data.saveFile(path, program, True)

    if not result and title == "":
        _savedCount -= 1

    return str(path) if result else ""


def _generateFullPathForAutoSave() -> data.Path:
    global _savedCount
    _savedCount += 1
    return data.createPathOf("program", _turtleFolder, "{:010d}_{:03d}.txt".format(_powerOns, _savedCount))


def getCommandArray():
    return _commandArray[:_commandPointer].decode()


def getProgramArray():
    return _programArray[:_programParts[-1]].decode()


def isMemoryEmpty():
    return isCommandMemoryEmpty() and isProgramMemoryEmpty()


def isCommandMemoryEmpty():
    return _commandPointer == 0


def isProgramMemoryEmpty():
    return _programParts == [0]


def clearMemory():
    clearCommandMemory()
    clearProgramMemory()


def clearProgramMemory():
    global _programParts
    _programParts = [0]


def clearCommandMemory():
    global _commandPointer
    _commandPointer = 0


def retainInTemporary():
    global _temporaryCommandPointer, _temporaryProgramParts, _temporaryProgramArray

    _temporaryCommandPointer = _commandPointer
    _temporaryProgramParts = _programParts
    _temporaryProgramArray = _programArray


def loadFromTemporary():
    global _commandPointer, _programParts, _programArray

    _commandPointer = _temporaryCommandPointer
    _programParts = _temporaryProgramParts
    _programArray = _temporaryProgramArray



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
        callback = checkButtons
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
    global _pressedList, _pressedListIndex

    pressed = 0

    for i in range(10):
        # pseudo pull-down                 # DEPRECATED: New PCB design (2.1) will resolve this.
        if _inputPin.value() == 1:         # DEPRECATED: New PCB design (2.1) will resolve this.
            _inputPin.init(Pin.OUT)        # DEPRECATED: New PCB design (2.1) will resolve this.
            _inputPin.off()                # DEPRECATED: New PCB design (2.1) will resolve this.
            _inputPin.init(Pin.IN)         # DEPRECATED: New PCB design (2.1) will resolve this.

        if _inputPin.value() == 1:
            pressed += 1 << _counterPosition # pow(2, _counterPosition)

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

    for pressed in _pressedList:
        count = _pressedList.count(pressed)

        if _pressLength <= count:
            return pressed

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
    global _processingProgram, _runningProgram

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

            if tupleWithCallable is None:                                   # Default branch
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
    global _commandArray, _commandPointer

    if _commandPointer < len(_commandArray):
        _commandArray[_commandPointer] = command
    else:
        _commandArray.append(command)

    _commandPointer += 1



################################
## HELPER METHODS FOR BLOCKS

def _blockStarted(newMapping):
    global _blockStartIndex, _currentMapping

    _blockStartStack.append(_blockStartIndex)
    _blockStartIndex = _commandPointer
    _mappingsStack.append(_currentMapping)
    _currentMapping  = newMapping
    buzzer.setDefaultState(1)
    buzzer.keyBeep("started")


def _blockCompleted(deleteFlag):
    global _commandPointer, _blockStartIndex, _currentMapping

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
    boundary = _commandArray[commandPointer]

    for boundaryPair in _blockBoundaries:
        if boundary == boundaryPair[0]:
            return boundaryPair[1]
        elif boundary == boundaryPair[1]:
            return boundaryPair[0]
    return -1


def _isTagBoundary(commandPointer):
    return _commandArray[commandPointer] == _getOppositeBoundary(commandPointer)



################################
## STANDARDIZED FUNCTIONS

def _start(arguments):                # (blockLevel,)
    global _processingProgram, _runningProgram

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
    logger.logCommandsAndProgram()

    motor.setCallback(0, _callbackEnd)

    #counter = 0                                   #    Debug
    #print("_toPlay[:_pointer]", "_toPlay[_pointer:]", "\t\t\t", "counter", "_pointer", "_toPlay[_pointer]") # Debug

    while _processingProgram:
        remaining = _upperBoundary - 1 - _pointer #    Remaining bytes in _toPlay bytearray. 0 if _toPlay[_pointer] == _toPlay[-1]
        checkCounter = False

        if remaining < 0:                         #    If everything is executed, exits.
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

        _pointer += 1

    _processingProgram = False

    _startButtonChecking()
    return 0


# COMMAND AND PROGRAM ARRAY

def _addToProgOrSave():
    global _commandPointer, _programArray

    if _commandPointer != 0:
        for i in range(_commandPointer):
            if _programParts[-1] + i < len(_programArray):
                _programArray[_programParts[-1] + i] = _commandArray[i]
            else:
                _programArray.append(_commandArray[i])

        _programParts.append(_programParts[-1] + _commandPointer)
        _commandPointer = 0
        buzzer.keyBeep("added")
    elif _programParts[-1] != 0:
        saveLoadedProgram()
        buzzer.keyBeep("saved")

    return 0


# LOOP

def _createLoop(arguments):                 # (creationState,)                40 [statements...] 42 [iteration count] 41
    global _currentMapping, _loopCounter

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
            buzzer.keyBeep("input_needed")
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
        buzzer.keyBeep("change_count")
    return 0


def _checkLoopCounter():
    global _loopChecking

    if _loopChecking == 2 or (_loopChecking == 1 and _loopCounter <= 20):
        buzzer.keyBeep("attention")
        buzzer.midiBeep(64, 100, 500, _loopCounter)
    else:
        buzzer.keyBeep("too_long")
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
        return 126, arguments[0] + 48, 126   # Increase by 48 = human-friendly bytes: 48 -> "0", 49 -> "1", ...
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
    global _commandPointer, _commandArray, _functionPosition

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
                _commandPointer -= 1                               # do...while loop can handle identical boundary pairs.
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
    global _commandPointer, _programParts, _functionPosition

    if arguments[0]:                        # Block-level: delete only the unfinished block.
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
    global _stepSignalSkipCount

    if _stepSignalEnabled and 0 == _stepSignalSkipCount and _stepSignal != "":
        buzzer.keyBeep(_stepSignal)
    else:
        _stepSignalSkipCount -= 1

    checkButtons()


def _callbackEnd():
    global _endSignalSkipCount, _runningProgram

    if _endSignalEnabled and 0 == _endSignalSkipCount and _endSignal != "":
        buzzer.keyBeep(_endSignal)
    else:
        _endSignalSkipCount -= 1

    _runningProgram   = False



################################
## MAPPINGS

# For turtle hat

_defaultMapping = {
    1:    (_beepAndReturn,     ("processed", 70)),                  # FORWARD
    2:    (_beepAndReturn,     ("processed", 80)),                  # PAUSE
    4:    (_createLoop,        (40,)),                              # REPEAT (start)
    6:    (_manageFunction,    (1, False)),                         # F1
    8:    (_addToProgOrSave,   ()),                                 # ADD
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

# For other purpose

_moveCharMapping = {
    70:  (1, _moveLength),  # "F" - FORWARD
    66:  (4, _moveLength),  # "B" - BACKWARD
    76:  (2, _turnLength),  # "L" - LEFT (90°)
    108: (2, _halfTurn),    # "l" - LEFT (45°)
    82:  (3, _turnLength),  # "R" - RIGHT (90°)
    114: (3, _halfTurn),    # "r" - RIGHT (45°)
    80:  (0, _moveLength),  # "P" - PAUSE
    75:  (2, _halfTurn),    # "K" - LEFT (45°)      alias for URL usage ( L - 1 = K   ~ l )
    81:  (3, _halfTurn)     # "Q" - RIGHT (45°)     alias for URL usage ( R - 1 = Q   ~ r )
}


################################
## LAST PART OF INITIALISATION

_currentMapping = _defaultMapping

motor.setCallback(0, _callbackEnd)
motor.setCallback(1, _callbackStep)

_startButtonChecking()

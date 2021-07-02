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

from machine import Pin, PWM, Timer


_active = 0
_pin    = 0
_pwm    = 0
_config = 0
_factor = 0
_breath = 0

_timer      = Timer(-1)
_timerT1    = Timer(-1)
_timerMotor = [Timer(-1), Timer(-1)]
_processing = False
_moveList   = []
_resumeList = []
_callbacks  = [(), ()]



################################
## CONFIG

def config(motorPins, motorConfig):
    global _active
    global _pin
    global _pwm

    _active = (0 not in motorPins[0], 0 not in motorPins[1])

    _pin = (
        (Pin(motorPins[0][0], Pin.OUT), Pin(motorPins[0][1], Pin.OUT)) if _active[0] else (0, 0),
        (Pin(motorPins[1][0], Pin.OUT), Pin(motorPins[1][1], Pin.OUT)) if _active[1] else (0, 0)
    )

    _driveMotor(0)  # Set both pin off, if motor is active.
    _driveMotor(1)  # Set both pin off, if motor is active.

    if _active[1]:
        _pwm = (PWM(Pin(motorPins[1][0])), PWM(Pin(motorPins[1][1])))

    configMotor(motorConfig)


def configMotor(motorConfig):
    global _config
    global _breath
    """
    Parameter motorConfig consists of three tuples: T0 timer setting, T1 PWM setting, T1 duty factor and borders.
    The third of the three tuple is modified:
        - The T1 duty factor extracted into a "dedicated" variable (_factor) by setFactor().
        - From the given minimum duty and initial duty calculates the minimum duty factor (_config[2][0]).
        - From the given maximum duty and initial duty calculates the maximum duty factor (_config[2][1]).


    The starting point (motorConfig):

          T0 - RIGHT MOTOR |     T1 - LEFT MOTOR - PWM (and finetuning)      | Pause length  |
          Timer based ctrl | PWM setting |          Fine tuning settings     | between moves |
            (~freq, ~duty) |             |                                   |               |
        ((period, duration), (freq, duty), (duty factor, min. duty, max. duty), breath length)


    The result (_config):

          T0 - RIGHT MOTOR |     T1 - LEFT MOTOR - PWM (and finetuning)       |
          Timer based ctrl | PWM setting |          Fine tuning settings      |
            (~freq, ~duty) |             |                                    |
        ((period, duration), (freq, duty), (min. duty factor, max. duty factor))
    """

    _config = (
        motorConfig[0],
        motorConfig[1],
        (motorConfig[2][1] / motorConfig[1][1], motorConfig[2][2] / motorConfig[1][1])
    )

    setFactor(motorConfig[2][0])

    """ The fourth element of the motorConfig is _breath, the pause between movements. Use case: turtle mode """
    _breath = motorConfig[3]



################################
## PUBLIC METHODS

def move(direction = 0, duration = 0):
    """
    Public function which books a move tuple (direction, duration)
    on _moveList for the indirect, future processing.

    direction   : integer parameter
    0           : STOP
    1           : FORWARD
    2           : LEFT
    3           : RIGHT
    4           : BACKWARD

    duration    : integer parameter (length of movement in millisecond)
    """
    _moveList.append((direction, duration))
    _startProcessing()


def stop():
    global _moveList
    global _resumeList
    """
    "Copy" pending move tuples to _resumeList and
    "clears" the _moveList, so pending move tuples
    will not be processed (now).
    """
    _stopProcessing()
    _resumeList = _moveList
    _moveList   = []                # Reassign instead of clear() method!


def resume():
    global _moveList
    global _resumeList
    """
    "Copy" back move tuples to _moveList from _resumeList,
    "clears" the _resumeList, and start the processing.
    """
    if not _processing:
        _moveList   = _resumeList
        _resumeList = []            # Reassign instead of clear() method!
        _startProcessing()


def setFactor(factor = 1):
    global _factor
    """
    Public function which set the T1 duty factor (_factor).
    This affects the left motor (T1) directly as you can see in _setController().
    The purpose of this function the on-the-fly correction.
    """
    if factor < _config[2][0]:         # If parameter is less than the minimum duty factor:
        _factor = _config[2][0]        #   - set the minimum duty f. as current duty f.
        return _config[2][0] - factor  #   - return the difference (as a negative number)
    elif _config[2][1] < factor:       # If the parameter is more than the maximum duty factor:
        _factor = _config[2][1]        #   - set the maximum duty f. as current duty f.
        return factor - _config[2][1]  #   - return the difference (as a positive number)
    else:
        _factor = factor
        return 0


def setCallback(slot, callbackFunction, isTemporary = False):
    global _callbacks
    """
    Setter for callbacks.

    slot : integer parameter
    0    : After processing every item on _moveList, _stopAndNext() will call this.
    1    : After every processed
    2    : backward    After processing every item on _moveList,
    _stopAndNext() will call _callbacks[0]. Use case: Beeps or other function
    after movements. If isTemporary is True, _stopAndNext() delete
    this after execution.
    """
    _callbacks[slot] = (callbackFunction, isTemporary)


def deleteCallback(slot = 0):
    global _callbacks
    """ Delete the callback from the specified slot. """
    _callbacks[slot] = ()


def getBreath():
    """ Getter method for _breath that is the pause in ms between movements. Use case: turtle mode """
    return _breath


def setBreath(breathLength):
    global _breath
    """ Setter method for _breath that is the pause in ms between movements. Use case: turtle mode """
    _breath = breathLength


def isProcessing():
    return _processing



################################
## PRIVATE, HELPER METHODS

def _startProcessing():
    global _processing

    if 0 < len(_resumeList):
        _resumeList.clear()

    if not _processing and 0 < len(_moveList):
        _processing = True
        _processMove(_moveList.pop(0))


def _stopProcessing():
    global _processing

    _processing = False


def _processMove(move):       # ((direction, duration))
    """
    Part of a recursive loop: _processMove(move) - _stopAndInitNext() - _processNext() - _processMove(move) ...

    Sets the motors by _setController() according to the 'move' tuple: (direction, duration)
    After that it initialise a timer to terminate this move, and to continue processing _moveList.
    """
    if move[0] == 1:                # FORWARD
        _setController(1, 1)
    elif move[0] == 2:              # LEFT
        _setController(2, 1)
    elif move[0] == 3:              # RIGHT
        _setController(1, 2)
    elif move[0] == 4:              # BACKWARD
        _setController(2, 2)
    else:                           # STOP
        _setController(0, 0)


    _timer.init(                    # STOP AND NEXT
        period = move[1],
        mode = Timer.ONE_SHOT,
        callback = _stopAndInitNext
    )


def _stopAndInitNext(timer):
    """
    Part of a recursive loop: _processMove(move) - _stopAndInitNext() - _processNext() - _processMove(move) ...

    Stops the current, done task (movement), calls the callback and indirectly calls _processNext() (after a while).
    """
    _setController(0, 0)
    _callCallback(1)

    if 0 == _breath:
        _processNext()
    else:
        _timer.init(                    # STOP AND NEXT
            period = _breath,
            mode = Timer.ONE_SHOT,
            callback = _processNext
        )


def _processNext(timer = None):
    """
    Part of a recursive loop: _processMove(move) - _stopAndInitNext() - _processNext() - _processMove(move) ...

    Checks if processing is active and there is any task waiting for processing.
    If it finds task(s), pops the first and call _processMove(move). If not, loop stops.
    """
    if _processing and 0 < len(_moveList):
        _processMove(_moveList.pop(0))
    else:
        _stopProcessing()
        _callCallback(0)


def _callCallback(slot = 1):
    global _callbacks
    """ Helper method for calling and managing callbacks. """

    if _callbacks[slot] != ():
        _callbacks[slot][0]()
        if _callbacks[slot][1]:
            _callbacks[slot] = ()


def _setController(modeLeft = 0, modeRight = 0):        # ! (T1 mode, T0 mode) ! because of clarity: (left, right)
    """
    Sets both motor in one go. (If both are active.)
    This setter is permanent,
    its only responsibility to handle PWM.

    mode : integer parameter
    0    : stop
    1    : forward
    2    : backward
    """

    if _active[1]:                                      # T1 - LEFT MOTOR - PWM
        if modeLeft == 0:
            _pwm[0].duty(0)
            _pwm[1].duty(0)
        else:
            duty = round(_factor * _config[1][1])       # Duty factor * initial duty
            _pwm[modeLeft - 1].freq(_config[1][0])
            _pwm[modeLeft - 1].duty(duty)

    if _active[0]:                                      # T0 - RIGHT MOTOR - Timer "PWM"
        if modeRight == 0:
            _timerT1.deinit()
            _driveMotor(0, 0)
        else:
            _timerT1.init(
                period = _config[0][0],
                mode = Timer.PERIODIC,
                callback = lambda t: _driveMotor(0, modeRight, _config[0][1])
            )



def _driveMotor(motor = 0, mode = 0, duration = 0):
    """
    Low-level motor (temporary) setter

    motor : integer parameter
    0     : (M3, M6)   T0 terminal / RIGHT MOTOR
    1     : (M11, M14) T1 terminal / LEFT MOTOR

    mode  : integer parameter
    0     : (off, off)  -> STOP
    1     : (on,  off)  -> FORWARD
    2     : (off,  on)  -> BACKWARD

    duration : integer parameter (makes this setter temporary)
    """
    if _active[motor]:
        if mode != 0:
            _pin[motor][1 - mode].on()
            _pin[motor][abs(mode - 2)].off()

            _timerMotor[motor].init(
                period = duration,
                mode = Timer.ONE_SHOT,
                callback = lambda t: _driveMotor(motor, 0)
            )
        else:
            _pin[motor][0].off()
            _pin[motor][1].off()

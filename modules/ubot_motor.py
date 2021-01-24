from machine import Pin, Timer
from utime   import sleep_ms


_factor = 0
_config = 0

_active = 0
_pin    = 0

_timer      = Timer(-1)
_timerMove  = [Timer(-1), Timer(-1)]
_timerMotor = [Timer(-1), Timer(-1)]
_processing = False
_moveList   = []
_callback   = ()


################################
## CONFIG

def config(motorConfig, motorPins):
    global _active
    global _pin
    """
    T0 and T1 have been swapped, because it's more clear: motorPins = ((left pins), (right pins))
    config() swaps it back: T0 - right (index : 0); T1 - left (index : 1)
    """

    _active = (0 not in motorPins[1], 0 not in motorPins[0])

    _pin = (
        (Pin(motorPins[1][0], Pin.OUT), Pin(motorPins[1][1], Pin.OUT)) if _active[0] else (0, 0),   # _active has got the
        (Pin(motorPins[0][0], Pin.OUT), Pin(motorPins[0][1], Pin.OUT)) if _active[1] else (0, 0)    # right order!
    )

    if _active[0]:
        _pin[0][0].off()
        _pin[0][1].off()

    if _active[1]:
        _pin[1][0].off()
        _pin[1][1].off()

    configMotor(motorConfig)


def configMotor(motorConfig):
    global _factor
    global _config
    """
    Parameter motorConfig consists of three tuples:
    T1 (left) timer setting, T0 (right) timer setting, borders and duty factor.

    T0 and T1 have been swapped, because it's more clear: motorConfig = ((left), (right), (fine))

    configMotor() swaps it back:

        T0 - RIGHT MOTOR | T1 - LEFT MOTOR |             Finetuning              |
                         |                 |                                     |
        ( (period, duty),  (period, duty),   (min. duty, max. duty, init. factor))

    """
    _config = (motorConfig[1], motorConfig[0], motorConfig[2])

    """
    Duty factor extracted from the third tuple into a "dedicated" variable.
    """
    _factor = _config[2][2]



################################
## PUBLIC METHODS

def move(direction = 0, duration = 500):
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
    if not _processing:
        _stopAndNext()


"""
def setDutyFactor(dutyFactor):
    global _factor
    \"""
    Public function which set the dutyFactor (_factor).
    This affects the left motor (T1) directly as you can see in _setController().
    The purpose of this funtion the on-the-fly correction.
    \"""
    if dutyFactor < _config[2][0]:         # If parameter is less than the minimum duty factor:
        _factor = _config[2][0]            #   - set the minimum duty f. as current duty f.
        return _config[2][0] - dutyFactor  #   - return the difference (as a negative number)
    elif _config[2][1] < dutyFactor:       # If the parameter is more than the maximum duty factor:
        _factor = _config[2][1]            #   - set the maximum duty f. as current duty f.
        return dutyFactor - _config[2][1]  #   - return the difference (as a positive number)
    else:
        _factor = dutyFactor
        return 0
"""

def setCallback(callbackFunction, isTemporary = True):
    global _callback
    _callback = (callbackFunction, isTemporary)



################################
## PRIVATE, HELPER METHODS

def _stopAndNext():
    global _processing
    global _callback
    """
    Part of a recursive loop: _stopAndNext() - _processMove(move) - _stopAndNext() - ...

    Stops the current, done task (movement) and checks if there is any task waiting for processing.
    If it finds task(s), pops the first and call _processMove(move). If not, loop stops.
    """
    _setController(0, 0)

    if 0 < len(_moveList):
        _processing = True
        _processMove(_moveList.pop(0))
    else:
        _processing = False

        if _callback != ():
            _callback[0]()
            if _callback[1]:
                _callback = ()


def _processMove(move):       # ((direction, duration))
    """
    Part of a recursive loop: _stopAndNext() - _processMove(move) - _stopAndNext() - ...

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
        callback = lambda t:_stopAndNext()
    )


def _setController(modeLeft = 0, modeRight = 0):        # (T1 mode, T0 mode)
    global _active
    """
    Sets both motor in one go. (If both are active.)
    This setter is permanent,
    its only responsibility to handle PWM.
    """

    mode = (modeRight, modeLeft)                        # Switch to lower-level order: (left, right) -> (T0 = right, T1 = left)

    for motor in range(2):
        if _active[motor]:
            if mode[motor] == 0:
                _timerMove[motor].deinit()
                _driveMotor(motor, 0)
            else:
                _timerMove[motor].init(
                    period = _config[motor][0],
                    mode = Timer.PERIODIC,
                    callback = lambda t:_driveMotor(motor, mode[motor], _config[motor][1])
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
    if mode != 0:
        _pin[motor][1 - mode].on()
        _pin[motor][abs(mode - 2)].off()

        _timerMotor[motor].init(
            period = duration,
            mode = Timer.ONE_SHOT,
            callback = lambda t:_driveMotor(motor, 0)
        )
    else:
        _pin[motor][0].off()
        _pin[motor][1].off()

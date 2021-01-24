from machine import Pin, Timer
from utime   import sleep_ms

_period   = 0
_duty     = 0
_baseDuty = 0
_range    = 0
_ratio    = 0

_active = 0
_pin    = 0

_timer      = Timer(-1)
_timerMove  = Timer(-1)
_timerMotor = [Timer(-1), Timer(-1)]
_processing = False
_moveList   = []
_callback   = ()


################################
## CONFIG

def config(motorPins, motorConfig):
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

    _driveMotor(0)  # Set both pin off, if motor is active.
    _driveMotor(1)  # Set both pin off, if motor is active.

    configMotor(motorConfig)


def configMotor(motorConfig):
    global _period
    global _duty
    global _baseDuty
    global _range
    global _ratio
    """
    Parameter motorConfig is a tuple consists of:

        motorPeriod     :   Period time in ms for both motor (~ PWM frequency). _timerMove uses it in _setController.
        motorDuty       :   Tuple (left duty in ms, right duty in ms). (~ PWM duty)
        motorDutyRange  :   Tuple (min. duty in ms, max. duty in ms). setRatio uses it to prevent overrun.
        motorRatio      :   Double value which describes the ratio between T0 (right) and T1 (left).

    In motorDuty T0 and T1 have been swapped, because it's more clear: (left, right).
    """
    _period   = motorConfig[0]
    _duty     = [motorConfig[1][1], motorConfig[1][0]]
    _baseDuty = (motorConfig[1][1], motorConfig[1][0])
    _range    = motorConfig[2]
    _ratio    = motorConfig[3]

    if _ratio != 1:
        setRatio(ratio)



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


def setRatio(ratio):
    global _ratio
    global _duty
    """
    Public function which set the T0:T1 ratio (_ratio).
    This affects both motor by changing their duty.
    The purpose of this funtion the on-the-fly correction.
    """
    if 1 < ratio:
        factor = (ratio - 1) / 2
    elif 0 < ratio:
        factor = 0 - (((1 / ratio) - 1) / 2)
    else:
        return

    _duty[0] = round(_baseDuty[0] + _baseDuty[0] * factor)
    _duty[1] = round(_baseDuty[1] - _baseDuty[1] * factor)

    if 1 < ratio:
        if _range[1] < _duty[0]:
            _duty[0] = _range[1]

        if _duty[1] < _range[0]:
            _duty[1] = _range[0]
    else:
        if _range[1] < _duty[1]:
            _duty[1] = _range[1]

        if _duty[0] < _range[0]:
            _duty[0] = _range[0]

    _ratio = _duty[0] / _duty[1]
    return _ratio


def setCallback(callbackFunction, isTemporary = True):
    """
    Setter for callback. After processing every item on _moveList,
    _stopAndNext() will call this. Use case: Beeps or other function
    after movements. If isTemporary is True, _stopAndNext() delete
    this after execution.
    """
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
    """
    Sets both motor in one go. (If both are active.)
    This setter is permanent,
    its only responsibility to handle PWM.
    """

    if modeLeft == 0 and modeRight == 0:
        _timerMove.deinit()
        _driveMotor(0, 0)
        _driveMotor(1, 0)
    else:
        _timerMove.init(
            period = _period,
            mode = Timer.PERIODIC,
            callback = lambda t:_initMotors(((0, modeRight, _duty[0]), (1, modeLeft, _duty[1])))
        )


def _initMotors(config):
    """ Helper method for lambda in _setController() """
    _driveMotor(config[0][0], config[0][1], config[0][2])
    _driveMotor(config[1][0], config[1][1], config[1][2])


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
                callback = lambda t:_driveMotor(motor, 0)
            )
        else:
            _pin[motor][0].off()
            _pin[motor][1].off()

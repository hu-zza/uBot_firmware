from machine import Pin, PWM, Timer
from utime   import sleep_ms

class Motor():
    def _config(self, motorConfig):
        # T0 - RIGHT MOTOR |     T1 - LEFT MOTOR - PWM (and finetuning)       |
        # Timer based ctrl | PWM setting |          Fine tuning settings      |
        #   (~freq, ~duty) |             |                                    |
        # ((period, sleep), (freq, duty), (min. duty factor, max. duty factor))
        self._config = (
            motorConfig[0],
            motorConfig[1],
            (motorConfig[2][1] / motorConfig[1][1], motorConfig[2][2] / motorConfig[1][1])
        )

        # Extracted duty factor
        self._factor = motorConfig[2][0]

        # Parameter motorConfig consists of three tuples: T0 timer setting, T1 pwm setting, T1 duty factor and borders.
        #
        # The third of the three tuple is modified:
        #   - Duty factor extracted into a "dedicated" variable (self._factor).
        #   - From the given minimum duty and initial duty calculates the minimum duty factor (self._config[2][0]).
        #   - From the given maximum duty and initial duty calculates the maximum duty factor (self._config[2][1]).


    def __init__(self, motorConfig, motorPins):
        self._active = (0 not in motorPins[0], 0 not in motorPins[1])

        self._pin = (
            (Pin(motorPins[0][0], Pin.OUT), Pin(motorPins[0][1], Pin.OUT)) if self._active[0] else (0, 0),
            (Pin(motorPins[1][0], Pin.OUT), Pin(motorPins[1][1], Pin.OUT)) if self._active[1] else (0, 0)
        )

        if self._active[0]:
            self._pin[0][0].off()
            self._pin[0][1].off()

        if self._active[1]:
            self._pin[1][0].off()
            self._pin[1][1].off()

            self._timerT1 = Timer(-1)
            self._pwm = (PWM(Pin(motorPins[1][0])), PWM(Pin(motorPins[1][1])))

        self._timer  = Timer(-1)

        self._processing = False
        self._moveList   = []

        self._config(motorConfig)


    def _driveMotor(self, motor = 0, mode = 0, sleep = 0):
        """
        Low-level motor setter

        motor : integer parameter
        0     : (M3, M6)   T0 terminal / RIGHT MOTOR
        1     : (M11, M14) T1 terminal / LEFT MOTOR

        mode  : integer parameter
        0     : (off, off)  -> STOP
        1     : (on,  off)  -> FORWARD
        2     : (off,  on)  -> BACKWARD
        """
        if mode != 0:
            self._pin[motor][1 - mode].on()
            self._pin[motor][abs(mode - 2)].off()
            sleep_ms(sleep)

        self._pin[motor][0].off()
        self._pin[motor][1].off()


    def _setController(self, modeLeft = 0, modeRight = 0):          # (self, T1 mode, T0 mode)
        if self._active[1]:                                         # T1 - LEFT MOTOR
            if modeLeft == 0:
                self._pwm[0].duty(0)
                self._pwm[1].duty(0)
            else:
                duty = round(self._factor * self._config[1][1])     # Duty factor * initial duty
                self._pwm[modeLeft - 1].freq(self._config[1][0])
                self._pwm[modeLeft - 1].duty(duty)

        if self._active[0]:                                         # T0 - RIGHT MOTOR
            if modeRight == 0:
                self._timerT1.deinit()
                self._driveMotor(0, 0)
            else:
                self._timerT1.init(
                    period = self._config[0][0],
                    mode = Timer.PERIODIC,
                    callback = lambda t:self._driveMotor(0, modeRight, self._config[0][1])
                )


    def _stopAndNext(self):
        self._setController(0, 0)
        self._processing = False

        if 0 < len(self._moveList):
            self._processing = True
            self._processMove(self._moveList.pop(0))


    def _processMove(self, move):       # (self, (direction, duration))

        if move[0] == 1:                # FORWARD
            self._setController(1, 1)
        elif move[0] == 2:              # LEFT
            self._setController(2, 1)
        elif move[0] == 3:              # RIGHT
            self._setController(1, 2)
        elif move[0] == 4:              # BACKWARD
            self._setController(2, 2)

        # STOP
        self._timer.init(
            period = 0 if move[0] == 0 else move[1],    # immediately / after movement duration (move[1])
            mode = Timer.ONE_SHOT,
            callback = lambda t:self._stopAndNext()
        )


    def move(self, direction = 0, duration = 500):
        self._moveList.append((direction, duration))
        if 1 == len(self._moveList) and not self._processing:
            self._stopAndNext()


    def setDutyFactor(self, dutyFactor):
        if dutyFactor < self._config[2][0]:         # If parameter is less than the minimum duty factor:
            self._factor = self._config[2][0]       #   - set the minimum duty f. as current duty f.
            return self._config[2][0] - dutyFactor  #   - return the difference (as a negative number)
        elif self._config[2][1] < dutyFactor:       # If the parameter is more than the maximum duty factor:
            self._factor = self._config[2][1]       #   - set the maximum duty f. as current duty f.
            return dutyFactor - self._config[2][1]  #   - return the difference (as a positive number)
        else:
            self._factor = dutyFactor
            return 0

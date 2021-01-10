from machine import Pin, PWM, Timer
from utime   import sleep_ms

class Motor():
    def _config(self, motorConfig):
        # T0 - RIGHT MOTOR |        LEFT MOTOR - PWM (and finetuning)         |
        # Timer based ctrl | PWM setting |          Fine tuning settings      |
        #   (~freq, ~duty) |             |                                    |
        # ((period, sleep), (freq, duty), (min. duty factor, max. duty factor))
        self._cfg = (motorConfig[0],
                     motorConfig[1],
                     (motorConfig[2][1] / motorConfig[1][1], motorConfig[2][2] / motorConfig[1][1]))

        # Extracted duty factor
        self._fac = motorConfig[2][0]

        # Parameter motorConfig consists of three tuples: timer setting, pwm setting, duty factor and borders.
        #
        # The third of the three tuple is modified:
        #   - Duty factor extracted into a "dedicated" variable (self._fac).
        #   - From the given minimum duty and initial duty calculates the minimum duty factor (self._cfg[2][0]).
        #   - From the given maximum duty and initial duty calculates the maximum duty factor (self._cfg[2][1]).

    def __init__(self, motorConfig, m3, m6, m11, m14):
        self._mot = [[Pin(m3,  Pin.OUT), Pin(m6,  Pin.OUT)],
                     [Pin(m11, Pin.OUT), Pin(m14, Pin.OUT)]]
        self._mot[0][0].off()
        self._mot[0][1].off()
        self._mot[1][0].off()
        self._mot[1][1].off()

        self._pwm = [PWM(Pin(m11)), PWM(Pin(m14))]
        self._t0  = Timer(-1)
        self._t1  = Timer(-1)

        self._processing = False
        self._moveList   = []

        self._config(motorConfig)



    def _setMotor(self, motor = 0, mode = 0):
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

        if mode == 0:
            self._mot[motor][0].off()
            self._mot[motor][1].off()
        else:
            self._mot[motor][1 - mode].on()
            self._mot[motor][abs(mode - 2)].off()


    def _driveMotor(self, motor = 0, mode = 0, sleep = 0):
        if mode != 0:
            self._setMotor(motor, mode)
            sleep_ms(self._cfg[0][1])
        self._setMotor(motor, 0)


    def _setController(self, modeLeft = 0, modeRight = 0): # (self, T1, T0)
        if modeLeft == 0:                                  # T1 - LEFT MOTOR
            self._pwm[0].duty(0)
            self._pwm[1].duty(0)
            self._driveMotor(1, 0)
        else:
            duty = round(self._fac * self._cfg[1][1])       # Duty factor * initial duty
            self._pwm[modeLeft - 1].freq(self._cfg[1][0])
            self._pwm[modeLeft - 1].duty(duty)

        if modeRight == 0:                                  # T0 - RIGHT MOTOR
            self._t0.deinit()
            self._driveMotor(0, 0)
        else:
            self._t0.init(
                period = self._cfg[0][0],
                mode = Timer.PERIODIC,
                callback = lambda t:self._driveMotor(0, modeRight, self._cfg[0][1])
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
        self._t1.init(
            period = 0 if move[0] == 0 else move[1],    # immediately / after movement duration (move[1])
            mode = Timer.ONE_SHOT,
            callback = lambda t:self._stopAndNext()
        )


    def move(self, direction = 0, duration = 500):
        self._moveList.append((direction, duration))
        if 1 == len(self._moveList) and not self._processing:
            self._stopAndNext()


    def setDutyFactor(self, dutyFactor):
        if dutyFactor < self._cfg[2][0]:            # If parameter is less than the minimum duty factor:
            self._fac = self._cfg[2][0]             #   - set the minimum duty f. as current duty f.
            return self._cfg[2][0] - dutyFactor     #   - return the difference (as a negative number)
        elif self._cfg[2][1] < dutyFactor:          # If the parameter is more than the maximum duty factor:
            self._fac = self._cfg[2][1]             #   - set the maximum duty f. as current duty f.
            return dutyFactor - self._cfg[2][1]     #   - return the difference (as a positive number)
        else:
            self._fac = dutyFactor
            return 0

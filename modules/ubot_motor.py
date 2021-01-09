from machine import Pin, PWM, Timer
from utime   import sleep_ms

class Motor():
    def _config(self, motorConfig):
        #                LEFT MOTOR - PWM (and finetuning)        |   RIGHT MOTOR
        #           Fine tuning settings       | PWM init setting | Timer based ctrl
        #                                      |                  | (~freq, ~duty)
        # ((min. duty factor, max. duty factor), (freq, init duty), (timer, sleep))
        self._cfg = ((motorConfig[0][1] / motorConfig[1][1], motorConfig[0][2] / motorConfig[1][1]),
                     motorConfig[1],
                     motorConfig[2])

        # Extracted duty factor
        self._fac = motorConfig[0][0]

        # Parameter motorConfig consists of three tuples: duty factor and borders, pwm setting, timer setting.
        #
        # The first of the three tuple is modified:
        #   - Duty factor extracted into a "dedicated" variable.
        #   - From the given minimum duty and initial duty calculates the minimum duty factor (self._cfg[0][1]).
        #   - From the given maximum duty and initial duty calculates the maximum duty factor (self._cfg[0][2]).

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


    def _useMotor(self, motor = 0, mode = 0):
        if mode != 0:
            self._setMotor(motor, mode)
            sleep_ms(self._cfg[2][1])
        self._setMotor(motor, 0)


    def _setController(self, modeLeft = 0, modeRight = 0):
        if modeLeft == 0:
            self._pwm[0].duty(0)
            self._pwm[1].duty(0)
            self._useMotor(1, 0)
        else:
            duty = round(self._fac * self._cfg[1][1])       # Duty factor * initial duty
            self._pwm[modeLeft - 1].freq(self._cfg[1][0])
            self._pwm[modeLeft - 1].duty(duty)

        if modeRight == 0:
            self._t0.deinit()
            self._useMotor(0, 0)
        else:
            self._t0.init(period = self._cfg[2][0], mode = Timer.PERIODIC, callback = lambda t:self._useMotor(0, modeRight))



    def move(self, direction = 0, duration = 500):

        if direction == 1:              # FORWARD
            self._setController(1, 1)
        elif direction == 2:            # LEFT
            self._setController(2, 1)
        elif direction == 3:            # RIGHT
            self._setController(1, 2)
        elif direction == 4:            # BACKWARD
            self._setController(2, 2)

        if direction == 0:
            self._setController(0, 0)
        else:
            self._t1.init(period = duration, mode = Timer.ONE_SHOT, callback = lambda t:self._setController(0, 0))


    def setDutyFactor(self, dutyFactor):
        if dutyFactor < self._cfg[0][0]:            # If parameter is less than the minimum duty factor:
            self._fac = self._cfg[0][0]             #   - set the minimum duty f. as current duty f.
            return self._cfg[0][0] - dutyFactor     #   - return the difference (as a negative number)
        elif self._cfg[0][1] < dutyFactor:          # If the parameter is more than the maximum duty factor:
            self._fac = self._cfg[0][1]             #   - set the maximum duty f. as current duty f.
            return dutyFactor - self._cfg[0][1]     #   - return the difference (as a positive number)
        else:
            self._fac = dutyFactor
            return 0

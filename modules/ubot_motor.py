from machine import Pin, PWM, Timer
from utime   import sleep_ms

class Motor():

    def __init__(self, motorConfig, m3, m6, m11, m14):
        self._cfg = motorConfig                             # [general T0:T1 ratio, timer, sleep, freq, duty]

        self._mot = [[Pin(m3,  Pin.OUT), Pin(m6,  Pin.OUT)],
                     [Pin(m11, Pin.OUT), Pin(m14, Pin.OUT)]]
        self._mot[0][0].off()
        self._mot[0][1].off()
        self._mot[1][0].off()
        self._mot[1][1].off()

        self._pwm  = [PWM(Pin(m11)), PWM(Pin(m14))]
        self._t0   = Timer(-1)
        self._t1   = Timer(-1)


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
            sleep_ms(self._cfg[2])
        self._setMotor(motor, 0)

    def _setController(self, modeLeft = 0, modeRight = 0):
        if modeRight == 0:
            self._t0.deinit()
            self._useMotor(0, 0)
        else:
            self._t0.init(period = self._cfg[1], mode = Timer.PERIODIC, callback = lambda t:self._useMotor(0, modeRight))

        if modeLeft == 0:
            self._pwm[0].duty(0)
            self._pwm[1].duty(0)
            self._useMotor(1, 0)
        else:
            self._pwm[modeLeft - 1].freq(self._cfg[3])
            self._pwm[modeLeft - 1].duty(self._cfg[4])


    def move(self, direction = 0, duration = 500):

        if direction == 1:              # FORWARD
            self._setController(1, 1)
        elif direction == 2:            # RIGHT
            self._setController(1, 2)
        elif direction == 3:            # LEFT
            self._setController(2, 1)
        elif direction == 4:            # BACKWARD
            self._setController(2, 2)

        if direction == 0:
            self._setController(0, 0)
        else:
            self._t1.init(period = duration, mode = Timer.ONE_SHOT, callback = lambda t:self._setController(0, 0))


    def config(motorConfig):
        self._cfg = motorConfig     # [general T0:T1 ratio, timer, sleep, freq, duty]

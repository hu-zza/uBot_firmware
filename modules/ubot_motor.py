from machine import Pin, PWM, Timer
from utime   import sleep_ms

class Motor():

    def __init__(self, motorConfig, m3, m6, m11, m14):
        self._cfg = motorConfig                             # [general T0:T1 ratio, timer, sleep, freq, duty]
        self._mot = [[m3, m6], [m11, m14]]
        self._t0  = Timer(-1)
        self._t1  = Timer(-1)

    def _setMotor(self, mode = 0):
        """
        Low-level motor setter

        mode  : integer parameter
        0     : (off, off)  -> STOP
        1     : (on,  off)  -> FORWARD
        2     : (off,  on)  -> BACKWARD
        """

        if mode == 0:
            self._mot[0][0].off()
            self._mot[0][1].off()
        else:
            self._mot[0][1 - mode].on()
            self._mot[0][abs(mode - 2)].off()

    def _useMotor(self, mode = 0):
        self._setMotor(mode)
        sleep_ms(self._cfg[2])
        self._setMotor()

    def _setController(self, modeRight, modeLeft):
            self._t0.init(period = self._cfg[1], mode = Timer.PERIODIC, callback = lambda t:self._useMotor(modeRight, ))
            self._setMotor(0, modeRight)
            self._setMotor(1, modeLeft)


    def move(self, direction = 0, duration = 1000):

        if direction == 1:              # FORWARD
            self._setController(1, 1)
        elif direction == 2:            # RIGHT
            self._setController(1, 2)
        elif direction == 3:            # LEFT
            self._setController(2, 1)
        elif direction == 4:            # BACKWARD
            self._setController(2, 2)

        if direction != 0:
            sleep_ms(duration)
            self._setController(0, 0)

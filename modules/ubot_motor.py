from machine import Pin
from utime   import sleep_ms

class Motor():

    def __init__(self, m3, m6, m11, m14):
        self._mot = [[m3, m6], [m11, m14]]

    def _setMotor(self, motor = 0, mode = 0):
        """
        Low-level motor setter

        motor : integer parameter
        0     : (M3, M6)   T0 terminal / RIGHT MOTOR
        1     : (M11, M14) T1 terminal / LEFT MOTOR

        mode  : integer parameter
        0     : (off, off)  -> STOP
        1     : (on, off)   -> FORWARD
        2     : (off, on)   -> BACKWARD
        """

        if mode == 0:
            self._mot[motor][0].off()
            self._mot[motor][1].off()
        else:
            self._mot[motor][1 - mode].on()
            self._mot[motor][abs(mode - 2)].off()


    def _setController(self, modeRight, modeLeft):
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

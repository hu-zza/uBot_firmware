from machine import Pin, PWM
from utime   import sleep_ms, sleep_us

class Buzzer(PWM):                                                              # TODO: task list?

    def __init__(self, pin, freq, duty, buzzerActive):
        super().__init__(pin, freq, duty)
        self._defaultState = 0
        self._buzzerActive = buzzerActive


    def setDefaultState(self, value = 0):
        self._defaultState = value
        if value == 0:
            self.duty(0)
        else:
            self.duty(1023)            


    def beep(self, freq = 440.0, duration = 100, restAround = 100, count = 1):
        for i in range(count):
            self.duty(0)
            sleep_ms(restAround)

            if self._buzzerActive:
                self.freq(round(freq))
                self.duty(512)
                sleep_us(round((1000000 / freq) * (freq * duration / 1000 )))
                self.duty(0)
            else:
                self.duty(1023)
                sleep_ms(duration)
                self.duty(0)

            sleep_ms(restAround)

        if self._defaultState == 1:
            self.duty(1023)


    def midiBeep(self, noteOn = 69, duration = 100, restAround = 100, count = 1):
        f = 440 * pow(2, (noteOn - 69) / 12)
        self.beep(f, duration, restAround, count)


    def rest(self, duration = 100):
        self.duty(0)
        sleep_ms(duration)

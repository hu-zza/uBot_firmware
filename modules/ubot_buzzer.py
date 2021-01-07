from machine import Pin, PWM
from utime   import sleep_ms, sleep_us

class Buzzer(PWM):

    def __init__(self, pin, freq, duty, buzzerActive):
        super().__init__(pin, freq, duty)
        self._pin = pin
        self._buzzerActive = buzzerActive

    def beep(self, freq = 440.0, duration = 100, pause = 100, count = 1):

        for i in range(count):
            self._pin.off()

            if self._buzzerActive:
                self.freq(round(freq))
                self.duty(512)
                sleep_us(round((1000000 / freq) * (freq * duration / 1000 )))
                self.duty(0)
            else:
                self._pin.on()
                sleep_ms(duration)
                self._pin.off()

            sleep_ms(pause)


    def midiBeep(self, noteOn = 69, duration = 100, pause = 100, count = 1):
        f = 440 * pow(2, (noteOn - 69) / 12)
        self.beep(f, duration, pause, count)

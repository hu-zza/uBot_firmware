from machine import Pin, PWM
from utime   import sleep_ms, sleep_us

class Buzzer(PWM):

    def __init__(self, pin, freq, duty, buzzerActive):
        super().__init__(pin, freq, duty)
        self._pin = pin
        self._buzzerActive = buzzerActive

    def beep(self, freq = 262, duration = 3, pause = 10, count = 1):

        for i in range(count):
            self._pin.off()

            if self._buzzerActive:
                self.freq(freq)
                self.duty(512)

                rest = round((1000000 / freq) * (freq * duration / 10 ))
                sleep_us(rest)

                self.duty(0)
            else:
                self._pin.on()
                sleep_ms(duration * 100)
                self._pin.off()

            sleep_ms(pause * 10)


    def midiBeep(self, noteOn = 60, duration = 3, pause = 10, count = 1):
        f = round(440 * pow(2, (noteOn - 69) / 12))
        self.beep(f, duration, pause, count)

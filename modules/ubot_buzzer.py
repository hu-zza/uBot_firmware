from machine import Pin, PWM
from utime   import sleep_ms, sleep_us

class Buzzer(PWM):                                                              # TODO: task list?

    def __init__(self, pin, freq, duty, buzzerActive):
        super().__init__(pin, freq, duty)
        self._pin = pin
        self._initialPin = pin.value()
        self._buzzerActive = buzzerActive

    def beep(self, freq = 440.0, duration = 100, restAround = 100, count = 1):
        self._initialPin = self._pin.value()

        for i in range(count):
            self._pin.off()
            sleep_ms(restAround)

            if self._buzzerActive:
                self.freq(round(freq))
                self.duty(512)
                sleep_us(round((1000000 / freq) * (freq * duration / 1000 )))
                self.duty(0)
            else:
                self._pin.on()
                sleep_ms(duration)
                self._pin.off()

            sleep_ms(restAround)

        self._pin.value(self._initialPin)


    def midiBeep(self, noteOn = 69, duration = 100, restAround = 100, count = 1):
        f = 440 * pow(2, (noteOn - 69) / 12)
        self.beep(f, duration, restAround, count)


    def rest(self, duration = 100):
        self._pin.off()
        sleep_ms(duration)

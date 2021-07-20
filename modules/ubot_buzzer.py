"""
    uBot_firmware   // The firmware of the μBot, the educational floor robot. (A MicroPython port to ESP8266 with additional modules.)

    This file is part of uBot_firmware.
    [https://zza.hu/uBot_firmware]
    [https://git.zza.hu/uBot_firmware]


    MIT License

    Copyright (c) 2020-2021 Szabó László András // hu-zza

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

from machine import Pin, PWM
from utime   import sleep_ms

import ubot_config as config


_buzzerActive = config.get("buzzer", "active")
_pwm          = PWM(Pin(15), 0, 0)
_defaultState = 0


################################
## PUBLIC METHODS

def keyBeep(key: str) -> None:
    tuneList = config.get("buzzer", key)

    if tuneList is not None:
        if isinstance(tuneList[0], list):
            for tune in tuneList:
                if tune[0] is None:
                    rest(tune[1])
                else:
                    midiBeep(tune[0], tune[1], tune[2], tune[3])
        else:
            if tuneList[0] is None:
                rest(tuneList[1])
            else:
                midiBeep(tuneList[0], tuneList[1], tuneList[2], tuneList[3])


def midiBeep(noteOn: int = 69, duration: int = 100, restAround: int = 100, count: int = 1) -> None:
    freq = 440 * pow(2, (noteOn - 69) / 12)
    beep(freq, duration, restAround, count)


def beep(freq: float = 440.0, duration: int = 100, restAround: int = 100, count: int = 1) -> None:
    for i in range(count):
        rest(restAround)

        if _buzzerActive:
            _pwmBeep(freq, duration)
        else:
            _pwm.duty(1023)
            sleep_ms(duration)

        rest(restAround)


def rest(duration: int = 100) -> None:
    _pwm.duty(0)
    sleep_ms(duration)
    _setDutyByDefaultState()


def setDefaultState(value: int = 0) -> None:
    global _defaultState

    _defaultState = value
    _setDutyByDefaultState()


################################
## PRIVATE, HELPER METHODS

def _pwmBeep(freq: float = 440.0, duration: int = 100) -> None:
    _pwm.freq(round(freq))
    _pwm.duty(512)
    sleep_ms(duration)


def _setDutyByDefaultState() -> None:
    _pwm.duty(1023 * _defaultState)

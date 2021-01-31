import uos

from machine import Pin, PWM
from utime   import sleep_ms
from ujson   import loads

import ubot_config as config


_buzzerActive = config.get("buzzer", "active")
_pwm          = PWM(Pin(15), 0, 0)
_defaultState = 0



################################
## PUBLIC METHODS

def keyBeep(key):
    tuneList = config.get("buzzer", key)

    if tuneList != None:
        if isinstance(tuneList[0], list):
            for tune in tuneList:
                if tune[0] == None:
                    rest(tune[1])
                else:
                    midiBeep(tune[0], tune[1], tune[2], tune[3])
        else:
            if tuneList[0] == None:
                rest(tuneList[1])
            else:
                midiBeep(tuneList[0], tuneList[1], tuneList[2], tuneList[3])


def midiBeep(noteOn = 69, duration = 100, restAround = 100, count = 1):
        freq = 440 * pow(2, (noteOn - 69) / 12)
        beep(freq, duration, restAround, count)


def beep(freq = 440.0, duration = 100, restAround = 100, count = 1):
    for i in range(count):
        rest(restAround)

        if _buzzerActive:
            _pwmBeep(freq, duration)
        else:
            _pwm.duty(1023)
            sleep_ms(duration)

        rest(restAround)


def rest(duration = 100):
    _pwm.duty(0)
    sleep_ms(duration)
    _setDutyByDefaultState()


def setDefaultState(value = 0):
    global _defaultState

    _defaultState = value
    _setDutyByDefaultState()



################################
## PRIVATE, HELPER METHODS

def _pwmBeep(freq = 440.0, duration = 100):
    _pwm.freq(round(freq))
    _pwm.duty(512)
    sleep_ms(duration)


def _setDutyByDefaultState():
    _pwm.duty(1023 * _defaultState)

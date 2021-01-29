import uos

from machine import Pin, PWM
from utime   import sleep_ms
from ujson   import loads

import ubot_logger as logger


_config = [False, -1]

try:
    with open("etc/buzzer/configuration.txt") as file:
        _config = loads(file.readline())
except Exception as e:
    logger.append(e)

_buzzerActive = _config[0]
_pwm          = PWM(Pin(_config[1] if _config[1] != -1 else 15), 0, 0)
_defaultState = 0



################################
## PUBLIC METHODS

def keyBeep(key):
    beepFile = "{}.txt".format(key)

    if beepFile in uos.listdir("etc/buzzer"):
        try:
            with open("etc/buzzer/{}".format(beepFile)) as file:
                tuneList = loads(file.readline())

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
        except Exception as e:
            logger.append(e)

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
    _pwm.duty(1023 * _defaultState)


def setDefaultState(value = 0):
    global _defaultState

    _defaultState = value
    if value == 0:
        _pwm.duty(0)
    else:
        _pwm.duty(1023)



################################
## PRIVATE, HELPER METHODS

def _pwmBeep(freq = 440.0, duration = 100):
    _pwm.freq(round(freq))
    _pwm.duty(512)
    sleep_ms(duration)

from machine import Pin, PWM
from utime   import sleep_ms, sleep_us

_config       = 0
_pwm          = 0
_buzzerActive = 0
_defaultState = 0


def config(config):
    global _config
    global _pwm
    global _buzzerActive
    global _defaultState

    _config       = config
    _pwm          = PWM(Pin(config.get("buzzerPin")), 0, 0)
    _buzzerActive = config.get("buzzerActive")
    _defaultState = 0


def setDefaultState(value = 0):
    global _defaultState

    _defaultState = value
    if value == 0:
        _pwm.duty(0)
    else:
        _pwm.duty(1023)


def keyBeep(keyInConfigDictionary):
    tuneList = _config.get(keyInConfigDictionary)

    if tuneList != None:
        if isinstance(tuneList[0], tuple):
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
    else:
        midiBeep(64)


def rest(duration = 100):
    _pwm.duty(0)
    sleep_ms(duration)
    _pwm.duty(1023 * _defaultState)

def midiBeep(noteOn = 69, duration = 100, restAround = 100, count = 1):
    if noteOn == None:
        rest(duration)
    else:
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


def _pwmBeep(freq = 440.0, duration = 100):
    _pwm.freq(round(freq))
    _pwm.duty(512)
    sleep_ms(duration)

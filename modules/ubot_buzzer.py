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
    predefinedTune = _config.get(keyInConfigDictionary)

    if predefinedTune != None:
        tuneList = predefinedTune.split("#")
        for tune in tuneList:
            p = tune.split(":")
            midiBeep(int(p[0]), int(p[1]), int(p[2]), int(p[3]))
    else:
        midiBeep(64)


def rest(duration = 100):
    _pwm.duty(0)
    sleep_ms(duration)


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

    if _defaultState == 1:
        _pwm.duty(1023)


def _pwmBeep(freq = 440.0, duration = 100):
    _pwm.freq(round(freq))
    _pwm.duty(512)
    sleep_ms(duration)

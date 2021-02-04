from machine import Pin


_count = [0, 0]
_pin   = [0, 0]



################################
## PUBLIC METHODS

def init():
    global _pin

    if 0 in _pin:
        _pin[0] = Pin(12, Pin.IN, Pin.PULL_UP)
        _pin[1] = Pin(14, Pin.IN, Pin.PULL_UP)


def start():
    if 0 not in _pin:
        _pin[0].irq(_increaseT0)
        _pin[1].irq(_increaseT1)
    else:
        init()
        start()


def stop():
    if 0 not in _pin:
        _pin[0].irq(None)
        _pin[1].irq(None)


def deinit():
    global _pin

    if 0 not in _pin:
        for x in range(2):
            _pin[0].irq(None)
            del _pin[0]
        _pin = [0, 0]


def get():
    return _count


def clear():
    global _count

    _count = [0, 0]



################################
## PRIVATE, HELPER METHODS

def _increaseT0(pin):
    _increase(0)


def _increaseT1(pin):
    _increase(1)


def _increase(index):
    global _count

    _count[index] += 1

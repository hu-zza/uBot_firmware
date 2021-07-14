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

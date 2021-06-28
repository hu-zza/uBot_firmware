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

import math

from machine import I2C, Pin
from smbus   import SMBus
from lsm303  import LSM303
from utime   import sleep_ms


_I2C    = 0
_MAP    = 0
_LSM303 = 0

_referenceRangeXY =  409500 / 1100
_referenceRangeZ  =  409500 / 980
_referenceMinXY   = -204800 / 1100
_referenceMinZ    = -204800 / 980
_rawMinimumTuple  = ()
_rawMaximumTuple  = ()
_rawRangeX = 0
_rawRangeY = 0
_rawRangeZ = 0

################################
## CONFIG

def config(freq, SDA, SCL):
    global _I2C
    global _MAP
    global _LSM303


    _SDA = Pin(SDA)
    _SCL = Pin(SCL)
    _I2C = I2C(freq = freq, sda = _SDA, scl = _SCL)
    _MAP = _I2C.scan()

    if 0 < len(_MAP):
        _LSM303 = LSM303(SMBus(freq = freq, sda = _SDA, scl = _SCL))


def calibrate(duration):
    if _LSM303 != 0:
        magData = _LSM303.read_mag()
        minimumTuple = maximumTuple = (magData[0], magData[1], magData[2])

        for i in range(duration * 100):
            sleep_ms(10)
            magData = _LSM303.read_mag()

            minimumTuple = (
                magData[0] if magData[0] < minimumTuple[0] else minimumTuple[0],
                magData[1] if magData[1] < minimumTuple[1] else minimumTuple[1],
                magData[2] if magData[2] < minimumTuple[2] else minimumTuple[2]
            )

            maximumTuple = (
                magData[0] if magData[0] > maximumTuple[0] else maximumTuple[0],
                magData[1] if magData[1] > maximumTuple[1] else maximumTuple[1],
                magData[2] if magData[2] > maximumTuple[2] else maximumTuple[2]
            )

        setMinMaxTuples(minimumTuple, maximumTuple)
        return minimumTuple, maximumTuple
    else:
        return ()


def setMinMaxTuples(minimumTuple, maximumTuple):
    global _rawMinimumTuple
    global _rawMaximumTuple
    global _rawRangeX
    global _rawRangeY
    global _rawRangeZ

    _rawMinimumTuple = minimumTuple
    _rawMaximumTuple = maximumTuple

    if minimumTuple != () and maximumTuple != ():
        _rawRangeX = _rawMaximumTuple[0] - _rawMinimumTuple[0]
        _rawRangeY = _rawMaximumTuple[1] - _rawMinimumTuple[1]
        _rawRangeZ = _rawMaximumTuple[2] - _rawMinimumTuple[2]


def getCorrectedMag():
    if _rawMinimumTuple == () or _rawMaximumTuple == ():
        return ()
    else:
        rawData = _readMag()

        if rawData != ():
            return (
                (((rawData[0] - _rawMinimumTuple[0]) * _referenceRangeXY) / _rawRangeX) + _referenceMinXY,
                (((rawData[1] - _rawMinimumTuple[1]) * _referenceRangeXY) / _rawRangeY) + _referenceMinXY,
                (((rawData[2] - _rawMinimumTuple[2]) * _referenceRangeZ)  / _rawRangeZ) + _referenceMinZ
            )
        else:
            return ()



def getHeading():
    accumulated = [0, 0]    # X and Y
    for i in range(10):
        magData = getCorrectedMag()
        accumulated[0] += magData[0]
        accumulated[1] += magData[1]
        sleep_ms(10)

    avg = (accumulated[0] / 10, accumulated[1] / 10)

    if avg[0] == 0:
        if avg[1] < 0:
            return 90
        elif 0 < avg[1]:
            return 270
    else:
        if avg[0] < 0:
            return 180 + math.atan(avg[1] / avg[0])
        else:
            if 0 <= avg[1]:
                return math.atan(avg[1] / avg[0])
            else:
                return 360 + math.atan(avg[1] / avg[0])



################################
## TEST METHODS


def _readMag():
    if _LSM303 != 0:
        return _LSM303.read_mag()
    else:
        return ()



def _test():
    if _LSM303 != 0:
        acc_data = _LSM303.read_accel()
        mag_data = _LSM303.read_mag()
        return ((acc_data[0], acc_data[1], acc_data[2]),
                (mag_data[0], mag_data[1], mag_data[2]))



def _testLoop():
    if _LSM303 != 0:
        while True:
            acc_data = _LSM303.read_accel()
            mag_data = _LSM303.read_mag()
            print(
                [round(v, 2) for v in acc_data],
                [round(v, 2) for v in mag_data]
            )
            sleep_ms(100)

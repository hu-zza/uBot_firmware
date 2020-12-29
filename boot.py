essid = ""  # Set the WiFi name in the quotation marks.     For example: ESSID = "uBot_01"
passw = ""  # Set the WiFi password in the quotation marks. For example: PASSW = "uBot_01_pwd"


########################################################################################################################
########################################################################################################################


###########
## GPIO

from machine import Pin

SDA = Pin(0, Pin.OUT, 0)
SCL = Pin(2, Pin.OUT, 0)

MSG = Pin(15, Pin.OUT, 0)

CLK = Pin(13, Pin.OUT, 0)  #GPIO pin. Advances the counter (CD4017) which maps the buttons of the turtle HAT.
INP = Pin(16, Pin.OUT, 0)  #GPIO pin. Receives button presses from turtle HAT.
INP.init(Pin.IN)

P12 = Pin(12, Pin.OUT, 0)  #GPIO pin.
P14 = Pin(14, Pin.OUT, 0)  #GPIO pin.

MOT1 = Pin(1, Pin.OUT, 0)  #Connected to the  2nd pin of the motor driver (SN754410). Left motor.
MOT2 = Pin(3, Pin.OUT, 0)  #Connected to the  7th pin of the motor driver (SN754410). Left motor.
MOT3 = Pin(4, Pin.OUT, 0)  #Connected to the 10th pin of the motor driver (SN754410). Right motor.
MOT4 = Pin(5, Pin.OUT, 0)  #Connected to the 15th pin of the motor driver (SN754410). Right motor.


PIN = {
    "SDA" : SDA,
    "SCL" : SCL,

    "MSG" : MSG,

    "CLK" : CLK,
    "INP" : INP,

    "P12" : P12,
    "P14" : P14,

    "MOT1" : MOT1,
    "MOT2" : MOT2,
    "MOT3" : MOT3,
    "MOT4" : MOT4
}


###########
## AP

import network
from ubinascii import hexlify

AP = network.WLAN(network.AP_IF)
AP.active(True)
AP.ifconfig(("192.168.11.1", "255.255.255.0", "192.168.11.1", "192.168.11.1"))
AP.config(authmode = network.AUTH_WPA_WPA2_PSK)

# check variable essid existence
try:
    essid
except Exception:
    essid = ""

# if empty, set to default
if essid == "":
    essid = "uBot__" + hexlify(network.WLAN().config('mac'), ':').decode()[9:]

try:
    AP.config(essid = essid)
except Exception:
    AP.config(essid = "uBot")

# check variable passw existence
try:
    passw
except Exception:
    passw = ""

# if empty, set to default
if passw == "":
    passw = "uBot_pwd"

try:
    AP.config(password = passw)
except Exception:
    AP.config(password = "uBot_pwd")


###########
## SOCKET

import usocket

S = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
S.bind(("", 80))
S.listen(5)


###########
## AUDIO

# Frequencies for the buzzer

from micropython import const

NOTE_C4  = const(262)
NOTE_CS4 = const(277)
NOTE_D4  = const(294)
NOTE_DS4 = const(311)
NOTE_E4  = const(330)
NOTE_F4  = const(349)
NOTE_FS4 = const(370)
NOTE_G4  = const(392)
NOTE_GS4 = const(415)
NOTE_A4  = const(440)
NOTE_AS4 = const(466)
NOTE_B4  = const(494)
NOTE_C5  = const(523)


###########
## GENERAL

from machine import I2C, RTC, Timer, WDT, reset
from uio import FileIO
import esp, gc, ujson, utime, webrepl

gc.enable()
esp.sleep_type(esp.SLEEP_NONE)

T  = Timer(-1)
DT = RTC()
#WD = WDT()

IIC = I2C(freq=400000, sda=SDA, scl=SCL)
webrepl.start()

CONN = ""
ADDR = ""
COMMANDS = []

COUNTER_POS  = 0
COUNTER_ACC  = -1
PRESSED_BTNS = []

EXCEPTIONS = []

########################################################################################################################
########################################################################################################################

"""
micropython-smbus by Geoff Lee

[https://github.com/gkluoe/micropython-smbus]


MIT License

Copyright (c) 2017 Geoff Lee

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


class SMBus(I2C):
    """ Provides an 'SMBus' module which supports some of the py-smbus
        i2c methods, as well as being a subclass of machine.I2C
        Hopefully this will allow you to run code that was targeted at
        py-smbus unmodified on micropython.
	    Use it like you would the machine.I2C class:
            import usmbus.SMBus
            bus = SMBus(1, pins=('G15','G10'), baudrate=100000)
            bus.read_byte_data(addr, register)
            ... etc
	"""

    def read_byte_data(self, addr, register):
        """ Read a single byte from register of device at addr
            Returns a single byte """
        return self.readfrom_mem(addr, register, 1)[0]

    def read_i2c_block_data(self, addr, register, length):
        """ Read a block of length from register of device at addr
            Returns a bytes object filled with whatever was read """
        return self.readfrom_mem(addr, register, length)

    def write_byte_data(self, addr, register, data):
        """ Write a single byte from buffer `data` to register of device at addr
            Returns None """
        # writeto_mem() expects something it can treat as a buffer
        if isinstance(data, int):
            data = bytes([data])
        # ADDED: for the compatibility with lsm303-python
        else:
            data = bytearray([data[0]])
        return self.writeto_mem(addr, register, data)

    def write_i2c_block_data(self, addr, register, data):
        """ Write multiple bytes of data to register of device at addr
            Returns None """
        # writeto_mem() expects something it can treat as a buffer
        if isinstance(data, int):
            data = bytes([data])
        # ADDED: for the compatibility with lsm303-python
        else:
            data = bytearray([data[0]])
        return self.writeto_mem(addr, register, data)

    # The follwing haven't been implemented, but could be.
    def read_byte(self, *args, **kwargs):
        """ Not yet implemented """
        raise RuntimeError("Not yet implemented")

    def write_byte(self, *args, **kwargs):
        """ Not yet implemented """
        raise RuntimeError("Not yet implemented")

    def read_word_data(self, *args, **kwargs):
        """ Not yet implemented """
        raise RuntimeError("Not yet implemented")

    def write_word_data(self, *args, **kwargs):
        """ Not yet implemented """
        raise RuntimeError("Not yet implemented")



"""
lsm303-python by Jack Whittaker

[https://github.com/jackw01/lsm303-python]


MIT License

Copyright (c) 2020 Jack

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

#import smbus
#import struct
from ustruct import unpack
#import time

# MODIFIED ALL: const()
# MODIFIED: 0x19 -> 0x18 ... because of the non-genuine chip maybe
LSM303_ADDRESS_ACCEL                      = const(0x18) # 0011000x

LSM303_REGISTER_ACCEL_CTRL_REG1_A         = const(0x20)
#LSM303_REGISTER_ACCEL_CTRL_REG2_A         = const(0x21)
#LSM303_REGISTER_ACCEL_CTRL_REG3_A         = const(0x22)
LSM303_REGISTER_ACCEL_CTRL_REG4_A         = const(0x23)
#LSM303_REGISTER_ACCEL_CTRL_REG5_A         = const(0x24)
#LSM303_REGISTER_ACCEL_CTRL_REG6_A         = const(0x25)
#LSM303_REGISTER_ACCEL_REFERENCE_A         = const(0x26)
#LSM303_REGISTER_ACCEL_STATUS_REG_A        = const(0x27)
LSM303_REGISTER_ACCEL_OUT_X_L_A           = const(0x28)
#LSM303_REGISTER_ACCEL_OUT_X_H_A           = const(0x29)
#LSM303_REGISTER_ACCEL_OUT_Y_L_A           = const(0x2A)
#LSM303_REGISTER_ACCEL_OUT_Y_H_A           = const(0x2B)
#LSM303_REGISTER_ACCEL_OUT_Z_L_A           = const(0x2C)
#LSM303_REGISTER_ACCEL_OUT_Z_H_A           = const(0x2D)
#LSM303_REGISTER_ACCEL_FIFO_CTRL_REG_A     = const(0x2E)
#LSM303_REGISTER_ACCEL_FIFO_SRC_REG_A      = const(0x2F)
#LSM303_REGISTER_ACCEL_INT1_CFG_A          = const(0x30)
#LSM303_REGISTER_ACCEL_INT1_SOURCE_A       = const(0x31)
#LSM303_REGISTER_ACCEL_INT1_THS_A          = const(0x32)
#LSM303_REGISTER_ACCEL_INT1_DURATION_A     = const(0x33)
#LSM303_REGISTER_ACCEL_INT2_CFG_A          = const(0x34)
#LSM303_REGISTER_ACCEL_INT2_SOURCE_A       = const(0x35)
#LSM303_REGISTER_ACCEL_INT2_THS_A          = const(0x36)
#LSM303_REGISTER_ACCEL_INT2_DURATION_A     = const(0x37)
#LSM303_REGISTER_ACCEL_CLICK_CFG_A         = const(0x38)
#LSM303_REGISTER_ACCEL_CLICK_SRC_A         = const(0x39)
#LSM303_REGISTER_ACCEL_CLICK_THS_A         = const(0x3A)
#LSM303_REGISTER_ACCEL_TIME_LIMIT_A        = const(0x3B)
#LSM303_REGISTER_ACCEL_TIME_LATENCY_A      = const(0x3C)
#LSM303_REGISTER_ACCEL_TIME_WINDOW_A       = const(0x3D)

LSM303_ADDRESS_MAG                        = const(0x1E) # 0011110x
LSM303_REGISTER_MAG_CRA_REG_M             = const(0x00)
LSM303_REGISTER_MAG_CRB_REG_M             = const(0x01)
LSM303_REGISTER_MAG_MR_REG_M              = const(0x02)
LSM303_REGISTER_MAG_OUT_X_H_M             = const(0x03)
#LSM303_REGISTER_MAG_OUT_X_L_M             = const(0x04)
#LSM303_REGISTER_MAG_OUT_Z_H_M             = const(0x05)
#LSM303_REGISTER_MAG_OUT_Z_L_M             = const(0x06)
#LSM303_REGISTER_MAG_OUT_Y_H_M             = const(0x07)
#LSM303_REGISTER_MAG_OUT_Y_L_M             = const(0x08)
#LSM303_REGISTER_MAG_SR_REG_Mg             = const(0x09)
#LSM303_REGISTER_MAG_IRA_REG_M             = const(0x0A)
#LSM303_REGISTER_MAG_IRB_REG_M             = const(0x0B)
#LSM303_REGISTER_MAG_IRC_REG_M             = const(0x0C)
#LSM303_REGISTER_MAG_TEMP_OUT_H_M          = const(0x31)
#LSM303_REGISTER_MAG_TEMP_OUT_L_M          = const(0x32)

MAG_GAIN_1_3                              = const(0x20) # +/- 1.3
#MAG_GAIN_1_9                              = const(0x40) # +/- 1.9
#MAG_GAIN_2_5                              = const(0x60) # +/- 2.5
#MAG_GAIN_4_0                              = const(0x80) # +/- 4.0
#MAG_GAIN_4_7                              = const(0xA0) # +/- 4.7
#MAG_GAIN_5_6                              = const(0xC0) # +/- 5.6
#MAG_GAIN_8_1                              = const(0xE0) # +/- 8.1

#MAG_RATE_0_7                              = const(0x00) # 0.75 H
#MAG_RATE_1_5                              = const(0x01) # 1.5 Hz
#MAG_RATE_3_0                              = const(0x62) # 3.0 Hz
#MAG_RATE_7_5                              = const(0x03) # 7.5 Hz
#MAG_RATE_15                               = const(0x04) # 15 Hz
#MAG_RATE_30                               = const(0x05) # 30 Hz
#MAG_RATE_75                               = const(0x06) # 75 Hz
#MAG_RATE_220                              = const(0x07) # 210 Hz

ACCEL_MS2_PER_LSB = 0.00980665 # meters/second^2 per least significant bit

GAUSS_TO_MICROTESLA = 100.0

class LSM303(object):
    "LSM303 3-axis accelerometer/magnetometer"

    def __init__(self, i2c, hires=True):
        "Initialize the sensor"
        self._bus = i2c

        # Enable the accelerometer - all 3 channels
        self._bus.write_i2c_block_data(LSM303_ADDRESS_ACCEL,
                                       LSM303_REGISTER_ACCEL_CTRL_REG1_A,
                                       [0b01000111])

        # Select hi-res (12-bit) or low-res (10-bit) output mode.
        # Low-res mode uses less power and sustains a higher update rate,
        # output is padded to compatible 12-bit units.
        if hires:
            self._bus.write_i2c_block_data(LSM303_ADDRESS_ACCEL,
                                           LSM303_REGISTER_ACCEL_CTRL_REG4_A,
                                           [0b00001000])
        else:
            self._bus.write_i2c_block_data(LSM303_ADDRESS_ACCEL,
                                           LSM303_REGISTER_ACCEL_CTRL_REG4_A,
                                           [0b00000000])

        # Enable the magnetometer
        self._bus.write_i2c_block_data(LSM303_ADDRESS_MAG,
                                       LSM303_REGISTER_MAG_MR_REG_M,
                                       [0b00000000])

        self.set_mag_gain(MAG_GAIN_1_3)

    def read_accel(self):
        "Read raw acceleration in meters/second squared"
        # Read as signed 12-bit little endian values
        accel_bytes = self._bus.read_i2c_block_data(LSM303_ADDRESS_ACCEL,
                                                    LSM303_REGISTER_ACCEL_OUT_X_L_A | 0x80,
                                                    6)
        # MODIFIED : struct.unpack -> method import + unpack()
        accel_raw = unpack('<hhh', bytearray(accel_bytes))

        return (
            (accel_raw[0] >> 4) * ACCEL_MS2_PER_LSB,
            (accel_raw[1] >> 4) * ACCEL_MS2_PER_LSB,
            (accel_raw[2] >> 4) * ACCEL_MS2_PER_LSB,
        )

    def set_mag_gain(self, gain):
        "Set magnetometer gain"
        self._gain = gain
        if gain == MAG_GAIN_1_3:
            self._lsb_per_gauss_xy = 1100
            self._lsb_per_gauss_z = 980
#        elif gain == MAG_GAIN_1_9:
#            self._lsb_per_gauss_xy = 855
#            self._lsb_per_gauss_z = 760
#        elif gain == MAG_GAIN_2_5:
#            self._lsb_per_gauss_xy = 670
#            self._lsb_per_gauss_z = 600
#        elif gain == MAG_GAIN_4_0:
#            self._lsb_per_gauss_xy = 450
#            self._lsb_per_gauss_z = 400
#        elif gain == MAG_GAIN_4_7:
#            self._lsb_per_gauss_xy = 400
#            self._lsb_per_gauss_z = 355
#        elif gain == MAG_GAIN_5_6:
#            self._lsb_per_gauss_xy = 330
#            self._lsb_per_gauss_z = 295
#        elif gain == MAG_GAIN_8_1:
#            self._lsb_per_gauss_xy = 230
#            self._lsb_per_gauss_z = 205

        self._bus.write_i2c_block_data(LSM303_ADDRESS_MAG,
                                       LSM303_REGISTER_MAG_CRB_REG_M,
                                       [self._gain])

    def set_mag_rate(self, rate):
        "Set magnetometer rate"
        self._bus.write_i2c_block_data(LSM303_ADDRESS_MAG,
                                       LSM303_REGISTER_MAG_CRA_REG_M,
                                       [(rate & 0x07) << 2])

    def read_mag(self):
        "Read raw magnetic field in microtesla"
        # Read as signed 16-bit big endian values
        mag_bytes = self._bus.read_i2c_block_data(LSM303_ADDRESS_MAG,
                                                  LSM303_REGISTER_MAG_OUT_X_H_M,
                                                  6)
        # MODIFIED : struct.unpack -> method import + unpack()
        mag_raw = unpack('>hhh', bytearray(mag_bytes))

        return (
            mag_raw[0] / self._lsb_per_gauss_xy * GAUSS_TO_MICROTESLA,
            mag_raw[2] / self._lsb_per_gauss_xy * GAUSS_TO_MICROTESLA,
            mag_raw[1] / self._lsb_per_gauss_z * GAUSS_TO_MICROTESLA,
        )

def _test():
    bus = SMBus(freq=400000, sda=SDA, scl=SCL)
    device = LSM303(bus)
    while True:
        accel_data = device.read_accel()
        mag_data = device.read_mag()
        print(
            [round(v, 2) for v in accel_data],
            [round(v, 2) for v in mag_data]
        )
        utime.sleep(0.1)



LSM = LSM303(SMBus(freq=400000, sda=SDA, scl=SCL))

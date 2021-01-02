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

# MODIFIED: imports
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

# MODIFIED: excluded method _test()

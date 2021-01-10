from machine import I2C
from smbus   import SMBus
from lsm303  import LSM303
from utime   import sleep_ms

_I2C    = 0
_MAP    = 0
_LSM303 = 0


def config(freq, SDA, SCL):
    _I2C = I2C(freq=freq, sda=SDA, scl=SCL)
    _MAP = _I2C.scan()

    if 0 < len(_MAP):
        _LSM303 = LSM303(SMBus(freq=freq, sda=SDA, scl=SCL))

def _test():
    if 0 < len(_MAP):
        acc_data = _LSM303.read_accel()
        mag_data = _LSM303.read_mag()
        return ((acc_data[0], acc_data[1], acc_data[2]),
                (mag_data[0], mag_data[1], mag_data[2]))


def _testLoop():
    if 0 < len(_MAP):
        while True:
            acc_data = _LSM303.read_accel()
            mag_data = _LSM303.read_mag()
            print(
                [round(v, 2) for v in acc_data],
                [round(v, 2) for v in mag_data]
            )
            sleep_ms(100)

from machine import I2C
from smbus   import SMBus
from lsm303  import LSM303
from utime   import sleep_ms

class Feedback():

    def __init__(self, freq, SDA, SCL):
        self._I2C = I2C(freq=freq, sda=SDA, scl=SCL)
        self._MAP = self._I2C.scan()

        if 0 < len(self._MAP):
            self._LSM303 = LSM303(SMBus(freq=freq, sda=SDA, scl=SCL))

    def _test(self):
        if 0 < len(self._MAP):
            acc_data = self._LSM303.read_accel()
            mag_data = self._LSM303.read_mag()
            return ((acc_data[0], acc_data[1], acc_data[2]),
                    (mag_data[0], mag_data[1], mag_data[2]))


    def _testLoop(self):
        if 0 < len(self._MAP):
            while True:
                acc_data = self._LSM303.read_accel()
                mag_data = self._LSM303.read_mag()
                print(
                    [round(v, 2) for v in acc_data],
                    [round(v, 2) for v in mag_data]
                )
                sleep_ms(100)

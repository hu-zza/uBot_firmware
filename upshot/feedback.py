from machine    import I2C
from lib.smbus  import SMBus
from lib.lsm303 import LSM303

class Feedback():

    def __init__(self, freq, SDA, SCL):
        self._I2C = I2C(freq=freq, sda=SDA, scl=SCL)
        self._MAP = self._I2C.scan()

        if 0 < len(self._MAP):
            self._LSM303 = LSM303(SMBus(freq=freq, sda=SDA, scl=SCL))

    def _test(self):
        if 0 < len(self._MAP):
            while True:
                accel_data = self._LSM303.read_accel()
                mag_data   = self._LSM303.read_mag()
                print(
                    [round(v, 2) for v in accel_data],
                    [round(v, 2) for v in mag_data]
                )
                sleep_ms(100)

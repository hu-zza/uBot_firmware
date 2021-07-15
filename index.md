  
The firmware of the [μBot][uBot], the educational floor robot.  
(A [MicroPython][MP] port to [ESP8266][ESP] with additional modules.)  
  
## Design decisions

- Multifunctionality over processing speed 
  - Multiple interfaces
    - Physical buttons: standalone device
    - Web "server" with AP: easy and versatile
    - REST API: for the more advanced controlling
  - Detailed settings:
    - Highly customisable (even the beeps)
    - Dedicated module for convenience
    - Persistent storing
    - Factory reset
- Fail-safe exception handling
  - Intensive exception catching
  - Scalable logger with fallback mechanism
- Modularity
  - Are wireless connections unnecessary? Turn it off.
  - What about motors? ... Buzzer?
  - Turtle programming interface?
  - ...
  - Do you need UART and I2C? OK, use it.
  
  
## Setup

Well, this is exactly the same as you flash [MicroPython][MP] to your [ESP8266][ESP] with the help of this [detailed guide: Getting started with MicroPython on the ESP8266][setup]. This firmware is a [MicroPython][MP] port, so nothing new.  
  
The only difference this line you execute after erasing the flash:  
`esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 uBot_firmware_0.1.x.bin`  
*(Where `x` is the current patch version number.)* You find this binary file in [sandbox][sandbox].  
  
**But please note: This is a halfly documented, often error-prone (or buggy) pre-release for testing.**  
However, if you are brave enough, come on. ;-)


## Acknowledgements

I would like to thank Damien P. George, Paul Sokolovsky and all their contributors for [MicroPython][MP], Geoff Lee for the [micropython-smbus][SMBUS] and Jack Whittaker for the [lsm303-python][LSM303].


[uBot]: https://github.com/hu-zza/uBot
[ESP]: https://en.wikipedia.org/wiki/ESP8266
[MP]: https://github.com/micropython/micropython
[SMBUS]: https://github.com/gkluoe/micropython-smbus
[LSM303]: https://github.com/jackw01/lsm303-python


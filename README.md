
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
Soon...


## Acknowledgements

I would like to thank Damien P. George, Paul Sokolovsky and all their contributors for [MicroPython](https://github.com/micropython/micropython), Geoff Lee for the [micropython-smbus](https://github.com/gkluoe/micropython-smbus) and Jack Whittaker for the [lsm303-python](https://github.com/jackw01/lsm303-python).


[uBot]: https://github.com/hu-zza/uBot
[ESP]: https://en.wikipedia.org/wiki/ESP8266
[MP]: https://github.com/micropython/micropython

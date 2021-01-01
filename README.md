# μBot driver

The micropython driver files for ESP8266, which SoC is the heart of the μBot.


## Setup
1. [Getting started with MicroPython on the ESP8266](https://docs.micropython.org/en/latest/esp8266/tutorial/intro.html)

2. [Getting a MicroPython REPL prompt](https://docs.micropython.org/en/latest/esp8266/tutorial/repl.html)

3. Download [uBot_driver](https://github.com/hu-zza/uBot_driver/archive/main.zip) and unpack. 

4. Upload the [files](#filesToUpload) to the ESP8266 SoC through the WebREPL.

    - Open the online [WebREPL](https://micropython.org/webrepl/) or [download it](https://github.com/micropython/webrepl/archive/master.zip) and run **webrepl.html**.
    
    - Connect to WiFi **MicroPython-xxxxxx** with the password **micropythoN**.
        
    - On WebREPL press **Connect**, type your password which you have set ([2.2 WebREPL - a prompt over WiFi](https://docs.micropython.org/en/latest/esp8266/tutorial/repl.html#webrepl-a-prompt-over-wifi)).
    
    - With the form (**Send a file**) upload the [files](#filesToUpload) one by one.
    
    - Reboot the μBot by turning it off and on. 


## Files to upload <a name="filesToUpload"></a>
Every file (except README.md and folders of course) from the folder 'uBot_driver-main': boot.py, buzzer.py, config.py, ...


## Acknowledgements

I would like to thank Geoff Lee for the [micropython-smbus](https://github.com/gkluoe/micropython-smbus) and Jack Whittaker for the [lsm303-python](https://github.com/jackw01/lsm303-python).

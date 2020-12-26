#import esp
#esp.osdebug(None)

import uos, machine, gc, webrepl, network
#uos.dupterm(None,1) # disable REPL on UART(0)
gc.enable()
webrepl.start()

from machine import Pin
led = Pin(2, Pin.OUT)
led.value(1)

try:
  import usocket as socket
except:
  import socket

ap = network.WLAN(network.AP_IF)
ap.ifconfig(('192.168.11.1', '255.255.255.0', '192.168.11.1', '192.168.11.1'))
ap.config(authmode = network.AUTH_WPA_WPA2_PSK)
ap.config(essid = 'uBot_01')
ap.config(password = 'uBot_01_pwd')

# This file is executed on every boot (including wake-boot from deepsleep)

#import esp
#esp.osdebug(None)

from machine import Pin
import uos, machine, gc, webrepl
#uos.dupterm(None,1) # disable REPL on UART(0)
led = Pin(2, Pin.OUT)
gc.enable()
webrepl.start()

try:
  import usocket as socket
except:
  import socket
  
import network

#ssid = ''
#password = ''

#station = network.WLAN(network.STA_IF)

#station.active(True)
#station.connect(ssid, password)

#while station.isconnected() == False:
#  pass



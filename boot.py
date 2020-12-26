###########
## GENERAL


#import esp
#esp.osdebug(None)

import uos, machine, gc, webrepl, network, ujson, time
#uos.dupterm(None,1) # disable REPL on UART(0)
gc.enable()
webrepl.start()


###########
## AP

try:
  import usocket as socket
except:
  import socket

ap = network.WLAN(network.AP_IF)
ap.ifconfig(('192.168.11.1', '255.255.255.0', '192.168.11.1', '192.168.11.1'))
ap.config(authmode = network.AUTH_WPA_WPA2_PSK)
ap.config(essid = 'uBot_01')
ap.config(password = 'uBot_01_pwd')


###########
## GPIO

from machine import Pin

LED = Pin(2, Pin.OUT)
MSG = Pin(15, Pin.OUT)
LED.on()
MSG.off()

INP1 = Pin(12, Pin.IN, Pin.PULL_UP) #GPIO pin. Used to Charlieplexing on turtle HAT.
INP2 = Pin(13, Pin.IN, Pin.PULL_UP) #GPIO pin. Used to Charlieplexing on turtle HAT.
INP3 = Pin(14, Pin.IN, Pin.PULL_UP) #GPIO pin. Used to Charlieplexing on turtle HAT.
INP4 = Pin(16, Pin.OUT)             #GPIO pin. Used to Charlieplexing on turtle HAT.

MOT1 = Pin(1, Pin.OUT)  #Connected to the  2nd pin of the motor driver (SN754410). Left motor.
MOT2 = Pin(3, Pin.OUT)  #Connected to the  7th pin of the motor driver (SN754410). Left motor.
MOT3 = Pin(4, Pin.OUT)  #Connected to the 10th pin of the motor driver (SN754410). Right motor.
MOT4 = Pin(5, Pin.OUT)  #Connected to the 15th pin of the motor driver (SN754410). Right motor.
MOT1.off()
MOT2.off()
MOT3.off()
MOT4.off()

PIN = {
    "LED" : LED,
    "MSG" : MSG,

    "INP1" : INP1,
    "INP2" : INP2,
    "INP3" : INP3,
    "INP4" : INP4,

    "MOT1" : MOT1,
    "MOT2" : MOT2,
    "MOT3" : MOT3,
    "MOT4" : MOT4
}

###########
## AUDIO

# Frequencies for the buzzer

NOTE_C4  = 262
NOTE_CS4 = 277
NOTE_D4  = 294
NOTE_DS4 = 311
NOTE_E4  = 330
NOTE_F4  = 349
NOTE_FS4 = 370
NOTE_G4  = 392
NOTE_GS4 = 415
NOTE_A4  = 440
NOTE_AS4 = 466
NOTE_B4  = 494
NOTE_C5  = 523

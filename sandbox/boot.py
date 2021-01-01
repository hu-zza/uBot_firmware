import network, webrepl
from ubinascii import hexlify

AP = network.WLAN(network.AP_IF)
AP.active(True)
AP.ifconfig(("192.168.11.1", "255.255.255.0", "192.168.11.1", "192.168.11.1"))
AP.config(authmode = network.AUTH_WPA_WPA2_PSK)

essid = "uBot__" + hexlify(network.WLAN().config('mac'), ':').decode()[9:]
AP.config(essid = essid)
AP.config(password = "uBot_pwd")

webrepl.start()

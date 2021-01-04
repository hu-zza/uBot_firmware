import uos
import network
from flashbdev import bdev
from ubinascii import hexlify

ap = network.WLAN(network.AP_IF)

initialDateTime = "(2021, 1, 4, 0, 20, 8, 0, 0)"

# Config dictionary initialisation
config = {
    "version"         : "0.0.12",

    "apEssid"         : "uBot__" + hexlify(ap.config("mac"), ":").decode()[9:],
    "apPassword"      : "uBot_pwd",
    "replPassword"    : "uBot_REPL",

    "uart"            : False,
    "webRepl"         : False,
    "webServer"       : True,

    "turtleHat"       : True,
    "beepMode"        : True,

    "pressLength"     : 5,
    "firstRepeat"     : 25,

    "apActive"        : True,
    "wdActive"        : False,

    "i2cActive"       : True,
    "sda"             : 0,
    "scl"             : 2,
    "freq"            : 400000
}


########################################################################################################################

def wifi():
    ap.ifconfig(("192.168.11.1", "255.255.255.0", "192.168.11.1", "8.8.8.8"))
    ap.config(essid = config.get("apEssid"), authmode = network.AUTH_WPA_WPA2_PSK, password = config.get("apPassword"))


def check_bootsec():
    buf = bytearray(bdev.SEC_SIZE)
    bdev.readblocks(0, buf)
    empty = True
    for b in buf:
        if b != 0xFF:
            empty = False
            break
    if empty:
        return True
    fs_corrupted()


def fs_corrupted():
    import time

    while 1:
        print(
            """\
The filesystem starting at sector %d with size %d sectors appears to
be corrupted. If you had important data there, you may want to make a flash
snapshot to try to recover it. Otherwise, perform factory reprogramming
of MicroPython firmware (completely erase flash, followed by firmware
programming).
"""
            % (bdev.START_SEC, bdev.blocks)
        )
        time.sleep(3)




def saveDictionaryToFile(fileName, dictionary):
    with open("etc/." + fileName, "w") as file:
        for key in sorted([k for k in dictionary.keys()]):
            value = dictionary.get(key)
            if isinstance(value, str):
                file.write("{} = '{}'\n".format(key, value))
            else:
                file.write("{} = {}\n".format(key, value))



def setup():
    check_bootsec()
    wifi()
    uos.VfsLfs2.mkfs(bdev)
    vfs = uos.VfsLfs2(bdev)
    uos.mount(vfs, "/")

    uos.mkdir("etc")
    uos.mkdir("home")
    uos.mkdir("tmp")
    uos.mkdir("home/programs")
    uos.mkdir("tmp/programs")


    with open("webrepl_cfg.py", "w") as f:
        f.write("PASS = '{}'".format(config.get("replPassword")))


    with open("boot.py", "w") as f:

        f.write("# uBot firmware {}\n".format(config.get("version")))

        f.write((
            "import gc\n"
            "import ubot_firmware\n\n"

            "gc.enable()\n"
            "ubot_firmware.startWebServer()\n"
        ))


    with open("main.py", "w") as f:

        f.write("# uBot firmware {}\n".format(config.get("version")))

        f.write((
            "import gc\n"
            "import webrepl\n"

            "gc.enable()\n"
            "webrepl.start()\n"
        ))


    with open("etc/.datetime", "w") as f:
        f.write(initialDateTime)

    saveDictionaryToFile("config", config)
    saveDictionaryToFile("defaults", config)

    return vfs

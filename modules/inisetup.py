import uos
import network
from flashbdev import bdev
from ubinascii import hexlify

ap = network.WLAN(network.AP_IF)

# Config dictionary initialisation
config = {
    "firmwareVersion"   : "0.0.83",
    "initialDateTime"   : (2021, 1, 11, 0, 22, 30, 0, 0),

    "apActive"          : True,
    "apEssid"           : "uBot__" + hexlify(ap.config("mac"), ":").decode()[9:],
    "apPassword"        : "uBot_pwd",

    "webServerActive"   : True,

    "webReplActive"     : True,
    "webReplPassword"   : "uBot_REPL",

    "uartActive"        : True,
    "watchdogActive"    : False,

    "i2cActive"         : True,
    "i2cSda"            : 0,
    "i2cScl"            : 2,
    "i2cFreq"           : 400000,

    "buzzerActive"      : True,

    "motorT0Period"     : 10,
    "motorT0Sleep"      : 6,
    "motorT1Frequency"  : 1000,
    "motorT1Duty"       : 750,
    "motorT1DutyFactor" : 1.0,
    "motorT1MinDuty"    : 500,
    "motorT1MaxDuty"    : 1023,


    "turtleHatActive"   : True,
    "turtleMoveLength"  : 500,
    "turtleTurnLength"  : 400,
    "turtleBreathLength": 300,
    "turtlePauseLength" : 400,
    "turtleLoopChecking": 1,    #  0 - off  #  1 - simple (max. 20)  #  2 - simple (no limit)

    "turtleClockPin"    : 13,
    "turtleInputPin"    : 16,
    "turtleCheckPeriod" : 20,   # ms
    "turtlePressLength" : 5,    # min. 100 ms           turtlePressLength * turtleCheckPeriod
    "turtleFirstRepeat" : 75,   # min. 1500 ms          turtleFirstRepeat * turtleCheckPeriod
    "turtleMaxError"    : 1     # max. 0.166' (16,6'%)  turtleMaxError / (turtlePressLength + turtleMaxError)
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
    with open(fileName, "w") as file:
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
        f.write("PASS = '{}'".format(config.get("webReplPassword")))


    with open("boot.py", "w") as f:

        f.write("# uBot firmware {}\n".format(config.get("firmwareVersion")))
        f.write((
            "import gc\n"
            "import sys\n\n"
            "gc.enable()\n"
            "core = sys.modules.get('ubot_core')\n\n"

            "import ubot_core\n"
            "from ubot_debug import listExceptions, printException\n\n"
        ))


    with open("main.py", "w") as f:

        f.write("# uBot firmware {}\n".format(config.get("firmwareVersion")))
        f.write((
            "import gc\n"
            "import sys\n\n"
            "gc.enable()\n"
            "core = sys.modules.get('ubot_core')\n\n"

            "import ubot_debug\n"
            "from ubot_debug import listExceptions, printException, startUart, stopUart\n\n"
        ))


    with open("etc/datetime.py", "w") as f:
        f.write("DT = {}".format(config.get("initialDateTime")))

    saveDictionaryToFile("etc/config.py", config)
    saveDictionaryToFile("etc/defaults.py", config)

    return vfs

import uos
import network
from flashbdev import bdev
from ubinascii import hexlify

ap = network.WLAN(network.AP_IF)

# Config dictionary initialisation
config = {
    "firmwareMajor"     : 0,
    "firmwareMinor"     : 1,
    "firmwarePatch"     : 73,
    "initialDateTime"   : (2021, 1, 25, 0, 23, 15, 0, 0),
    "powerOnCount"      : 0,

    "apActive"          : True,
    "apEssid"           : "uBot__" + hexlify(ap.config("mac"), ":").decode()[9:],
    "apPassword"        : "uBot_pwd",

    "webServerActive"   : True,

    "webReplActive"     : True,
    "webReplPassword"   : "uBot_REPL",

    "uartActive"        : True,
    "watchdogActive"    : False,

    "i2cActive"         : False,
    "i2cSda"            : 0,
    "i2cScl"            : 2,
    "i2cFreq"           : 400000,

    "buzzerActive"      : True,
    "buzzerPin"         : 15,

    "motorConfig"       : [[10, 6], [1000, 750], [1.0, 500, 1023], 0],

    "feedbackMagMin"    : (),
    "feedbackMagMax"    : (),

    "beepStep"          : ((None, 200), (60, 50, 0, 1)),
    "beepReady"         : ((60, 100, 25, 3), (71, 500, 100, 1)),

    "beepProcessed"     : (64, 100, 0, 1),
    "beepAttention"     : ((60, 100, 25, 1), (64, 100, 25, 1), (71, 100, 25, 1), (None, 500)),

    "beepStarted"       : ((60, 300, 50, 1), (71, 100, 50, 1)),
    "beepInputNeeded"   : ((71, 100, 50, 2), (64, 100, 50, 1)),
    "beepCompleted"     : ((71, 300, 50, 1), (60, 100, 50, 1)),
    "beepUndone"        : ((71, 100, 25, 2), (None, 200)),
    "beepDeleted"       : ((71, 100, 25, 3), (60, 500, 100, 1), (None, 200)),

    "beepInAndDecrease" : (71, 100, 0, 1),
    "beepBoundary"      : (60, 500, 100, 2),
    "beepTooLong"       : (64, 1500, 100, 2),

    "beepAdded"         : ((71, 500, 50, 1), (64, 300, 50, 1), (60, 100, 50, 1)),
    "beepLoaded"        : ((60, 500, 50, 1), (64, 300, 50, 1), (71, 100, 50, 1)),


    "turtleActive"      : True,
    "turtleMoveLength"  : 890,
    "turtleTurnLength"  : 359,
    "turtleBreathLength": 500,
    "turtleLoopChecking": 1,    #  0 - off  #  1 - simple (max. 20)  #  2 - simple (no limit)
    "turtleStepSignal"  : "beepStep",
    "turtleEndSignal"   : "beepReady",

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
    uos.mkdir("program")
    uos.mkdir("log")
    uos.mkdir("log/commands")
    uos.mkdir("log/datetime")
    uos.mkdir("log/event")
    uos.mkdir("log/exception")
    uos.mkdir("log/program")

    with open("webrepl_cfg.py", "w") as file:
        file.write("PASS = '{}'".format(config.get("webReplPassword")))


    firmwareComment = "# uBot firmware {}.{}.{}\n\n".format(
        config.get("firmwareMajor"), config.get("firmwareMinor"), config.get("firmwarePatch")
    )

    gc = ("import gc\n"
          "gc.enable()\n\n")

    footerComment = ("#\n"
                     "# For more information:\n"
                     "#\n"
                     "# https://github.com/hu-zza/uBot\n"
                     "# https://ubot.hu\n"
                     "#\n")


    with open("boot.py", "w") as file:
        file.write(firmwareComment)
        file.write(gc + "import ubot_core as core\n\n")
        file.write(footerComment)


    with open("main.py", "w") as file:
        file.write(firmwareComment)
        file.write(gc + ("import sys\n"
                         "core = sys.modules.get('ubot_core')\n\n"
                         "import ubot_debug\n"
                         "from ubot_debug import listExceptions, printExceptions, startUart, stopUart, stopErrorSignal\n\n"
        ))
        file.write(footerComment)


    with open("etc/datetime.py", "w") as file:
        file.write("DT = {}".format(config.get("initialDateTime")))


    with open("log/datetime.txt", "w") as file:
        file.write("{}\n0000000000.txt\n\n".format(config.get("initialDateTime")))


    with open("log/exception/0000000000.txt", "w") as file:
        file.write("{}\nFallback exception log initialised successfully.\n\n".format(config.get("initialDateTime")))


    with open("log/event/0000000000.txt", "w") as file:
        file.write("{}\nFallback event log initialised successfully.\n\n".format(config.get("initialDateTime")))


    saveDictionaryToFile("etc/config.py", config)
    saveDictionaryToFile("etc/defaults.py", config)


    return vfs

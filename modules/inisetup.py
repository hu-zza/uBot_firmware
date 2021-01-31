import network, ujson, uos

from flashbdev import bdev
from ubinascii import hexlify


AP = network.WLAN(network.AP_IF)


################################
## CONFIG SUBDICTIONARIES

ap = {
    "active"        : True,
    "essid"         : "uBot__" + hexlify(AP.config("mac"), ":").decode()[9:],
    "password"      : "uBot_pwd"
}


buzzer = {
    "active"        : True,

    "step"          : ((None, 200), (60, 50, 0, 1)),
    "ready"         : ((60, 100, 25, 3), (71, 500, 100, 1)),

    "processed"     : (64, 100, 0, 1),
    "attention"     : ((60, 100, 25, 1), (64, 100, 25, 1), (71, 100, 25, 1), (None, 500)),

    "started"       : ((60, 300, 50, 1), (71, 100, 50, 1)),
    "inputNeeded"   : ((71, 100, 50, 2), (64, 100, 50, 1)),
    "completed"     : ((71, 300, 50, 1), (60, 100, 50, 1)),
    "undone"        : ((71, 100, 25, 2), (None, 200)),
    "deleted"       : ((71, 100, 25, 3), (60, 500, 100, 1), (None, 200)),

    "inAndDecrease" : (71, 100, 0, 1),
    "boundary"      : (60, 500, 100, 2),
    "tooLong"       : (64, 1500, 100, 2),

    "added"         : ((71, 500, 50, 1), (64, 300, 50, 1), (60, 100, 50, 1)),
    "loaded"        : ((60, 500, 50, 1), (64, 300, 50, 1), (71, 100, 50, 1))
}


i2c = {
    "active"        : False,
    "sda"           : 0,
    "scl"           : 2,
    "freq"          : 400000
}


motor = {
    "active"        : True,
    "T0Period"      : 10,
    "T0Duration"    : 6,
    "T1Frequency"   : 1000,
    "T1Duty"        : 750,
    "T1DutyFactor"  : 1.0,
    "T1MinDuty"     : 500,
    "T1MaxDuty"     : 1023,
    "breathLength"  : 0
}


system = {
    "firmware"      : (0, 1, 96),
    "initDateTime"  : (2021, 1, 31, 0, 16, 45, 0, 0),
    "powerOnCount"  : 0
}


turtle = {
    "active"        : True,
    "moveLength"    : 890,
    "turnLength"    : 359,
    "breathLength"  : 500,
    "loopChecking"  : 1,    #  0 - off  #  1 - simple (max. 20)  #  2 - simple (no limit)
    "stepSignal"    : "step",
    "endSignal"     : "ready",

    "checkPeriod"   : 20,   # ms
    "pressLength"   : 5,    # min. 100 ms           turtlePressLength * turtleCheckPeriod
    "firstRepeat"   : 75,   # min. 1500 ms          turtleFirstRepeat * turtleCheckPeriod
    "maxError"      : 1     # max. 0.166' (16,6'%)  turtleMaxError / (turtlePressLength + turtleMaxError)
}


uart = {
    "active"        : False
}


webServer = {
    "active"        : True
}


webRepl = {
    "active"        : False,
    "password"      : "uBot_REPL"
}


################################
## CONFIG DICTIONARY

configModules = {
    "ap"        : ap,
    "buzzer"    : buzzer,
    "i2c"       : i2c,
    "motor"     : motor,
    "system"    : system,
    "turtle"    : turtle,
    "uart"      : uart,
    "webRepl"   : webRepl,
    "webServer" : webServer
}


########################################################################################################################

def wifi():
    AP.ifconfig(("192.168.11.1", "255.255.255.0", "192.168.11.1", "8.8.8.8"))
    AP.config(essid = ap.get("essid"), authmode = network.AUTH_WPA_WPA2_PSK, password = ap.get("password"))


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



def setup():
    check_bootsec()
    wifi()
    uos.VfsLfs2.mkfs(bdev)
    vfs = uos.VfsLfs2(bdev)
    uos.mount(vfs, "/")


    uos.mkdir("etc")
    uos.mkdir("etc/ap")
    uos.mkdir("etc/buzzer")
    uos.mkdir("etc/i2c")
    uos.mkdir("etc/motor")
    uos.mkdir("etc/system")
    uos.mkdir("etc/turtle")
    uos.mkdir("etc/uart")
    uos.mkdir("etc/webRepl")
    uos.mkdir("etc/webServer")

    uos.mkdir("program")

    uos.mkdir("log")
    uos.mkdir("log/event")
    uos.mkdir("log/exception")
    uos.mkdir("log/object")

    uos.mkdir("log/executed")
    uos.mkdir("log/executed/commands")
    uos.mkdir("log/executed/datetime")
    uos.mkdir("log/executed/program")




    firmware = system.get("firmware")
    firmwareComment = "# uBot firmware {}.{}.{}\n\n".format(
        firmware[0], firmware[1], firmware[2]
    )

    gc = ("import gc\n"
          "gc.enable()\n\n")

    footerComment = ("#\n"
                     "# For more information:\n"
                     "#\n"
                     "# https://github.com/hu-zza/uBot\n"
                     "# https://ubot.hu\n"
                     "#\n")


    with open(".webrepl_cfg.py", "w") as file:
        file.write(firmwareComment)
        file.write("PASS = '{}'\n\n".format(webRepl.get("password")))
        file.write(footerComment)

    if webRepl.get("active"):
        uos.rename(".webrepl_cfg.py", "webrepl_cfg.py")


    with open("boot.py", "w") as file:
        file.write(firmwareComment)
        file.write(gc)
        file.write("import ubot_core as core\n\n")
        file.write(footerComment)


    with open("main.py", "w") as file:
        file.write(firmwareComment)
        file.write(gc)
        file.write(("import sys\n"
                    "core = sys.modules.get('ubot_core')\n\n"
                    "import ubot_debug\n"
                    "from ubot_debug import listExceptions, printExceptions, startUart, stopUart, stopSignal\n\n"
        ))
        file.write(footerComment)


    with open("etc/datetime.py", "w") as file:
        file.write("DT = {}".format(system.get("initDateTime")))


    with open("log/datetime.txt", "w") as file:
        file.write("{}\n0000000000.txt\n\n".format(system.get("initDateTime")))


    with open("log/exception/0000000000.txt", "w") as file:
        file.write("{}\nFallback exception log initialised successfully.\n\n".format(system.get("initDateTime")))


    with open("log/event/0000000000.txt", "w") as file:
        file.write("{}\nFallback event log initialised successfully.\n\n".format(system.get("initDateTime")))


    with open("log/object/0000000000.txt", "w") as file:
        file.write("{}\nFallback event log initialised successfully.\n\n".format(system.get("initDateTime")))


    for moduleName, module in configModules.items():
        for attrName, attrValue in module.items():
            with open("etc/{}/{}.txt".format(moduleName, attrName), "w") as file:
                file.write("{}\n".format(ujson.dumps(attrValue)))
            with open("etc/{}/{}.def".format(moduleName, attrName), "w") as file:
                file.write("{}\n".format(ujson.dumps(attrValue)))

    return vfs

import network, ujson, uos

from flashbdev import bdev
from ubinascii import hexlify

firmware = (0, 1, 148)
initDatetime = (2021, 7, 7, 0, 21, 40, 0, 0)

AP  = network.WLAN(network.AP_IF)
mac = hexlify(AP.config("mac"), ":").decode()

################################
## CONFIG SUBDICTIONARIES


ap = {
    "name"          : "Access point",
    "active"        : True,
    "ip"            : "192.168.11.1",
    "netmask"       : "255.255.255.0",
    "gateway"       : "192.168.11.1",
    "dns"           : "8.8.8.8",
    "mac"           : mac,
    "ssid"          : "uBot__" + mac[9:],
    "password"      : "uBot_pwd"
}

buzzer = {
    "name"          : "Buzzer",
    "active"        : True,

    "step"          : ((None, 200), (60, 50, 0, 1)),
    "ready"         : ((60, 100, 25, 3), (71, 500, 100, 1)),

    "processed"     : (64, 100, 0, 1),
    "attention"     : ((60, 100, 25, 1), (64, 100, 25, 1), (71, 100, 25, 1), (None, 500)),

    "started"       : ((60, 300, 50, 1), (71, 100, 50, 1)),
    "input_needed"  : ((71, 100, 50, 2), (64, 100, 50, 1)),
    "completed"     : ((71, 300, 50, 1), (60, 100, 50, 1)),
    "undone"        : ((71, 100, 25, 2), (None, 200)),
    "deleted"       : ((71, 100, 25, 3), (60, 500, 100, 1), (None, 200)),

    "change_count"  : (71, 100, 0, 1),
    "boundary"      : (60, 500, 100, 2),
    "tooLong"       : (64, 1500, 100, 2),

    "added"         : ((71, 500, 50, 1), (64, 300, 50, 1), (60, 100, 50, 1)),
    "loaded"        : ((60, 500, 50, 1), (64, 300, 50, 1), (71, 100, 50, 1)),
    "saved"         : ((64, 300, 50, 1), (64, 100, 50, 1), (64, 300, 50, 1))
}

constant = {
    "name"          : "Constant provider",
    "active"        : True,     # Just for unity
    "api_link"      : "https://zza.hu/uBot_API"
}


feedback = {
    "name"          : "Motion feedback",
    "active"        : False
}


i2c = {
    "name"          : "I2C Bus",
    "active"        : False,
    "sda"           : 0,
    "scl"           : 2,
    "freq"          : 400000
}


logger = {
    "name"          : "Logger",
    "active"        : True,
    "active_logs"   : ("Exception", "Event", "Object", "Run")    # All: ("Exception", "Event", "Object", "Run")
}


motor = {
    "name"          : "Motor driver",
    "active"        : True,
    "t0_period"     : 10,
    "t0_duration"   : 6,
    "t1_frequency"  : 1000,
    "t1_duty"       : 750,
    "t1_factor"     : 1.0,
    "t1_min_duty"   : 500,
    "t1_max_duty"   : 1023,
    "breath_length" : 0
}


system = {
    "name"          : "System",
    "active"        : True,     # Just for unity
    "id"            : hexlify(uos.urandom(32)).decode(),
    "chk"           : hexlify(uos.urandom(32)).decode(),
    "firmware"      : firmware,
    "init_datetime" : initDatetime,
    "power_ons"     : 0,
    "json_folders"  : ("etc", "program")
}


turtle = {
    "name"          : "Turtle",
    "active"        : True,
    "json_folder"   : "json",
    "turtle_folder" : "turtle",
    "move_length"   : 890,
    "turn_length"   : 359,
    "breath_length" : 500,
    "loop_checking" : 1,    #  0 - off  #  1 - simple (max. 20)  #  2 - simple (no limit)
    "step_signal"   : "step",
    "end_signal"    : "ready",

    "check_period"  : 20,   # ms
    "press_length"  : 5,    # min. 100 ms           press_length * check_period
    "first_repeat"  : 75,   # min. 1500 ms          first_repeat * check_period
    "max_error"     : 1,    # max. 0.166' (16,6'%)  max_error / (press_length + max_error)

    "move_chars"    : ["F", "B", "L", "l", "R", "r", "P", "K", "Q"],
    "turtle_chars"  : ["F", "B", "L", "l", "R", "r", "P", "K", "Q", "(", "*", ")", "{", "|", "}", "~"]

}


uart = {
    "name"          : "UART",
    "active"        : True
}


web_server = {
    "name"          : "Web server",
    "active"        : True,
    "period"        : 1000,
    "timeout"       : 750
}


web_repl = {
    "name"          : "MicroPython WebREPL",
    "active"        : False,
    "password"      : "uBot_REPL"
}


################################
## CONFIG DICTIONARY

configModules = {
    "ap"            : ap,
    "buzzer"        : buzzer,
    "constant"      : constant,
    "feedback"      : feedback,
    "i2c"           : i2c,
    "logger"        : logger,
    "motor"         : motor,
    "system"        : system,
    "turtle"        : turtle,
    "uart"          : uart,
    "web_repl"      : web_repl,
    "web_server"    : web_server
}


########################################################################################################################

def wifi():
    AP.ifconfig((ap.get("ip"), ap.get("netmask"), ap.get("gateway"), ap.get("dns")))
    AP.config(essid = ap.get("ssid"), authmode = network.AUTH_WPA_WPA2_PSK, password = ap.get("password"))


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

    uos.mkdir("/etc")

    uos.mkdir("/log")
    uos.mkdir("/log/event")
    uos.mkdir("/log/exception")
    uos.mkdir("/log/object")
    uos.mkdir("/log/run")

    uos.mkdir("/program")
    uos.mkdir("/program/turtle")
    uos.mkdir("/program/json")

    firmware = system.get("firmware")
    firmwareComment = "# uBot firmware {}.{}.{}\n\n".format(
        firmware[0], firmware[1], firmware[2]
    )

    gc = ("import gc\n"
          "gc.enable()\n\n")

    footerComment = ("#\n"
                     "# For more information:\n"
                     "#\n"
                     "# https://ubot.hu\n"
                     "# https://zza.hu/uBot\n"
                     "#\n")

    with open("/.webrepl_cfg.py", "w") as file:
        file.write(firmwareComment)
        file.write("PASS = '{}'\n\n".format(web_repl.get("password")))
        file.write(footerComment)

    if web_repl.get("active"):
        uos.rename("/.webrepl_cfg.py", "/webrepl_cfg.py")

    with open("/boot.py", "w") as file:
        file.write(firmwareComment)
        file.write(gc)
        file.write("import micropython\n"
                   "micropython.alloc_emergency_exception_buf(100)\n\n"
                   "import ubot_core as core\n\n")
        file.write(footerComment)

    with open("/main.py", "w") as file:
        file.write(firmwareComment)
        file.write(gc)
        file.write(("import usys\n"
                    "core = usys.modules.get('ubot_core')\n\n"))
        file.write(footerComment)

    with open("/etc/datetime.py", "w") as file:
        file.write("DT = {}".format(system.get("init_datetime")))

    with open("/log/datetime.txt", "w") as file:
        file.write("{}\n0000000000.txt\n\n".format(system.get("init_datetime")))

    with open("/log/exception/0000000000.txt", "w") as file:
        file.write("{}\nFallback exception log initialised successfully.\n\n".format(system.get("init_datetime")))

    with open("/log/event/0000000000.txt", "w") as file:
        file.write("{}\nFallback event log initialised successfully.\n\n".format(system.get("init_datetime")))

    with open("/log/object/0000000000.txt", "w") as file:
        file.write("{}\nFallback object log initialised successfully.\n\n".format(system.get("init_datetime")))

    with open("/log/run/0000000000.txt", "w") as file:
        file.write("{}\nFallback run log initialised successfully.\n\n".format(system.get("init_datetime")))

    for moduleName, module in configModules.items():
        uos.mkdir("/etc/{}".format(moduleName))
        for attrName, attrValue in module.items():
            with open("/etc/{}/{}.txt".format(moduleName, attrName), "w") as file:
                file.write("{}\n".format(ujson.dumps(attrValue)))
            with open("/etc/{}/{}.def".format(moduleName, attrName), "w") as file:
                file.write("{}\n".format(ujson.dumps(attrValue)))

    return vfs

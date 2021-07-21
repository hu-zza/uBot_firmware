import flashbdev, network, ubinascii, ujson, uos

firmware = (0, 1, 195)
initDatetime = (2021, 7, 21, 0, 21, 20, 0, 0)

AP  = network.WLAN(network.AP_IF)
mac = ubinascii.hexlify(AP.config("mac"), ":").decode()

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
    "too_long"      : (64, 1500, 100, 2),

    "added"         : ((71, 500, 50, 1), (64, 300, 50, 1), (60, 100, 50, 1)),
    "loaded"        : ((60, 500, 50, 1), (64, 300, 50, 1), (71, 100, 50, 1)),
    "saved"         : ((64, 300, 50, 1), (64, 100, 50, 1), (64, 300, 50, 1))
}

constant = {
    "name"          : "Constant provider",
    "active"        : True,     # Should be always active
    "api_link"      : "https://zza.hu/uBot_API"
}

data = {
    "name"          : "File manager",
    "active"        : True,     # Should be always active
    "json_category" : ("etc", ),
    "modify_rights" : ("/etc/ap/", "/etc/buzzer/", "/etc/feedback/", "/etc/i2c/", "/etc/logger/", "/etc/motor/",
                       "/etc/turtle/", "/etc/uart/", "/etc/web_repl/", "/etc/web_server"),
    "write_rights"  : ("/home/", "/program/"),
    "delete_rights" : ("/future/", "/home/", "/log/exception/", "/log/event/", "/log/object/", "/log/run/", "/program/")
}

feedback = {
    "name"          : "Motion feedback",
    "active"        : False
}

future = {
    "name"          : "Async manager",
    "active"        : True,     # Should be always active
    "period"        : 1000,
    "tickets"       : True
}

i2c = {
    "name"          : "I2C driver",
    "active"        : False,
    "sda"           : 0,
    "scl"           : 2,
    "freq"          : 400000
}

logger = {
    "name"          : "Log manager",
    "active"        : True,
    "folders"       : ("exception", "event", "object", "run"),   # Used only at running inisetup.py
    "active_logs"   : ("exception", "event", "object", "run")    # All: ("exception", "event", "object", "run")
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
    "name"          : "System core",
    "active"        : True,     # Should be always active
    "id"            : ubinascii.hexlify(uos.urandom(32)).decode(),
    "chk"           : ubinascii.hexlify(uos.urandom(32)).decode(),
    "firmware"      : firmware,
    "init_datetime" : initDatetime,
    "power_ons"     : 0,
    "root"          : True
}

turtle = {
    "name"          : "Turtle interface",
    "active"        : True,
    "named_folder"  : "named",
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
    "name"          : "UART interface",
    "active"        : True
}

web_repl = {
    "name"          : "WebREPL",
    "active"        : False,
    "password"      : "uBot_REPL"
}

web_server = {
    "name"          : "Web server",
    "active"        : True,
    "period"        : 300,
    "timeout"       : 150,
    "port"          : 80,
    "backlog"       : 15,
    "html_enabled"  : True,
    "json_enabled"  : True,
    "open_quick"    : True,
    "open_command"  : True,
    "log_event"     : True,
    "log_request"   : True,
    "log_response"  : True,
    "log__reply"    : True
}


################################
## CONFIG DICTIONARY

configModules = {
    "ap"            : ap,
    "buzzer"        : buzzer,
    "constant"      : constant,
    "data"          : data,
    "feedback"      : feedback,
    "future"        : future,
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

def check_bootsec():
    buf = bytearray(flashbdev.bdev.SEC_SIZE)
    flashbdev.bdev.readblocks(0, buf)
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
            % (flashbdev.bdev.START_SEC, flashbdev.bdev.blocks)
        )
        time.sleep(3)


def setWifi() -> None:
    AP.ifconfig((ap.get("ip"), ap.get("netmask"), ap.get("gateway"), ap.get("dns")))
    AP.config(essid = ap.get("ssid"), authmode = network.AUTH_WPA_WPA2_PSK, password = ap.get("password"))


def createFolders() -> None:
    uos.mkdir("/etc")
    uos.mkdir("/future")
    uos.mkdir("/home")

    uos.mkdir("/log")
    for folder in logger.get("folders"):
        uos.mkdir("/log/{}".format(folder))

    uos.mkdir("/program")
    uos.mkdir("/program/{}".format(turtle.get("turtle_folder")))
    uos.mkdir("/program/{}".format(turtle.get("named_folder")))

    uos.mkdir("/srv")


def createBaseFiles():
    firmware = system.get("firmware")

    firmwareComment = "# μBot firmware {}.{}.{}\r\n\r\n".format(
        firmware[0], firmware[1], firmware[2]
    )

    gc = ("import gc\r\n"
          "gc.enable()\r\n\r\n")

    footerComment = ("#\r\n"
                     "# For more information:\r\n"
                     "#\r\n"
                     "# https://ubot.hu\r\n"
                     "# https://zza.hu/uBot\r\n"
                     "#\r\n")

    with open("/.webrepl_cfg.py", "w") as file:
        file.write(firmwareComment)
        file.write("PASS = '{}'\r\n\r\n".format(web_repl.get("password")))
        file.write(footerComment)

    if web_repl.get("active"):
        uos.rename("/.webrepl_cfg.py", "/webrepl_cfg.py")

    with open("/boot.py", "w") as file:
        file.write(firmwareComment)
        file.write(gc)
        file.write("import micropython\r\n"
                   "micropython.alloc_emergency_exception_buf(100)\r\n"
                   "del micropython\r\n\r\n"
                   "import ubot_core as core\r\n\r\n")
        file.write(footerComment)

    with open("/main.py", "w") as file:
        file.write(firmwareComment)
        file.write(gc)
        file.write(("import usys\r\n"
                    "core = usys.modules.get('ubot_core')\r\n"
                    "del usys\r\n\r\n"))
        file.write(footerComment)


def createLogs():
    with open("/log/datetime.txt", "w") as file:
        file.write("{}\r\n0000000000.txt\r\n\r\n".format(system.get("init_datetime")))

    for folder in logger.get("folders"):
        with open("/log/{}/0000000000.txt".format(folder), "w") as file:
            file.write("{}     \tFallback {} log initialised successfully.\r\n\r\n\r\n"
                       .format(system.get("init_datetime"), folder))


def createConfigFoldersAndFiles():
    with open("/etc/datetime.py", "w") as file:
        file.write("DT = {}".format(system.get("init_datetime")))

    for moduleName, module in configModules.items():
        uos.mkdir("/etc/{}".format(moduleName))

        for attrName, attrValue in module.items():
            with open("/etc/{}/{}.txt".format(moduleName, attrName), "w") as file:
                file.write("{}\r\n".format(ujson.dumps(attrValue)))
            with open("/etc/{}/{}.def".format(moduleName, attrName), "w") as file:
                file.write("{}\r\n".format(ujson.dumps(attrValue)))


def createServerFiles():
    for fileName, fileData in files.items():
        path = "/srv/{}".format(fileName)
        with open(path, "wb") as file:
            file.write(ubinascii.a2b_base64(fileData[0]()))

        with open("/srv/{}_meta".format(fileName), "w") as file:
            file.write("{}\r\n".format(uos.stat(path)[6]))

            for line in fileData[1]:
                file.write("{}\r\n".format(line))


def setup():
    check_bootsec()
    setWifi()

    uos.VfsLfs2.mkfs(flashbdev.bdev)
    vfs = uos.VfsLfs2(flashbdev.bdev)
    uos.mount(vfs, "/")

    createFolders()
    createBaseFiles()
    createLogs()
    createConfigFoldersAndFiles()
    createServerFiles()
    deleteDictionaries()

    return vfs


###########
## FILES


def getTurtleArrowPng() -> str:
    return "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"


def getTurtleCrossPng() -> str:
    return "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"


def getTurtleF1Png() -> str:
    return "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"


def getTurtleF2Png() -> str:
    return "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"


def getTurtleF3Png() -> str:
    return "iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAABhGlDQ1BJQ0MgcHJvZmlsZQAAKJF9kT1Iw0AcxV9TpSIVESuKOGSoThZERXTTKhShQqgVWnUwuX5Ck4YkxcVRcC04+LFYdXBx1tXBVRAEP0Dc3JwUXaTE/yWFFjEeHPfj3b3H3TtAqJWYaraNAapmGYlYVEylV8XAKwLoQw9m0C8zU5+TpDg8x9c9fHy9i/As73N/jq5M1mSATySeZbphEW8QT21aOud94hAryBnic+JRgy5I/Mh1xeU3znmHBZ4ZMpKJeeIQsZhvYaWFWcFQiSeJwxlVo3wh5XKG8xZntVRhjXvyFwaz2soy12kOIYZFLEGCCAUVFFGChQitGikmErQf9fAPOn6JXAq5imDkWEAZKmTHD/4Hv7s1cxPjblIwCrS/2PbHMBDYBepV2/4+tu36CeB/Bq60pr9cA6Y/Sa82tfAR0L0NXFw3NWUPuNwBBp502ZAdyU9TyOWA9zP6pjTQewt0rrm9NfZx+gAkqav4DXBwCIzkKXvd490drb39e6bR3w+lG3K75++UuAAAAAlwSFlzAAAN1wAADdcBQiibeAAAAAd0SU1FB+UHFRIML0d8XmcAAAjGSURBVHja7Z15jBRFFMZ/O6wLC7iwgqCAyCUCEoGACqioiIi3gjEebMSgRg2SqIl4Jh6JJAokGgE1EDZRQI1GBQ9UggkiR0LACKKICuhyKLpcy8IiO+sf9QZ6m+menp6q3u6Z/pIX2OmZ6ur6ul69eu9VVRHRRSugxPZZEtgf4WeiKOT1aw0MAgYAvYAeIl2ANg6/aQD2WeRfYDOwAfgRWA8cignxhjLgcmC0/NsHaKb5HseAtcByYBnwDXCUGI1IqAA+k4ZpCFj2AQuAcUDzQiZiMDBH1EdDSGQPME16ZsFgDLAiRCSkkySwCBiWz0SMBFaHnIh0sgy4IJ+I6AV8FEEi7D3mbeCsKBORAO4HaiJOhlVqgSkGLD/j6A2sySMi7LICOCcqZIwD9uYxGSk5ANwRZiKKgVkFQIRdZqVx4TQ5TgU+LUAyrCqsfVjIOFP8RA0FLpuA7k1NRlfgl5iM4/KHmPlNgs7A1piEk6RKrMxA0U5c2TEBzqR0DYqMFsCquNEzygagbRDxk3fixs7KD1ZskpApcSNnLdNNkTEc+C9uYF+Oydt0k9E2tqhyjkp68hR71W/TgW4ev/sNcG+OL0CN9MZs0FJCsJ8D54bMk9EGmAdcJQTlhFHS7by+DT8Dl4j7PWg0Exd5WHvKg7k+YHPgV5833w28LuQEhZ4hV13VQIdcHvBxTRW5z+UeGx1+UycP4Cb9bGXdEIHxZK5fMjqgsgB1VOJpH4R4kcmGXiDTVtdAtzCrW+8o06RKTjGkokbZ/j4vAgG8IuDFbAnpqGMA8mHNZYvLbGUPiEhU9XpgaDaEPCJmJCHvIWWWBysB+hIdPOGVkFIN84igCAGVB5xSVyURIuSGdLGTdISMF/d6VAgZI/+eT7SQAB72Qsh9hm5uCoOBScAEoofxZEjw7m3I1JtpyOzNBxnr9uZWGDT1YqRHhRshtxi6aUPc7o642mrRWm34bgYnVmHuIQdRMfDdQL2lXXoSTHJ1KXAlsNhOyLUF8kbuBD4GvhXZ4fLdNqjA3FjgdtSaRxO4LkWIFe8aHLhmaxzU64GHgOey/N0Seen8Zq6XAy8ARwy0z0/pblgVEUJWye+u8Pj9j3Fx5vnAecDv6Hc4trcO6l1RiW9RwCKP49JO1Erem4Hv01xvhVpLOFjMfa+T4R+Bi1FZijrH2GFWQqI0y/3EIyF/yhiRQluZ9C4QsmpEVaxFrWP/B9gCvMnJcRY7dgF3arYeG/XiJw1PfnSprPWW343y8P17UB7gt8huJVe9TGYzeakXa2yjhVYry3RSgNvbvBoVh09aPqtFRQxT2C9j3AdZmtKz8bf2PCGGQxeZmyUdvvc+ypWua2w6jmWGe8gbBkgeHZBrw81H1l/jfQ5Yx5Aori4NarI53uVatcb7nAq0TqmsjoYfKulybY4MuG4q67AM0vNlRh0kIReJaj/mMDfRiU7F0ktaG34oN2tkaBYum3Eycw6SkNbiazqQ5prulbjlKTKKmrCHZINhnFh3ERQhSbHQnByDOtEygVrvQUQIARX6DJKQVQ71bwfcpdvRmCAY13iUCal0+PwlGYh1ojiKhFyOiqMPCqDeK1BJ0nZMQG0boht1xWLBRImQ5sAXAdR5i6iketvnD6Jylk2gLoHaQOxohAgJAsvFmvvD5gubj9q5wVTSxqFUwXtjQgDlNJwgavEf+awElUO8BeVQNIm/ii0VMTk5DHNM/QiwVAbvxRZt0RF4QOSMAOrRYCVkK3qDOGHuIVWiktaKSbsujcoulfGjFyrEW4be1FonN0xdipBtTaiygk6AmIKKibjhMDDD8ncz1HK0u8RbUGqgXpuxDE6bCmgMOd3WE8pFPbkN1PWomHwFKni1yEC9NlkJWWe4EcK0UfEUVPzlMMqJWY1yWB4RTbEQ5eF1UlHbgJtQ8ZKkbkKstn0d5mIKj2WoSBhTPHcAEzM04gSN9xtuL/w7gw83yeWhfiDcubezcU8dqtRwj8PSKRrpzWUG1URdBusizHgAeMbl+qMa5nFrU20UE+INT+Gcd1ANfJhj+V+m/pOwOdJMzdhrXa6tjAAhJcDdLtffz7H8RSb1YUr+Al4Dhnio0AjgFcK9XeAGl/qfnUO5W90aRsfC+99lEuU3h7YP4dwj/qBLnVvkUO5Ua0H2RLAlYpPn4rs5IHo1F1fMRlRyQZiQiq3XOhDiF5WZvjCVeDuldPKfy2x+iM8yTxo/091gDtGLXwSBn1zapb/PMmd6IeQ31PESMRrjc5drY32Utx14z+uXB8cqqpEcRZ0Olw49UUl0uW6ckxFfxEQcl5dd2uk9H+VV4SO+MlDczoVOxnKcM+hv9VnmRL96c16Bk7EU5/zdQTI3ybbMjTnM0egi84pCJGMGzgt2LkSdIOpnLeHIXK2LhwuMiJXApS7tUYH/jTbnogEJqWQ+k1APfI1aIOoU4+8upq/fe+xC4/KFPuTXaWsNqJDtClRIt4vLs7cDniW3E0mTGNiY4e6INnySE6k/lULAJR78T/1Ri0V1HA07zdRstTIiJPyJ2ligdxaOvwTqRM/nJYKX1FSXNWSx0122OVEtUFuJDw25m2M/mc/u6IRaMj1ATNgR6M9QrJK22mGKEFA5TKvxvhd8U+FJ1AYBZag9iDtL3TuhFrmaPlWtRqy174N42L4SEYzdKs67cl8T9Bt4PipDPCagsRzDwHkh2XiF98QkNPIK39bUuron/k9QyCepIUSbwHVG5QcXKhl/i38rVGhRoN7hdWG3OCejclULgYy5BLPOP2f0y3MVthf9mwYYR3NxytXmGRkfEMyaQ6NW2OI8IGIz+vc2aVKMwOwaFFOyE7W+pYQ8xWjgqwgQsR11sE0pBYIBqNVJ+0IWO1kus+1iChSpNeEfaQoG+ZGNYoB0J0YjtARuBF5FrT1MGiJgD2r/30lhIyHs53qUo4JHA1Eh1R4infG2AUy1DMq/oVb7bkDt/ftzWB84ygetnCaE2SODB0X1VRPM1lNa8T+sPGxProdd8AAAAABJRU5ErkJggg=="


def getTurtlePausePng() -> str:
    return "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"


def getTurtlePlayPng() -> str:
    return "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"


def getTurtleRepeatPng() -> str:
    return "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"


def getTurtleUndoPng() -> str:
    return "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"


def getFaviconIco() -> str:
    return "AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADj4+P/nJyc/01NTf88PDz/PDw8/zw8PP88PDz/PDw8/zw8PP88PDz/PDw8/zw8PP88PDz/PDw8/zw8PP88PDz/PDw8/zw8PP88PDz/PDw8/zw8PP88PDz/PDw8/zw8PP88PDz/PDw8/zw8PP88PDz/PDw8/09PT/+dnZ3/4+Pj/7CwsP9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0RERP+xsbH/WVlZ/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/1paWv9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/RERE/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9GRkb/TExM/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/3t7e//39/f/wcHB/3Fxcf9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/d3d3//7+/v/+/v7/rq6u/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9ycnL//v7+//7+/v+cnJz/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/2xsbP/+/v7//v7+/4uLi/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/ZGRk//7+/v/+/v7/fX19/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9YWFj//v7+//7+/v9xcXH/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0lJSf/+/v7//v7+/2pqav9GRkb/gYGB/5qamv9ycnL/RERE/0NDQ/9DQ0P/Q0ND/11dXf+JiYn/eHh4/0dHR/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND//Ly8v/+/v7/ZWVl/7u7u//+/v7//v7+//7+/v++vr7/RUVF/0NDQ/9XV1f/9fX1//7+/v/+/v7/2NjY/1JSUv9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/29vb//7+/v+enp7//v7+//7+/v/+/v7//v7+//7+/v+YmJj/Q0ND/5mZmf/+/v7//v7+//39/f/+/v7/w8PD/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ//BwcH//v7+//f39//4+Pj/mpqa/29vb/+cnJz/+Pj4//Dw8P9LS0v/wMDA//7+/v/CwsL/UlJS/19fX//a2tr/ZmZm/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/6SkpP/+/v7//v7+/4uLi/9DQ0P/Q0ND/0NDQ/98fHz//f39/4KCgv/a2tr//f39/1xcXP9DQ0P/Q0ND/1FRUf9ISEj/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/hYWF//7+/v/j4+P/RUVF/0NDQ/9DQ0P/Q0ND/0NDQ/+1tbX/t7e3/+/v7//r6+v/RERE/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/98fHz//v7+/7Ozs/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/1lZWf/v7+///f39/9bW1v9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/3x8fP/+/v7/p6en/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/8DAwP/+/v7/ycnJ/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/fX19//7+/v+5ubn/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/gICA//7+/v/V1dX/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9+fn7//v7+/9TU1P9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9SUlL//Pz8//Ly8v9GRkb/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/35+fv/+/v7/7+/v/0RERP9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0VFRf/29vb//v7+/1tbW/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/fn5+//7+/v/9/f3/UFBQ/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/RERE//T09P/+/v7/e3t7/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/+AgID//v7+//7+/v9qamr/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/8fHx//7+/v+cnJz/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/4CAgP/+/v7//v7+/4WFhf9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ//u7u7//v7+/7y8vP9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/gICA//7+/v/+/v7/oKCg/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/+zs7P/+/v7/3d3d/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/+AgID//v7+//7+/v+7u7v/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/6Ojo//7+/v/4+Pj/SEhI/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/1BQUP9vb2//dXV1/2hoaP9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9nZ2f/c3Nz/3h4eP9FRUX/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/T09P/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/1JSUv+Wlpb/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/mJiY//n5+f+Ojo7/R0dH/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/Q0ND/0NDQ/9DQ0P/R0dH/4+Pj//5+fn/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="


def getFavicon512Png() -> str:
    return "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"


def getFavicon192Png() -> str:
    return "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"


def getFaviconPng() -> str:
    return getFavicon192Png()


def getFavicon180Png() -> str:
    return "iVBORw0KGgoAAAANSUhEUgAAALQAAAC0CAMAAAAKE/YAAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAA/UExURUNDQ0FBQUNDQ/f390RERERERP///0pKSkRERERERG9vb2JiYlNTU35+ft3d3ezs7Ly8vJ6enszMzI+Pj62trQgR3kEAAAAKdFJOUwP////d///9sVmNEbtQAAAGSUlEQVR42u2d6darIAxFCxapE4Py/s967fgBWg2Gitwlv8vqLiYnA1guF2tU1e3K2eEGv96q6jI/qtsBgd9j5J5DvrKDjyn2kVf5YyY3j5llMRzqK2PZUd8Yy446I+YPdcVzguZVXgZtLXXFMhtVbhb9Wuq8LPoR0av8FvpuHxlC33LTjod9XNgJvc84oU/oE/qEPqEhgz7HDpPQ0JSM4/6lfBztOEBZ4msSf0/aF5o2Whtj1Dj6vhdCSA2Y1A6vSf1zUt/QPaFJV5Tu6NtVANJIb5ImiaHX7eN40IqFQxddYmjAok2gZZMYeoBAe5NEu68j1t73FzUJn9RzlhQa8qQnkwxLCw150pNJA0kLDXnS/iSkeOCh1YZJSPHAQ0PChD8JKR54aIh5+jqpWFpHhCjeBNrQtNAg8/ShkeKBhgaZpwcNejq/hAbFNg8aKx5oaJBPedBY8UBDgxJj0kUVDzQ0KLaRIWIFgIeG+ZQH3SWGhvmUC40WDyw0zKdcaIn1Qyw0LJt3oXueGBqWzbvQaPHAQsOEwIVGiwcWGiYEREcVDyQ0UAgcaHQQx0IDARxodBDHQgMBHOieJ3ZEIIADbWhiaGD/guqIFQAaGqhe1MRrH6ChoQA2dATxQEJDUx8TVTxw0OBVs6BVhJM8wdB21xa6aryPKh44aKDi0VZEFQ8ctAk3KXwFgIUGKp6d5MUQDxQ0WHJVXPHAQcMetWPS+AoACQ3N8eoiZgWAhN6S43WpoYGP2lbpKOKBggZWtfbOZxQ/3AAtA+OEU9X2nCWGBtknta0jPTRMpkktozZq9oHWZXkgmwYpgRNZjgDdhe8RRUk9fg7NVXkoaNhJD1nG7U1joSF5hIl6DigCtAle6DiFCwp6PVI8uzSFEceBXvUq0oinzqnUqakMMFD9ygZNrINAEfoeBvYDtRUVoyQfqCNua/HNvGVuSFwjarCAvVMl0Vq/NEk1zhR0d422/bvAsWwqRd/DzY4Xl/rTlB5IeOUQF7oR7oGCr0v9yaNHg7BTPbW/I06OMH1bOPI2jrsJ2c8nQavXO7kxMsw7FuXGCSdqOWWi5KfQuvSPT88ZCOW6sCHtrYCZXi9tm6B3Gy4Y8XhCTKkt5ufpe7sin9oHbZUcQorHC0Y8nkup/e+zmZ/W4YQk3w0eplSoAOpAaLfi+1AT1weN3+9zSnLPDSh7/MSQbY0w6Gl+/KBWDSP041J1X/pbLLS156mW2MxDEarfgdCTw/Wv9TQ1f7yAw9pOyWn08Z6Qaf9+48uUgpQwEPrPoQrhltm9GYZBK1HMvwTjOnDfcfJ4yYjX6jlB/049yJ90ybovV8cn9vhSWfS667pB98Wi3MeRPGV52BdTmV3oSVC6g9u9dvqz4GIrnmy4Wl3oTz4178FbY/tlq+KNWlbLFeg/7Z0TeEAGEwPaqWrH8GyWmaWVZlANsaKfQLu7mKQRy164kB5++3E/gO7cBhcdCpBx2HXMyo/7AbT2oJd80VMx75DscsYV1RH9EzILBiK8Z06/fdSEVwWXjTL9krOvCiImdjrvisUG5jBoR7deWUUn55np1+p8Oa+NDe2mPa/AQWsxl/aROe2ZfFJ0bEvFGAYtZzaMSaO8YveeDs2X8s4nC6Hbbf2Ey8bYYiXAhA/9XzNGjFnqNxTCOyVkcU87pFBdu/Wl98vG2GJn7WNSXA+PV8KV7tpPPcBmq+62GdO7rm4WPxcTuiu+9PTpmP7fX75nZJXk8YY/IQTT/QiDXjy7TWNsEcaHjnzgfB9oHfP9vJ2gqckQ2q1OVZbQLAtot2TqeQ7QXsclznmTnaHjHN04ode7j3GObpzQs9BxX6TeB9p7U7XLELrMAzrynwMkgdZ5QJflMdK8EOgh/D9UDgedLmNCQKeL4/89tI76B2FpoNPF8ZDUVP/i3Oivof19oSyhhwygJztwmmYInSwkhkD7W1l9ltCpmgjboQsx8LxW+r5LkUUL4QM9EneY3YddoZ+tPKnSEgdCayGlGprExIHQrG0aTghLPsI29I9AzM7/VD+hT+gT+oQ+PDTPj5nnebFSlldYVflBVxlcUDqxjirPC/DyvGowt6W+5Xt9ZpYXleZ5JWyel+/mec1xnhdK328bP/wyz944fjuwac9fkn7g6+iv/nX0/wDH+5XJDhrPzAAAAFd6VFh0UmF3IHByb2ZpbGUgdHlwZSBpcHRjAAB4nOPyDAhxVigoyk/LzEnlUgADIwsuYwsTIxNLkxQDEyBEgDTDZAMjs1Qgy9jUyMTMxBzEB8uASKBKLgDqFxF08kI1lQAAAABJRU5ErkJggg=="


def getSafariTabSvg() -> str:
    return "PD94bWwgdmVyc2lvbj0iMS4wIiBzdGFuZGFsb25lPSJubyI/Pgo8IURPQ1RZUEUgc3ZnIFBVQkxJQyAiLS8vVzNDLy9EVEQgU1ZHIDIwMDEwOTA0Ly9FTiIKICJodHRwOi8vd3d3LnczLm9yZy9UUi8yMDAxL1JFQy1TVkctMjAwMTA5MDQvRFREL3N2ZzEwLmR0ZCI+CjxzdmcgdmVyc2lvbj0iMS4wIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiB3aWR0aD0iNTEyLjAwMDAwMHB0IiBoZWlnaHQ9IjUxMi4wMDAwMDBwdCIgdmlld0JveD0iMCAwIDUxMi4wMDAwMDAgNTEyLjAwMDAwMCIKIHByZXNlcnZlQXNwZWN0UmF0aW89InhNaWRZTWlkIG1lZXQiPgo8bWV0YWRhdGE+CkNyZWF0ZWQgYnkgcG90cmFjZSAxLjE0LCB3cml0dGVuIGJ5IFBldGVyIFNlbGluZ2VyIDIwMDEtMjAxNwo8L21ldGFkYXRhPgo8ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgwLjAwMDAwMCw1MTIuMDAwMDAwKSBzY2FsZSgwLjEwMDAwMCwtMC4xMDAwMDApIgpmaWxsPSIjMDAwMDAwIiBzdHJva2U9Im5vbmUiPgo8cGF0aCBkPSJNMzkzIDUxMDYgYy0xODYgLTQ1IC0zNDUgLTIwNyAtMzgyIC0zODggLTggLTM4IC0xMSAtNjc3IC05IC0yMTgzCmwzIC0yMTMwIDIyIC02MCBjNjcgLTE3NSAyMjAgLTMwNiAzOTMgLTMzNSA0NiAtOCA2ODQgLTEwIDIxODAgLTggbDIxMTUgMyA2OAoyNyBjODYgMzUgMTQxIDczIDIwNSAxNDMgNjAgNjYgMTA2IDE1NiAxMjIgMjQwIDggNDQgMTAgNjMzIDggMjE4MCBsLTMgMjEyMAotMjMgNTkgYy02NCAxNjkgLTIxMyAzMDAgLTM4MCAzMzUgLTgyIDE3IC00MjQ4IDE0IC00MzE5IC0zeiBtMTQ3MyAtNzgzIGM1Ci0xNiAtMzAgLTI4MyAtODYgLTY3MyAtMTAxIC02OTQgLTEwOCAtNzc0IC03NiAtOTE1IDQ2IC0yMDAgMTU5IC0zNjkgMjk4Ci00NDIgNDggLTI1IDYzIC0yOCAxNTMgLTI4IDkzIDAgMTA1IDIgMTY2IDMyIDc2IDM4IDE4NyAxNDcgMjU3IDI1MyAxMDEgMTUzCjIxNSA0MTkgMjc0IDYzOCBsMzEgMTE3IDkgNTE1IGM1IDI4MyAxMCA1MTUgMTEgNTE2IDEgMSAxMDIgNSAyMjQgOCBsMjIzIDgKMTEgLTI2IGMxMCAtMjEgLTcgLTEzNCAtMTAxIC02NzEgLTEyMyAtNzA4IC0xMTYgLTY0MSAtODkgLTkyMCAzNiAtMzY4IDEyNQotNTA1IDMyOSAtNTA1IDEwNSAwIDE1NyAyNiAyNDUgMTIzIGw2OSA3NSA0MyAtMjkgNDIgLTI5IC0yOSAtNjkgYy04OSAtMjE3Ci0yMjcgLTM3MyAtMzc2IC00MjcgLTExNSAtNDIgLTI4MiAtNDIgLTM2NCAxIC05OSA1MSAtMTY4IDIxMyAtMjA1IDQ4MSAtMTYKMTE4IC00NCAzNTcgLTQ1IDM4MiAwIDI4IC0zMCAxMCAtMzkgLTI1IC01IC0yMSAtMTkgLTc1IC0zMCAtMTE5IC0zMCAtMTE5Ci04NyAtMjc2IC0xMzMgLTM2OCAtMTM4IC0yNzcgLTMyMyAtNDA1IC01NjcgLTM5NCAtMTI2IDYgLTE3MiAyOCAtMjcxIDEyNwotNTYgNTcgLTkwIDEwMyAtMTM0IDE4NCAtMzIgNTkgLTY1IDEwNyAtNzMgMTA3IC0xMiAwIC0xMyAtMzAgLTggLTE5NyAxMAotMzIzIDIzIC01NTEgNTEgLTg1NiAxNCAtMTU5IDIyIC0yOTIgMTggLTI5NyAtMjAgLTE3IC0zNzEgLTEzMyAtMzk5IC0xMzIKLTcyIDUgLTY4IC0xMyAtNjEgMjUxIDE4IDY0NyA0OSAxMDAxIDEyNiAxNDYzIGwzMCAxNzYgMCA4NDEgMCA4NDAgMTM4IDQgYzc1CjEgMTgxIDQgMjM0IDUgbDk4IDIgNiAtMjd6Ii8+CjwvZz4KPC9zdmc+Cg=="


def getMsTilePng() -> str:
    return "iVBORw0KGgoAAAANSUhEUgAAAQ4AAAEOBAMAAACKn+SWAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAAqUExURUxpcUdHR0RERERERERERP///zg4OD4+PtHR0ejo6LCwsFhYWI2NjXBwcHl5pUQAAAAEdFJOUwD+x1YKeo0IAAAEcklEQVR42u2cTWsTQRyHffkCrgy7hF4U+wFE/AKrA2k/wMKmpgehJKUmh0BI4ttBMLaCHgQDzd0GrVdtjJ4raM616qdxZ3ZNdrLZQLM7L+jvOZm95OnMf37zsk7OnQMAAAAAAAAAAAAAAAAAAADAAG5cpWfn8rXcNehy5CxygS7LlTw1LpKlPdzrOXqcX1qDkks5eqxmaI9bOXYLzcJ1A6o030q9mcnjdn7lkcnj1j/nQTJ5uLl50GzAAx76PNptcT6jtNhW7dFuu9bKl2bsSbHdDJ44ij3e7vX7/dIwlhG1vef9fm9XsUfPY8Q9dviTVzo8SiThoaU9/Fh9uNvcY0A0eGzcTXh8NcTjhw6PctyjM1u5Sjy67Es3Yx60M1u56trjTnPWw2/oaA8hLDqzFaOuPXYTHuW7OtpDCItOomIUeBS7ibDoJCpGj8cae/Ka6vA4jXussyfPiA4PIbTW06cXyR5iaK2nTy+SPXyhKAuJnlLlIYYW8ygNddRpOeHhN83wSIl1yR6bjVmPshYPITydQnqsS/YQptviKD3WJXvsxgepM0rdNcj2EMKz+DF11yDbQwhP+zg91pV6HKTHumQPIcT5kx9aPIQQf5i+a5DsURKOBGvpuwbJHsIegW+zU3YNkj2EyYTHWNr0otCDD1s9HsKkZnfN8ODDxdfeL+FpkAF1WvAWLMfkeThdsRd4mWrID2c2x3reQfoyWa5HLMWDNPULunI9PrsWvI37OuY5tyesx4LyKG/rmPd5XEzW627w8c62hnWQWxcOodiZ5dOd9O2+PI+acFjKRu1gZ7pOdokqj/Aw/WmsdU5r0/2Ls6WqPsJD26hj7BGLsPrkgVv7qsqDx3jQGW7wb6veYwbhwpD1iH2y0VTjwTcr7O9vuRapfONjhw/lgcW8EgsAWR72SejhvbQrWz/Do9TwSKRKaetXYp8rzSMYICV+RLZ/+C4aOnwD4710Gp+T+zppHmxSG3lTghk/nHK9/edz8l2aB5tuH8U8go6Y9NWc9ZC0OmUepDf1YIFemFqp8mBjo3R0PPlitvCIsm3uKaosD54VHzrxbonmnPnLQ0ke7mOeWQ8nHRPO993o05OGKg/+pw8nlRnGVjRgPN8hqjz4dDt061GDRNPJg/DTm4aqeT8sySGxP/Evfh+lZzFMsi2i1uOUuO3fPW9/XP37xfe+7x2OW4Sq9qCksvLFnmhQp1KpVC1167HwnTELb6vYji++LMtS+j57zVuwSVDoUVjwzkehh2OIR7gcM8VjoL9fTszwsI3yeKbf49hb8JJDtcdrQzxeGeKR9jLuP/Q4WPB/X5R7lOEheGzAQ/DwTfEwZNz61AgPf6zfI9hRvziqGtAe/rjVINo96Mqw6ppwr6DYJNQED3o2Ddw7gYcaD5JJI797a6uZPP69+4Q3M3nkd8/TlHuvptwDzlQgOd6LNuae+PL35t1c782b8jsCxvyugjG/MwEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADU8Aejz7Io8gWfIAAAAFd6VFh0UmF3IHByb2ZpbGUgdHlwZSBpcHRjAAB4nOPyDAhxVigoyk/LzEnlUgADIwsuYwsTIxNLkxQDEyBEgDTDZAMjs1Qgy9jUyMTMxBzEB8uASKBKLgDqFxF08kI1lQAAAABJRU5ErkJggg=="


def getFavicon32Png() -> str:
    return "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAA8UExURURERP///0hISDc3N0FBQUREREVFRURERExpcUJCQj09PYGBgWlpaefn51ZWVtPT06CgoL6+vvT09LGxsYF87CQAAAAKdFJOU4L///8B///xAAFwXrpgAAABFUlEQVQ4y4WT4bqDIAiGBY+0oWLp/d/rxLLOnD35R4xX+kAwb7O427WYlzGO7gFy5rpPRIOhwGLOAzMPRkNMtzAE2S0JAS/iANB6gM2qgyJkuYT9B9YGYITk5hF8BUiBzdIUCEw7sIf6AbJ0wM+BqD9ogIaaAEk/EwtkdFOgZUmdnABNGtrylUQH9GLRLFlii0BTDUg1QIrRzTSsWihnA/gEwkw4AhtA9uJzxg2KkxQOIV0DJyiga9VY8crEHI2h5alBIBGHukUZAJZc67cWr3ZYPZ6lOIH6VrYurTa3bQBCe21s2glxTLMDk8Y+gJr/Vxf8ArVfygOQPNMt4FgCT/3uGBxyTFM/9dG7cdfRexzev4fx/wCCRhbrZo3bZwAAAFd6VFh0UmF3IHByb2ZpbGUgdHlwZSBpcHRjAAB4nOPyDAhxVigoyk/LzEnlUgADIwsuYwsTIxNLkxQDEyBEgDTDZAMjs1Qgy9jUyMTMxBzEB8uASKBKLgDqFxF08kI1lQAAAABJRU5ErkJggg=="


def getFavicon16Png() -> str:
    return "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAA5UExURURERFRUVHJycsnJyTc3N0dHRz8/P0RERERERERERF5eXv39/evr66Ojo9jY2I+Pj7m5uYODg7S0tMK1v7kAAAAJdFJOU/r///////+QkXy16ecAAACASURBVBjTTc/rEoUgCARgpYVa7/X+D3vUrNMfZvYbRHAHSdWncHeuV2AUGzCz1WzUfGL0dFBsBdRYP9A6JPlABn3y95AJJ0wS+YcKXIlYQCvJ51ZExqMBWrYY/RXb6jCfggR4oS0IMcDUsIZqB7G+gj6/WMj3CnyPwTfP89/M/Qcl5wfiXGg3cwAAAFd6VFh0UmF3IHByb2ZpbGUgdHlwZSBpcHRjAAB4nOPyDAhxVigoyk/LzEnlUgADIwsuYwsTIxNLkxQDEyBEgDTDZAMjs1Qgy9jUyMTMxBzEB8uASKBKLgDqFxF08kI1lQAAAABJRU5ErkJggg=="


def getSiteWebmanifest() -> str:
    return "ewogICAgIm5hbWUiOiAiXHUwM2JjQm90IiwKICAgICJzaG9ydF9uYW1lIjogIlx1MDNiY0JvdCIsCiAgICAiaWNvbnMiOiBbCiAgICAgICAgewogICAgICAgICAgICAic3JjIjogIi9hbmRyb2lkLWNocm9tZS0xOTJ4MTkyLnBuZyIsCiAgICAgICAgICAgICJzaXplcyI6ICIxOTJ4MTkyIiwKICAgICAgICAgICAgInR5cGUiOiAiaW1hZ2UvcG5nIgogICAgICAgIH0sCiAgICAgICAgewogICAgICAgICAgICAic3JjIjogIi9hbmRyb2lkLWNocm9tZS01MTJ4NTEyLnBuZyIsCiAgICAgICAgICAgICJzaXplcyI6ICI1MTJ4NTEyIiwKICAgICAgICAgICAgInR5cGUiOiAiaW1hZ2UvcG5nIgogICAgICAgIH0KICAgIF0sCiAgICAidGhlbWVfY29sb3IiOiAiI2ZmZmZmZiIsCiAgICAiYmFja2dyb3VuZF9jb2xvciI6ICIjZmZmZmZmIiwKICAgICJkaXNwbGF5IjogInN0YW5kYWxvbmUiCn0K"


def getBrowserconfigXml() -> str:
    return "PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz4KPGJyb3dzZXJjb25maWc+CiAgICA8bXNhcHBsaWNhdGlvbj4KICAgICAgICA8dGlsZT4KICAgICAgICAgICAgPHNxdWFyZTE1MHgxNTBsb2dvIHNyYz0iL21zdGlsZS0xNTB4MTUwLnBuZyIvPgogICAgICAgICAgICA8VGlsZUNvbG9yPiNkYTUzMmM8L1RpbGVDb2xvcj4KICAgICAgICA8L3RpbGU+CiAgICA8L21zYXBwbGljYXRpb24+CjwvYnJvd3NlcmNvbmZpZz4K"


def getLicenseHtml() -> str:
    return "PCFET0NUWVBFIGh0bWw+CjxodG1sPgogICAgPGhlYWQ+CiAgICAgICAgPG1ldGEgbmFtZT0ndmlld3BvcnQnIGNvbnRlbnQ9J3dpZHRoPTYxMCc+CiAgICAgICAgPG1ldGEgY2hhcnNldD0ndXRmLTgnPgogICAgICAgIDxtZXRhIG5hbWU9J2F1dGhvcicgY29udGVudD0nU3phYsOzIEzDoXN6bMOzIEFuZHLDoXMgLy8gaHUtenphJz4KICAgICAgICA8bGluayByZWw9J2F1dGhvcicgaHJlZj0naHR0cHM6Ly96emEuaHUnPgogICAgICAgIDxsaW5rIHJlbD0nbGljZW5zZScgaHJlZj0nL2xpY2Vuc2UuaHRtbCc+CiAgICAgICAgPGxpbmsgcmVsPSdoZWxwJyBocmVmPSdodHRwczovL3Vib3QuaHUnPgogICAgICAgIDxsaW5rIHJlbD0naWNvbicgdHlwZT0naW1hZ2UvcG5nJyBocmVmPScvYW5kcm9pZC1jaHJvbWUtNTEyeDUxMi5wbmcnIHNpemVzPSc1MTJ4NTEyJz4KICAgICAgICA8bGluayByZWw9J2ljb24nIHR5cGU9J2ltYWdlL3BuZycgaHJlZj0nL2FuZHJvaWQtY2hyb21lLTE5MngxOTIucG5nJyBzaXplcz0nMTkyeDE5Mic+CiAgICAgICAgPGxpbmsgcmVsPSdpY29uJyB0eXBlPSdpbWFnZS9wbmcnIGhyZWY9Jy9mYXZpY29uLnBuZycgc2l6ZXM9JzE5MngxOTInPgogICAgICAgIDxsaW5rIHJlbD0naWNvbicgdHlwZT0naW1hZ2UvcG5nJyBocmVmPScvZmF2aWNvbi0zMngzMi5wbmcnIHNpemVzPSczMngzMic+CiAgICAgICAgPGxpbmsgcmVsPSdpY29uJyB0eXBlPSdpbWFnZS9wbmcnIGhyZWY9Jy9mYXZpY29uLTE2eDE2LnBuZycgc2l6ZXM9JzE2eDE2Jz4KICAgICAgICA8bGluayByZWw9J2ljb24nIHR5cGU9J2ltYWdlL3gtaWNvbicgaHJlZj0nL2Zhdmljb24uaWNvJz4KICAgICAgICA8bGluayByZWw9J3Nob3J0Y3V0IGljb24nIHR5cGU9J2ltYWdlL3gtaWNvbicgaHJlZj0nL2Zhdmljb24uaWNvJz4KICAgICAgICA8bGluayByZWw9J21hbmlmZXN0JyBocmVmPScvc2l0ZS53ZWJtYW5pZmVzdCc+CiAgICAgICAgPGxpbmsgcmVsPSdzdHlsZXNoZWV0JyBocmVmPScvc3R5bGUuY3NzJz4KICAgICAgICA8dGl0bGU+zrxCb3QgTUlUIExpY2Vuc2U8L3RpdGxlPgogICAgPC9oZWFkPgogICAgPGJvZHk+CiAgICAgICAgPGgxPgogICAgICAgICAgICBUaGUgbGljZW5zZSBvZiB0aGUgzrxCb3QgZmlybXdhcmUKICAgICAgICA8L2gxPgogICAgICAgIFRoaXMgZmlsZSBpcyBwYXJ0IG9mIHVCb3RfZmlybXdhcmUuPGJyPgogICAgICAgIDxhIGhyZWY9J2h0dHBzOi8venphLmh1L3VCb3RfZmlybXdhcmUnIHRhcmdldD0nX2JsYW5rJz5odHRwczovL3p6YS5odS91Qm90X2Zpcm13YXJlPC9hPjxicj4KICAgICAgICA8YSBocmVmPSdodHRwczovL2dpdC56emEuaHUvdUJvdF9maXJtd2FyZScgdGFyZ2V0PSdfYmxhbmsnPmh0dHBzOi8vZ2l0Lnp6YS5odS91Qm90X2Zpcm13YXJlPC9hPjxicj48YnI+PGJyPgogICAgICAgIDxoMj4KICAgICAgICAgICAgTUlUIExpY2Vuc2UKICAgICAgICA8L2gyPgogICAgICAgIENvcHlyaWdodCAoYykgMjAyMC0yMDIxIFN6YWLDsyBMw6FzemzDsyBBbmRyw6FzIC8vIGh1LXp6YTxicj48YnI+CiAgICAgICAgUGVybWlzc2lvbiBpcyBoZXJlYnkgZ3JhbnRlZCwgZnJlZSBvZiBjaGFyZ2UsIHRvIGFueSBwZXJzb24gb2J0YWluaW5nIGEgY29weTxicj4KICAgICAgICBvZiB0aGlzIHNvZnR3YXJlIGFuZCBhc3NvY2lhdGVkIGRvY3VtZW50YXRpb24gZmlsZXMgKHRoZSAiU29mdHdhcmUiKSwgdG8gZGVhbDxicj4KICAgICAgICBpbiB0aGUgU29mdHdhcmUgd2l0aG91dCByZXN0cmljdGlvbiwgaW5jbHVkaW5nIHdpdGhvdXQgbGltaXRhdGlvbiB0aGUgcmlnaHRzPGJyPgogICAgICAgIHRvIHVzZSwgY29weSwgbW9kaWZ5LCBtZXJnZSwgcHVibGlzaCwgZGlzdHJpYnV0ZSwgc3VibGljZW5zZSwgYW5kL29yIHNlbGw8YnI+CiAgICAgICAgY29waWVzIG9mIHRoZSBTb2Z0d2FyZSwgYW5kIHRvIHBlcm1pdCBwZXJzb25zIHRvIHdob20gdGhlIFNvZnR3YXJlIGlzPGJyPgogICAgICAgIGZ1cm5pc2hlZCB0byBkbyBzbywgc3ViamVjdCB0byB0aGUgZm9sbG93aW5nIGNvbmRpdGlvbnM6PGJyPjxicj4KICAgICAgICBUaGUgYWJvdmUgY29weXJpZ2h0IG5vdGljZSBhbmQgdGhpcyBwZXJtaXNzaW9uIG5vdGljZSBzaGFsbCBiZSBpbmNsdWRlZCBpbiBhbGw8YnI+CiAgICAgICAgY29waWVzIG9yIHN1YnN0YW50aWFsIHBvcnRpb25zIG9mIHRoZSBTb2Z0d2FyZS48YnI+PGJyPgogICAgICAgIFRIRSBTT0ZUV0FSRSBJUyBQUk9WSURFRCAiQVMgSVMiLCBXSVRIT1VUIFdBUlJBTlRZIE9GIEFOWSBLSU5ELCBFWFBSRVNTIE9SPGJyPgogICAgICAgIElNUExJRUQsIElOQ0xVRElORyBCVVQgTk9UIExJTUlURUQgVE8gVEhFIFdBUlJBTlRJRVMgT0YgTUVSQ0hBTlRBQklMSVRZLDxicj4KICAgICAgICBGSVRORVNTIEZPUiBBIFBBUlRJQ1VMQVIgUFVSUE9TRSBBTkQgTk9OSU5GUklOR0VNRU5ULiBJTiBOTyBFVkVOVCBTSEFMTCBUSEU8YnI+CiAgICAgICAgQVVUSE9SUyBPUiBDT1BZUklHSFQgSE9MREVSUyBCRSBMSUFCTEUgRk9SIEFOWSBDTEFJTSwgREFNQUdFUyBPUiBPVEhFUjxicj4KICAgICAgICBMSUFCSUxJVFksIFdIRVRIRVIgSU4gQU4gQUNUSU9OIE9GIENPTlRSQUNULCBUT1JUIE9SIE9USEVSV0lTRSwgQVJJU0lORyBGUk9NLDxicj4KICAgICAgICBPVVQgT0YgT1IgSU4gQ09OTkVDVElPTiBXSVRIIFRIRSBTT0ZUV0FSRSBPUiBUSEUgVVNFIE9SIE9USEVSIERFQUxJTkdTIElOIFRIRTxicj4KICAgICAgICBTT0ZUV0FSRS48YnI+CiAgICA8L2JvZHk+CjwvaHRtbD4K"


def getStyleCss() -> str:
    return "Ym9keSB7CiAgICBmb250LWZhbWlseTogR2FyYW1vbmQsIEJhc2tlcnZpbGxlLCBCYXNrZXJ2aWxsZSBPbGQgRmFjZSwgVGltZXMgTmV3IFJvbWFuLCBzZXJpZjsKfQoKYSB7CiAgICBjb2xvcjogcmdiKDEwMCwgMTAwLCAxMDApOwogICAgdHJhbnNpdGlvbjogMC43NXM7CiAgICB0ZXh0LWRlY29yYXRpb246IHVuZGVybGluZSAjQkJCIGRvdHRlZCAxcHg7Cn0KCmE6YWN0aXZlIHsKICAgIGNvbG9yOiByZ2IoNTAsIDUwLCA1MCk7CiAgICB0cmFuc2l0aW9uOiAwLjFzOwp9CgpociB7CiAgICBjb2xvcjogI0VFRTsKfQoKdGFibGUgewogICAgbWFyZ2luOiAzMHB4Owp9CgouZGF0YSB0ZCB7CiAgICBwYWRkaW5nOiA1cHg7CiAgICBib3JkZXItYm90dG9tOiBkb3R0ZWQgMXB4ICNBQUE7Cn0KCmJvZHkucmF3IGEgewogICAgdGV4dC1kZWNvcmF0aW9uOiBub25lOwp9Cgpib2R5LnJhdyB0YWJsZSB7CiAgICBtYXJnaW46IDMwcHg7Cn0KCmJvZHkucmF3IHRkLCB0aCB7CiAgICBwYWRkaW5nOiAxMHB4IDI1cHg7Cn0KCmJvZHkucmF3IHRoZWFkIHsKICAgIGNvbG9yOiAjRkZGOwogICAgYmFja2dyb3VuZDogIzU1NTsKfQoKYm9keS5yYXcgdGQ6bnRoLWNoaWxkKGV2ZW4pIHsKICAgIHRleHQtYWxpZ246IHJpZ2h0Owp9Cgpib2R5LnJhdyB0cjpudGgtY2hpbGQoZXZlbikgewogICAgYmFja2dyb3VuZDogI0VFRTsKfQoKYm9keS5yYXcgLmluZm8gewogICAgdGV4dC1hbGlnbjogY2VudGVyOwp9CgppbWcudHVydGxlIHsKICAgIHdpZHRoOiAxMDBweDsKICAgIGhlaWdodDogMTAwcHg7CiAgICBvcGFjaXR5OiAzNSU7CiAgICB0cmFuc2l0aW9uOiAwLjc1czsKfQoKaW1nLnR1cnRsZTphY3RpdmUgewogICAgb3BhY2l0eTogNzAlOwogICAgdHJhbnNpdGlvbjogMC4xczsKfQoKLnJvdC0xODAgewogICAgdHJhbnNmb3JtOiByb3RhdGUoLTE4MGRlZyk7Cn0KCi5yb3QtMTM1IHsKICAgIHRyYW5zZm9ybTogcm90YXRlKC0xMzVkZWcpOwp9Cgoucm90LTkwIHsKICAgIHRyYW5zZm9ybTogcm90YXRlKC05MGRlZyk7Cn0KCi5yb3QtNDUgewogICAgdHJhbnNmb3JtOiByb3RhdGUoLTQ1ZGVnKTsKfQoKLnJvdDQ1IHsKICAgIHRyYW5zZm9ybTogcm90YXRlKDQ1ZGVnKTsKfQoKLnJvdDkwIHsKICAgIHRyYW5zZm9ybTogcm90YXRlKDkwZGVnKTsKfQoKLnJvdDEzNSB7CiAgICB0cmFuc2Zvcm06IHJvdGF0ZSgxMzVkZWcpOwp9Cgoucm90MTgwIHsKICAgIHRyYW5zZm9ybTogcm90YXRlKDE4MGRlZyk7Cn0KCi5kcml2ZSB7CiAgICBoZWlnaHQ6IDQwMHB4Owp9Cgouc2ltcGxlIHsKICAgIGhlaWdodDogOTAwcHg7Cn0KCi5wcm8gewogICAgaGVpZ2h0OiAxMDAwcHg7Cn0KCi5wYW5lbCB7CiAgICB3aWR0aDogNjAwcHg7CiAgICBtYXJnaW46IGF1dG87CiAgICB0ZXh0LWFsaWduOiBjZW50ZXI7Cn0KCi5saW5rcyB7CiAgICB3aWR0aDogMzUwcHg7CiAgICBwYWRkaW5nOiAwOwogICAgbWFyZ2luOiAxMDBweCBhdXRvOwogICAgYm9yZGVyLXRvcDogMDsKICAgIGJvcmRlcjogMXB4IHNvbGlkICNCQkI7CiAgICBib3JkZXItcmFkaXVzOiAxNXB4IDE1cHggMCAwOwogICAgZm9udC1zaXplOiAyMHB4OwogICAgY29sb3I6ICM4ODg7Cn0KCi5saW5rcyBsaSB7CiAgICBsaXN0LXN0eWxlOiBub25lOwogICAgYmFja2dyb3VuZDogI0VFRTsKICAgIHBhZGRpbmc6IDEwcHggMjBweDsKICAgIGJvcmRlci10b3A6IDFweCBzb2xpZCAjQ0NDOwp9CgoubGlua3MgbGk6Zmlyc3QtY2hpbGQgewogICAgY29sb3I6ICNGRkY7CiAgICBiYWNrZ3JvdW5kOiAjNTU1OwogICAgYm9yZGVyOiBub25lOwogICAgYm9yZGVyLXJhZGl1czogMTBweCAxMHB4IDAgMDsKfQo="


files = {
    "favicon.ico":                (getFaviconIco,      ("image/vnd.microsoft.icon; charset=UTF-8",), "getFaviconIco"),
    "android-chrome-512x512.png": (getFavicon512Png,   ("image/png; charset=UTF-8",), "getFavicon512Png"),
    "android-chrome-192x192.png": (getFavicon192Png,   ("image/png; charset=UTF-8",), "getFavicon192Png"),
    "favicon.png":                (getFaviconPng,      ("image/png; charset=UTF-8",), "getFaviconPng"),
    "apple-touch-icon.png":       (getFavicon180Png,   ("image/png; charset=UTF-8",), "getFavicon180Png"),
    "safari-pinned-tab.svg":      (getSafariTabSvg,    ("image/svg+xml; charset=UTF-8",), "getSafariTabSvg"),
    "mstile-150x150.png":         (getMsTilePng,       ("image/png; charset=UTF-8",), "getMsTilePng"),
    "favicon-32x32.png":          (getFavicon32Png,    ("image/png; charset=UTF-8",), "getFavicon32Png"),
    "favicon-16x16.png":          (getFavicon16Png,    ("image/png; charset=UTF-8",), "getFavicon16Png"),

    "site.webmanifest":     (getSiteWebmanifest,    ("application/manifest+json; charset=UTF-8",), "getSiteWebmanifest"),
    "browserconfig.xml":    (getBrowserconfigXml,   ("application/xml; charset=UTF-8",), "getBrowserconfigXml"),
    "style.css":            (getStyleCss,           ("text/css; charset=UTF-8",), "getStyleCss"),
    "license.html":         (getLicenseHtml,        ("text/html; charset=UTF-8",), "getLicenseHtml"),

    "turtle_arrow.png":     (getTurtleArrowPng,  ("image/png; charset=UTF-8",), "getTurtleArrowPng"),
    "turtle_cross.png":     (getTurtleCrossPng,  ("image/png; charset=UTF-8",), "getTurtleCrossPng"),
    "turtle_f1.png":        (getTurtleF1Png,     ("image/png; charset=UTF-8",), "getTurtleF1Png"),
    "turtle_f2.png":        (getTurtleF2Png,     ("image/png; charset=UTF-8",), "getTurtleF2Png"),
    "turtle_f3.png":        (getTurtleF3Png,     ("image/png; charset=UTF-8",), "getTurtleF3Png"),
    "turtle_pause.png":     (getTurtlePausePng,  ("image/png; charset=UTF-8",), "getTurtlePausePng"),
    "turtle_play.png":      (getTurtlePlayPng,   ("image/png; charset=UTF-8",), "getTurtlePlayPng"),
    "turtle_repeat.png":    (getTurtleRepeatPng, ("image/png; charset=UTF-8",), "getTurtleRepeatPng"),
    "turtle_undo.png":      (getTurtleUndoPng,   ("image/png; charset=UTF-8",), "getTurtleUndoPng"),
}


def deleteDictionaries() -> None:
    global configModules, files

    for key, module in configModules.items():
        module.clear()
        exec("del inisetup.{}".format(key))

    configModules.clear()
    del configModules

    for _, value in files.items():
        exec("del inisetup.{}".format(value[2]))

    files.clear()
    del files

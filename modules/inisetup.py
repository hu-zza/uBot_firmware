import flashbdev, network, ubinascii, ujson, uos

firmware = (0, 1, 198)
initDatetime = (2021, 7, 23, 0, 2, 10, 0, 0)

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
    "json_get_limit": 8000,
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
    "period"        : 200,
    "timeout"       : 100,
    "port"          : 80,
    "backlog"       : 5,
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

def getTurtleSvg() -> str:
    return "PHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnPgogICAgPGRlZnM+CiAgICAgICAgPHN5bWJvbCBpZD0nYXJyb3cnIHdpZHRoPScxMDAnIGhlaWdodD0nMTAwJyB2aWV3Qm94PScwIDAgNDAwIDQwMCcgeG1sbnM6dj0naHR0cHM6Ly92ZWN0YS5pby9uYW5vJz4KICAgICAgICAgICAgPHBhdGggZD0nTTE4Ni42NjcgMy43MjlsLTkgLjk3NkM3MS42MDUgMTUuODUxLTguNTg5IDExNi44MTIgNC41MzcgMjIyLjY2NyAyNC44NzIgMzg2LjY0OCAyMjMuMDQgNDU1LjcyMyAzMzkuMzgxIDMzOS4zODEgNDU0LjYxNyAyMjQuMTQ1IDM4Ny45MDIgMjcuMzg3IDIyNiA0Ljk5N2MtNy4yNjItMS4wMDQtMzQuMjAyLTEuODczLTM5LjMzMy0xLjI2OE0yMDYuNzYzIDQzbDk1LjQ0NiAxMzUuNjY3IDEwLjM3MSAxNC41OTJjMS41NDMgMi4wMjggMS41ODQgMi4yMjEuNDAzIDEuODkxLS43MjQtLjIwMy0zLjcxNi0uODYtNi42NS0xLjQ2TDI5MiAxOTAuNjhsLTE5LTQuMDA0LTE3LjYyNC0zLjgwN2MtMTkuMTExLTQuMzItMTkuNDQ2LTMuNzU2LTE1LjcwMyAyNi40NjRsMS42NzEgMTUuMzM0IDEwLjA0OSA5Ni42NjZMMjUzLjY3OCAzNDRsMS4zOTUgMTQuODMzLjQ1MyA0LjVIMTQ5LjE2M2wuMzg4LTIuNWMuMjEzLTEuMzc1LjU3Mi00LjkuNzk3LTcuODMzczEuMjc1LTEzLjQzMyAyLjMzMi0yMy4zMzNsNi42MzctNjRjOS4yMjctODcuNzQzIDguNTM2LTc5Ljc3NSA3LjEwNi04MS45NTYtMS41MDMtMi4yOTYtNC4wMy0zLjIxOC03LjM5My0yLjctMy4wMDkuNDY0LTMxLjQ1NSA2LjA1Ny01Ni4yOTMgMTEuMDY5LTguOTQ1IDEuODA1LTE2LjM2IDMuMTg2LTE2LjQ3OCAzLjA2OHM0LjczMy02Ljk0OSAxMC43NzktMTUuMTgxbDE3LjE0NC0yMy4zNzdMMTUwLjY4NiAxMDdsMTYuODk0LTIzIDE3LjY5MS0yNCAxMy41NjItMTguNTA2YzEuODgyLTIuNjYyIDMuNjE2LTQuNjEyIDMuODU1LTQuMzM0czIuMDczIDIuOTA3IDQuMDc1IDUuODQnIGZpbGwtcnVsZT0nZXZlbm9kZCcvPgogICAgICAgIDwvc3ltYm9sPgoKICAgICAgICA8c3ltYm9sIGlkPSdwbGF5JyB3aWR0aD0nMTAwJyBoZWlnaHQ9JzEwMCcgdmlld0JveD0nMCAwIDQwMCA0MDAnIHhtbG5zOnY9J2h0dHBzOi8vdmVjdGEuaW8vbmFubyc+CiAgICAgICAgICAgIDxwYXRoIGQ9J00xODYuNjY3IDMuNzI5bC05IC45NzZDNzEuNjA1IDE1Ljg1MS04LjU4OSAxMTYuODEyIDQuNTM3IDIyMi42NjcgMjQuODcyIDM4Ni42NDggMjIzLjA0IDQ1NS43MjMgMzM5LjM4MSAzMzkuMzgxIDQ1NC42MTcgMjI0LjE0NSAzODcuOTAyIDI3LjM4NyAyMjYgNC45OTdjLTcuMjYyLTEuMDA0LTM0LjIwMi0xLjg3My0zOS4zMzMtMS4yNjhtLTk2LjU4MiA5OC42NDhjNC44MjQgMi40NDQgOC44MDcgNi42OTggMTAuNDk1IDExLjIxbDEuNDIgMy43OTZ2MTY1LjQyNmwtMi4wMTIgNC4yMTZjLTcuODA0IDE2LjM1Mi0zMC41ODUgMTYuMjM1LTM4Ljc1MS0uMTk5bC0xLjU3LTMuMTU5LS4xNzUtODIuMzAzYy0uMTk0LTkxLjU2OC0uNDMzLTg2LjQxNyA0LjMwNS05Mi44NzMgNS41OTMtNy42MjMgMTcuNzM4LTEwLjQ0NyAyNi4yODgtNi4xMTRtNjkuODE3LTEuNzM4YzEuMjI1LjM1MSA5LjMyMyA0LjUyMSAxNy45OTYgOS4yNjZMMjkzIDE3Mi42NTRjMzMuNDU4IDE4LjEwMiA0NS44MTQgMjUuMDQxIDQ2LjM0MSAyNi4wMjcgMS4xNDQgMi4xMzctMS4wOTcgMy41OTYtMjcuNjc0IDE4LjAyMWwtNDUgMjQuNDY3TDIyOSAyNjEuNjc3bC00My4zMzMgMjMuNjY1Yy0yOS40NzggMTYuMTQ4LTMyLjgzNiAxNi45OTMtMzYuODI4IDkuMjYtMS42NDItMy4xODEtLjgzNy0xODkuNDI1LjgyOC0xOTEuMjkgMi41ODktMi45MDIgNi4xNzQtMy44MzggMTAuMjM1LTIuNjczJyBmaWxsLXJ1bGU9J2V2ZW5vZGQnLz4KICAgICAgICA8L3N5bWJvbD4KCiAgICAgICAgPHN5bWJvbCBpZD0ncGF1c2UnIHdpZHRoPScxMDAnIGhlaWdodD0nMTAwJyB2aWV3Qm94PScwIDAgNDAwIDQwMCcgeG1sbnM6dj0naHR0cHM6Ly92ZWN0YS5pby9uYW5vJz4KICAgICAgICAgICAgPHBhdGggZD0nTTE4Ni42NjcgMy43MjlsLTkgLjk3NkM0Mi4zNTEgMTguOTI2LTM3LjI4OCAxNjguMjU0IDI1LjI5NyAyOTAuNDExYzY0Ljc2MyAxMjYuNDA5IDI0MC41NyAxNDQuMDAzIDMyOC45NzYgMzIuOTIyQzQ0OS40OTkgMjAzLjY4MiAzNzcuOTA0IDI2LjAwNSAyMjYgNC45OTdjLTcuMjYyLTEuMDA0LTM0LjIwMi0xLjg3My0zOS4zMzMtMS4yNjhtLTIxLjI0OCA5OC42NDhjNC44MjMgMi40NDQgOC44MDYgNi42OTggMTAuNDk0IDExLjIxbDEuNDIgMy43OTZWMjgxLjk1bC0xLjQzNiAzLjgzOGMtNi40NzIgMTcuMjk4LTMwLjkyNiAxNy45NDQtMzkuMzI3IDEuMDM4bC0xLjU3LTMuMTU5LS4xNzQtODIuMzAzYy0uMTk1LTkxLjU2OC0uNDMzLTg2LjQxNyA0LjMwNC05Mi44NzMgNS41OTMtNy42MjMgMTcuNzM4LTEwLjQ0NyAyNi4yODktNi4xMTRtODguNjY2IDBjNC44MjQgMi40NDQgOC44MDcgNi42OTggMTAuNDk1IDExLjIxbDEuNDIgMy43OTZWMjgxLjk1bC0xLjQzNiAzLjgzOGMtNi40NzIgMTcuMjk4LTMwLjkyNiAxNy45NDQtMzkuMzI3IDEuMDM4bC0xLjU3LTMuMTU5LS4xNzUtODIuMzAzYy0uMTk0LTkxLjU2OC0uNDMzLTg2LjQxNyA0LjMwNS05Mi44NzMgNS41OTMtNy42MjMgMTcuNzM4LTEwLjQ0NyAyNi4yODgtNi4xMTQnIGZpbGwtcnVsZT0nZXZlbm9kZCcvPgogICAgICAgIDwvc3ltYm9sPgoKICAgICAgICA8c3ltYm9sIGlkPSdyZXBlYXQnIHdpZHRoPScxMDAnIGhlaWdodD0nMTAwJyB2aWV3Qm94PScwIDAgNDAwIDQwMCcgeG1sbnM6dj0naHR0cHM6Ly92ZWN0YS5pby9uYW5vJz4KICAgICAgICAgICAgPHBhdGggZD0nTTE4Ni42NjcgMy43MjlsLTkgLjk3NkM0Mi4zNTEgMTguOTI2LTM3LjI4OCAxNjguMjU0IDI1LjI5NyAyOTAuNDExYzY0Ljc2MyAxMjYuNDA5IDI0MC41NyAxNDQuMDAzIDMyOC45NzYgMzIuOTIyQzQ0OS40OTkgMjAzLjY4MiAzNzcuOTA0IDI2LjAwNSAyMjYgNC45OTdjLTcuMjYyLTEuMDA0LTM0LjIwMi0xLjg3My0zOS4zMzMtMS4yNjhtMjIuNjY2IDU0Ljk1NWMzMC4xNzUgMi4yODIgNjEuMDA4IDE1LjExNSA4Mi40OTYgMzQuMzM1bDQuMjc4IDMuODI2IDMuMTEzLTIuOTczIDEyLjk3OC0xMi41ODljMTIuMjU4LTExLjk1IDE0LjM2Ny0xMi45NjUgMjAuODMtMTAuMDMgNy4zOTQgMy4zNTkgNy4wNDkuNzEgNi44MjcgNTIuNDY2bC0uMTg4IDQ0LjA1Mi0xLjkyMyAyLjUyYy0zLjk2NyA1LjIwMS0yLjA2OCA1LjAxMS01MC4yNjUgNS4wMjgtNDkuODYzLjAxNy00OC4yNDIuMjM2LTUxLjU1OS02Ljk4Ni0zLjE2OC02LjkwMS0yLjY5My03LjczNSAxMy45MDQtMjQuNDI2bDEzLjY4My0xMy43NTktNC43Ny0zLjkwN2MtMzYuODU3LTMwLjE5Mi05MS4wMzUtMjcuNDE4LTEyNC43NTkgNi4zODgtNTIuNTgxIDUyLjcxLTI1LjUxOCAxNDIuNDI5IDQ3LjQ3NSAxNTcuMzg4IDQ1LjI1NCA5LjI3NCA5Mi4zNS0xNy41OTYgMTA2LjQ4Mi02MC43NTMgMi40NzQtNy41NTUuMjg0LTYuOTAyIDIzLjkyNy03LjEyNGwyMC42MzgtLjE5NCAyLjE2NSAxLjgyMWMyLjg4MSAyLjQyNSAyLjU4MiA1Ljg1OC0xLjYxNCAxOC41NjYtNDIuNzMyIDEyOS40MTktMjI1LjE5IDEyNy41OTgtMjY3LjI0OS0yLjY2NkMzOC43MTQgMTU1Ljc3IDEwMC41MSA2NS4wNDkgMTg5LjA2MSA1OC43MTNjMTAuNzEyLS43NjYgMTAuNTMtLjc2NiAyMC4yNzItLjAyOScgZmlsbC1ydWxlPSdldmVub2RkJy8+CiAgICAgICAgPC9zeW1ib2w+CgogICAgICAgIDxzeW1ib2wgaWQ9J0YxJyB3aWR0aD0nMTAwJyBoZWlnaHQ9JzEwMCcgdmlld0JveD0nMCAwIDQwMCA0MDAnIHhtbG5zOnY9J2h0dHBzOi8vdmVjdGEuaW8vbmFubyc+CiAgICAgICAgICAgIDxwYXRoIGQ9J00xODYuNjY3IDMuNzI5bC05IC45NzZDNDIuMzUxIDE4LjkyNi0zNy4yODggMTY4LjI1NCAyNS4yOTcgMjkwLjQxMWM2NC43NjMgMTI2LjQwOSAyNDAuNTcgMTQ0LjAwMyAzMjguOTc2IDMyLjkyMkM0NDkuNDk5IDIwMy42ODIgMzc3LjkwNCAyNi4wMDUgMjI2IDQuOTk3Yy03LjI2Mi0xLjAwNC0zNC4yMDItMS44NzMtMzkuMzMzLTEuMjY4bTIyLjMwOCA4NC44OTZjLjIxMi4zNDQtMS4zMjEgOS43NzctMy40MDcgMjAuOTYxbC0zLjc5MyAyMC4zMzUtMi41OTkuNDM5Yy0zLjI1Ni41NS0yLjQxMiAyLjM2Ni02Ljk5LTE1LjAyN2wtMy45NDgtMTUtNTkuNTcxLS4zNDd2NzQuODc3bDIyLjA2Mi0uMzUxYzI1Ljk5Ny0uNDE0IDIzLjA2My44NTEgMjYuODc1LTExLjU4NWwyLjgzOC05LjI2IDYuNTU4LS4zOTItLjIxMSA1My43MjVoLTYuNGwtMi45MTMtOS42NjdjLTMuODUxLTEyLjc3OS0uODA5LTExLjQzMi0yNi43NDctMTEuODQ1bC0yMi4wNjItLjM1MXYzNi4zODRjMCA0Mi4zMzktMS4xODYgMzcuNDI2IDkuODQ4IDQwLjgxOGw5LjQ4NSAyLjkxN2MxLjM3Ny40MjUgMS43MDIuOTk3IDEuODcyIDMuMjk2bC4yMDUgMi43ODFIODMuMzk0bC0uNDQ3LTIuMzgzYy0uNTgxLTMuMDkzLS42OC0zLjAyOCA5LjA1My01LjkxMiA0LjU4My0xLjM1OCA4Ljc4My0yLjkwOCA5LjMzMy0zLjQ0NCAxLjA4Ni0xLjA1OCAxLjU3OS0xNTMuODcuNTA5LTE1Ny42NzYtLjU1MS0xLjk1OS0uOTY4LTIuMTU4LTExLjUwOS01LjQ5Mkw4MyA5NC4xMDZsLS40MS01LjQzMSA0OC4yMDUtLjE3NSA2Mi45OTktLjMzOGM4LjY4NC0uMDk1IDE0Ljk1NC4wOTYgMTUuMTgxLjQ2M202Mi42MTUgNjIuMDQyYy0xLjc1NCA1My4zMTEtMS45ODMgNzIuMjY2LTEuMTUxIDk1LjI0My41MzUgMTQuNzc4LS40IDEzLjUyNCAxMi41NjEgMTYuODQ4IDExLjA5MiAyLjg0NiAxMi4zMzMgMy41MiAxMi4zMzMgNi43MDN2MS44NzJoLTc0bC0uMTExLTEuNjY2LS4xNjYtMi43OTJjLS4wNDUtLjkwOSAyLjEwMS0xLjY2NSAxMS4xOTUtMy45NDIgNi4xODgtMS41NDkgMTEuNzM4LTMuMzA0IDEyLjMzNC0zLjkgMS4wMzQtMS4wMzYgMS43NDEtOTIuOTI5LjcyMi05My45NDgtLjE2OS0uMTY5LTUuNTU3LS44MDItMTEuOTc0LTEuNDA2LTE1LjMxMy0xLjQ0My0xNC41MjItMS4yMy0xNS4wNS00LjA0OS0uNTk4LTMuMTg3LTEuMzQtMi45MDQgMTQuMjE1LTUuNDA2TDI1NyAxNTAuMDcyYzEzLjgzNS0yLjUgMTQuNjkxLTIuNDY1IDE0LjU5LjU5NScgZmlsbC1ydWxlPSdldmVub2RkJy8+CiAgICAgICAgPC9zeW1ib2w+CgogICAgICAgIDxzeW1ib2wgaWQ9J0YyJyB3aWR0aD0nMTAwJyBoZWlnaHQ9JzEwMCcgdmlld0JveD0nMCAwIDQwMCA0MDAnIHhtbG5zOnY9J2h0dHBzOi8vdmVjdGEuaW8vbmFubyc+CiAgICAgICAgICAgIDxwYXRoIGQ9J00xODYuNjY3IDMuNzI5bC05IC45NzZDNDIuMzUxIDE4LjkyNi0zNy4yODggMTY4LjI1NCAyNS4yOTcgMjkwLjQxMWM2NC43NjMgMTI2LjQwOSAyNDAuNTcgMTQ0LjAwMyAzMjguOTc2IDMyLjkyMkM0NDkuNDk5IDIwMy42ODIgMzc3LjkwNCAyNi4wMDUgMjI2IDQuOTk3Yy03LjI2Mi0xLjAwNC0zNC4yMDItMS44NzMtMzkuMzMzLTEuMjY4bTIyLjMwOCA4NC44OTZjLjIxMi4zNDQtMS4zMjEgOS43NzctMy40MDcgMjAuOTYxbC0zLjc5MyAyMC4zMzUtMi41OTkuNDM5Yy0zLjI1Ni41NS0yLjQxMiAyLjM2Ni02Ljk5LTE1LjAyN2wtMy45NDgtMTUtNTkuNTcxLS4zNDd2NzQuODc3bDIyLjA2Mi0uMzUxYzI1Ljk5Ny0uNDE0IDIzLjA2My44NTEgMjYuODc1LTExLjU4NWwyLjgzOC05LjI2IDYuNTU4LS4zOTItLjIxMSA1My43MjVoLTYuNGwtMi45MTMtOS42NjdjLTMuODUxLTEyLjc3OS0uODA5LTExLjQzMi0yNi43NDctMTEuODQ1bC0yMi4wNjItLjM1MXYzNi4zODRjMCA0Mi4zMzktMS4xODYgMzcuNDI2IDkuODQ4IDQwLjgxOGw5LjQ4NSAyLjkxN2MxLjM3Ny40MjUgMS43MDIuOTk3IDEuODcyIDMuMjk2bC4yMDUgMi43ODFIODMuMzk0bC0uNDQ3LTIuMzgzYy0uNTgxLTMuMDkzLS42OC0zLjAyOCA5LjA1My01LjkxMiA0LjU4My0xLjM1OCA4Ljc4My0yLjkwOCA5LjMzMy0zLjQ0NCAxLjA4Ni0xLjA1OCAxLjU3OS0xNTMuODcuNTA5LTE1Ny42NzYtLjU1MS0xLjk1OS0uOTY4LTIuMTU4LTExLjUwOS01LjQ5Mkw4MyA5NC4xMDZsLS40MS01LjQzMSA0OC4yMDUtLjE3NSA2Mi45OTktLjMzOGM4LjY4NC0uMDk1IDE0Ljk1NC4wOTYgMTUuMTgxLjQ2M204Mi42OTIgNjAuMDNDMzA5LjI0MyAxNTQuMjk3IDMxOCAxNjQuODQ0IDMxOCAxODAuMzcxYzAgMjEuOTktMTQuNDQ5IDM4LjUyMi01Ni41NDQgNjQuNjk1TDI1MS45MTEgMjUxbDMyLjE3Mi4xNzNjMTcuNjk0LjA5NSAzMi4zODktLjA1NSAzMi42NTYtLjMzM3MyLjY0OC01LjIyMiA1LjI5My0xMC45ODVsNC44MDktMTAuNDc4IDIuNzQ2LS41NTZjMS42NTgtLjMzNiAyLjg0Ny0uMzA3IDMgLjA3My4yOTQuNzI4LTEuODQ0IDM4LjY5LTIuMzA1IDQwLjkzOWwtLjMwNyAxLjVIMjI0LjA2bC0uMzMxLTIuMTY2Yy0uMTgyLTEuMTkyLS40NTctMy41NzEtLjYxLTUuMjg3bC0uMjc4LTMuMTIgOS43NDYtNi40NzVjNDUtMjkuODk0IDYwLjMzMi00Ny4zNzIgNTguNTI1LTY2LjcxNy0xLjk4Ny0yMS4yNzktMjcuMDE3LTI5LjU5MS01My45OTItMTcuOTI5LTYuMTY4IDIuNjY3LTUuNzE3IDIuNzczLTguMzktMS45NjItMi42NDktNC42OTUtMi43OTItNC4yNTggMi40MzctNy40NTUgMjAuMTE4LTEyLjI5OSA0My45OTUtMTYuODY0IDYwLjUtMTEuNTY3JyBmaWxsLXJ1bGU9J2V2ZW5vZGQnLz4KICAgICAgICA8L3N5bWJvbD4KCiAgICAgICAgPHN5bWJvbCBpZD0nRjMnIHdpZHRoPScxMDAnIGhlaWdodD0nMTAwJyB2aWV3Qm94PScwIDAgNDAwIDQwMCcgeG1sbnM6dj0naHR0cHM6Ly92ZWN0YS5pby9uYW5vJz4KICAgICAgICAgICAgPHBhdGggZD0nTTE4Ni42NjcgMy43MjlsLTkgLjk3NkM0Mi4zNTEgMTguOTI2LTM3LjI4OCAxNjguMjU0IDI1LjI5NyAyOTAuNDExYzY0Ljc2MyAxMjYuNDA5IDI0MC41NyAxNDQuMDAzIDMyOC45NzYgMzIuOTIyQzQ0OS40OTkgMjAzLjY4MiAzNzcuOTA0IDI2LjAwNSAyMjYgNC45OTdjLTcuMjYyLTEuMDA0LTM0LjIwMi0xLjg3My0zOS4zMzMtMS4yNjhtMjIuMzA4IDg0Ljg5NmMuMjEyLjM0NC0xLjMyMSA5Ljc3Ny0zLjQwNyAyMC45NjFsLTMuNzkzIDIwLjMzNS0yLjU5OS40MzljLTMuMjU2LjU1LTIuNDEyIDIuMzY2LTYuOTktMTUuMDI3bC0zLjk0OC0xNS01OS41NzEtLjM0N3Y3NC44NzdsMjIuMDYyLS4zNTFjMjUuOTk3LS40MTQgMjMuMDYzLjg1MSAyNi44NzUtMTEuNTg1bDIuODM4LTkuMjYgNi41NTgtLjM5Mi0uMjExIDUzLjcyNWgtNi40bC0yLjkxMy05LjY2N2MtMy44NTEtMTIuNzc5LS44MDktMTEuNDMyLTI2Ljc0Ny0xMS44NDVsLTIyLjA2Mi0uMzUxdjM2LjM4NGMwIDQyLjMzOS0xLjE4NiAzNy40MjYgOS44NDggNDAuODE4bDkuNDg1IDIuOTE3YzEuMzc3LjQyNSAxLjcwMi45OTcgMS44NzIgMy4yOTZsLjIwNSAyLjc4MUg4My4zOTRsLS40NDctMi4zODNjLS41ODEtMy4wOTMtLjY4LTMuMDI4IDkuMDUzLTUuOTEyIDQuNTgzLTEuMzU4IDguNzgzLTIuOTA4IDkuMzMzLTMuNDQ0IDEuMDg2LTEuMDU4IDEuNTc5LTE1My44Ny41MDktMTU3LjY3Ni0uNTUxLTEuOTU5LS45NjgtMi4xNTgtMTEuNTA5LTUuNDkyTDgzIDk0LjEwNmwtLjQxLTUuNDMxIDQ4LjIwNS0uMTc1IDYyLjk5OS0uMzM4YzguNjg0LS4wOTUgMTQuOTU0LjA5NiAxNS4xODEuNDYzbTc5LjM1OCA1OS45OGMyMC4xNzIgNS4zNDggMzEuMzM0IDE3LjIzMSAzMS4zMzQgMzMuMzYgMCAxOC41NzYtMTEuOCAzMS44NDktMzYuODM0IDQxLjQzMy01LjM2MiAyLjA1My01LjI1NSAyLjMyIDEuMTMgMi44MTMgMzAuODQ1IDIuMzc4IDQ5LjUxNCAyNC44MjcgNDIuNzI1IDUxLjM3NC03LjY5MyAzMC4wNzktNDUuMzYzIDQ5LjY5MS0xMDEuNDE1IDUyLjc5OS05LjUwMS41MjctOC44NTIuODgtOS42MTctNS4yMzZsLS40NjUtMy43MjcgMi4yMzgtLjM1YzEuMjMxLS4xOTMgNC4zMzgtLjUyOSA2LjkwNC0uNzQ4IDQ3LjAyNC00LjAxIDc1Ljc3OS0yMi45NDMgNzUuOTIxLTQ5Ljk5LjEyNi0yNC4wOS0xOC45MTQtMzcuMzkyLTQ5LjE4NS0zNC4zNjEtNC40MjMuNDQzLTguMjM1LjkyNS04LjQ3MSAxLjA3LS41MjQuMzI0LTEuMjQ3LTMuODE0LTEuMjU3LTcuMTk2LS4wMDktMi43NzUtLjQwMS0yLjU3OCA3LjY1OS0zLjg0MiAzMi4xOTgtNS4wNDkgNDkuNTk0LTI0LjMzMSA0MS40OTEtNDUuOTg3LTYuNzYzLTE4LjA3Ni0zNi45NzgtMjIuNDctNjMuMzkyLTkuMjItMi4xNDUgMS4wNzYtMy45NzYgMS44NjItNC4wNjkgMS43NDctMS4wMzctMS4yOTYtNS4wMy04LjA1LTUuMDMtOC41MDkgMC0xLjczNSAxNy41My0xMC41NDQgMjYuNjY3LTEzLjQwMSAxMy44MTctNC4zMTkgMzEuODY0LTUuMTU4IDQzLjY2Ni0yLjAyOScgZmlsbC1ydWxlPSdldmVub2RkJy8+CiAgICAgICAgPC9zeW1ib2w+CgogICAgICAgIDxzeW1ib2wgaWQ9J3VuZG8nIHdpZHRoPScxMDAnIGhlaWdodD0nMTAwJyB2aWV3Qm94PScwIDAgNDAwIDQwMCcgeG1sbnM6dj0naHR0cHM6Ly92ZWN0YS5pby9uYW5vJz4KICAgICAgICAgICAgPHBhdGggZD0nTTE4Ni42NjcgMy43MjlsLTkgLjk3NkM3MS42MDUgMTUuODUxLTguNTg5IDExNi44MTIgNC41MzcgMjIyLjY2NyAyNC44NzIgMzg2LjY0OCAyMjMuMDQgNDU1LjcyMyAzMzkuMzgxIDMzOS4zODEgNDU0LjYxNyAyMjQuMTQ1IDM4Ny45MDIgMjcuMzg3IDIyNiA0Ljk5N2MtNy4yNjItMS4wMDQtMzQuMjAyLTEuODczLTM5LjMzMy0xLjI2OG0tNCAzNS41MzNjNi4zNDMgMi42MzcgNi4yNzcgMi4yODMgNi41NDkgMzQuNjkxLjEzMSAxNS42MDkuNDM2IDI4LjU2NS42NzggMjguNzkyczQuOTM5IDEuMDQzIDEwLjQzOSAxLjgxNkMyOTYuMTE2IDExOC4wMTYgMzU4LjM2IDIxMC43MTEgMzM0LjI1NiAzMDRjLTMuNzIzIDE0LjQwOC0xNi4wMDkgNDIuOTk5LTE2LjMxNSAzNy45NjctNC4xMzctNjguMDE2LTU4LjU5Mi0xMjUuNTM2LTEyNC4xMDgtMTMxLjA5M2wtNC41LS4zODItLjA3OSAyMi4yNTRjLS4xMTEgMzEuNDUtLjI2IDM0LjQ5NC0xLjc4MyAzNi41NTItMi45OTkgNC4wNTEtOC4wNTUgNS43NDEtMTIuMjYxIDQuMDk5LTMuMjc4LTEuMjgtMTE3LjY5MS05Ni4zNzctMTMwLjY1MS0xMDguNTk0LTguNTY1LTguMDc0LTcuNzA4LTEwLjg0MSA3LjMzOC0yMy42OTdMMTY4LjE1NiA0NC4xMmM3LjYyMi02LjE5MSA5LjY2Mi02Ljg3NCAxNC41MTEtNC44NTgnIGZpbGwtcnVsZT0nZXZlbm9kZCcvPgogICAgICAgIDwvc3ltYm9sPgoKICAgICAgICA8c3ltYm9sIGlkPSdjcm9zcycgd2lkdGg9JzEwMCcgaGVpZ2h0PScxMDAnIHZpZXdCb3g9JzAgMCA0MDAgNDAwJyB4bWxuczp2PSdodHRwczovL3ZlY3RhLmlvL25hbm8nPgogICAgICAgICAgICA8cGF0aCBkPSdNMTg2LjY2NyAzLjcyOWwtOSAuOTc2QzcxLjYwNSAxNS44NTEtOC41ODkgMTE2LjgxMiA0LjUzNyAyMjIuNjY3IDI0Ljg3MiAzODYuNjQ4IDIyMy4wNCA0NTUuNzIzIDMzOS4zODEgMzM5LjM4MSA0NTQuNjE3IDIyNC4xNDUgMzg3LjkwMiAyNy4zODcgMjI2IDQuOTk3Yy03LjI2Mi0xLjAwNC0zNC4yMDItMS44NzMtMzkuMzMzLTEuMjY4TTk4LjgwMSA2OS40MTZjNy44MzIgMS42NjIgNy41OTggMS40NTQgNTUuNTMyIDQ5LjMwNWw0NS4zMzQgNDUuMjU0TDI0NSAxMTguNzI0YzQ4LjUyMS00OC40MzMgNDcuNzUxLTQ3Ljc1NSA1Ni4yMDItNDkuNDE4IDE1LjkwNi0zLjEyOSAzMS44MjkgMTIuNzEyIDI4LjgwNSAyOC42NTgtMS41MDYgNy45NDEtLjUxIDYuODE2LTQ5LjE5MiA1NS41MzRsLTQ1Ljc5NyA0NS44MzEgNDUuNDIyIDQ1LjUwMmM0NC43MTggNDQuNzk2IDQ2LjkwMyA0Ny4xNzcgNDguNzc2IDUzLjE2OSA2LjM3NiAyMC4zOTQtMTUuNjExIDM5LjE0Ni0zNC43NTggMjkuNjQ1LTIuNzQzLTEuMzYxLTEyLjgzMS0xMS4wOC00OC43OTMtNDcuMDE0bC00NS45OTgtNDUuMjk4Yy0uMzY1IDAtMjEuMDY0IDIwLjM4NC00NS45OTkgNDUuMjk4LTQ4LjM0NSA0OC4zMDctNDcuODE3IDQ3Ljg0LTU1Ljk5MiA0OS40ODJDODAuOTE4IDMzMy40NzggNjQuODcyIDMxNC43OCA3MC4xMTggMjk4YzEuODczLTUuOTkyIDQuMDU3LTguMzczIDQ4Ljc3NS01My4xNjlsNDUuNDIyLTQ1LjUwMi00NS43OTctNDUuODMxYy00OC42ODItNDguNzE4LTQ3LjY4Ni00Ny41OTMtNDkuMTkxLTU1LjUzNC0zLjA5OC0xNi4zMzQgMTMuMDk5LTMyLjAyMiAyOS40NzQtMjguNTQ4JyBmaWxsLXJ1bGU9J2V2ZW5vZGQnLz4KICAgICAgICA8L3N5bWJvbD4KICAgIDwvZGVmcz4KPC9zdmc+Cg=="


def getFavicon512Png() -> str:
    return "iVBORw0KGgoAAAANSUhEUgAAAgAAAAIABAMAAAAGVsnJAAAABGdBTUEAALGPC/xhBQAAAAFzUkdCAK7OHOkAAAAeUExURUxpcUNDQ0JCQkRERP///2hoaObm5oqKiqmpqcnJyZHxpT4AAAADdFJOUwCkT9Z+4TIAAAzXSURBVHja7d3LWty4EgDghrwAhBdgwgsAat/W7evaziRZt8MhaztfOOvuOUPW9pkMbzuQZEJffJVKwtVV2gYc/FuqKkm+zGZN7c3pmTiwdnr6Zja0/SYOtL2mffoDCS7EQbfrntM/PhMH3q7OaZ9/twCF838UaAcgcf4dAheCSGvJBUeCTDunPABaB8GFINQuGzKAINXOKQ+AxorwSAjaXeCMGsA18Q6w2wUu6AFcE04B+13gFUWAS8ohcKccPBKC9hi4oAnwPAZonv/zGCA6Ap7HwAVVgEvKOWBjDBwLso14CBDihHYI+DcInNEFuKJcBfwKAkeUAc6pzgQ3o+AFZYBL2jHwx7IQ5fN/SgPHpAEE8STwlAaIA5zQzoJPABe0AS4Z4Iw2wDUDEAe4ol0IMgADkAcQDMAADMAADMAADMAADMAADMAADMAADMAADMAADMAADMAADMAADMAADCDR3r599+XL3f39w8NfNze+Hyod6u2vQ+W+H0wb4MPDw9MJ77VC4lhff5zxTkumDVD6zW0pcayWQ6WTBsha/uoIDmCJsgfEcAAR9R4QoOwBARzAAmUPWFCPAYBZoELZAyo4gBVKAIm/2mo5VEEdAGchVMABCJQAKRhAghNAgAHEKAFCOIAIJUACBxCgBIjhABbUAZYoASI4gAolQAAHsEIJIDNwHbOVsF6AJRxAihKgggMQKAFWYAAhToACDCChDhDjBEjBACKcAAIMIEAJEMIBLFACJHAAS5QAMRxAhRJAKnK5ZqcCWAAKlAABHECKEmABByBQAizBABKcABUYQIwTYAUGEOEEKMAAApwAKRjAgjrAEieAAAOoUALILWN5ZithnQAJHECBEiCGA0hRAkRwAAIlQAAGEFIHSHACLMAAYpwASzCACCdABQYQ4ARYgQEscAIUYABLnABy1YttdiqAA2CFE0CAARQoAUI4gBQlQAIHIFACxGAAIU6ACAwgxgkQgAFEOAEWYAABKYC52UpYI8ASDGCJE6ACA6hwAqzAAFbTB5jD1a9zs5WwRoAU7FApTgC4QwniACFOgATsUAl1gBgnQAx2qAgngOyfnZmdCugDCMAAFjgBFmAAS5wASzCACidABQawog5Q4ARYgQGkOAEKMACBEyCFAgiRAoCtrcQ4AUIwgAgngPQUrjRbCWsDiMEAFtQBljgBIjCACidAAAawwgmwAAMocAIswQBSnAAVGIDACbCCAgipAyRIAQoogBgpQAoFECEFkD7U2uxUQBdACAawwAmQgAEscQLEYAAVTgD50FWbnQpMH6DACSAfuw1PBXQBSMduy/BUQBeAdOx2DE8FdAFIx27XcCWsC0A6dnuGK2FdAAXUkQJqAJnhSlgXANhkcIkUAE0lrAlAPnnlhithTQDSk0HL8KK4LgDp7O2YroQ1AUhnb9d0JawJQDp726Yr4akBZIYXxXUBSJcvphfFdQFIly+16amAJgDp8sU3PRXQBCBbvli+6amAJgDZ8sX1TU8FgABsoPLF9k1PBSYGkPmmpwKaAKCyoP6pgB4A6fqtNj4V0AMgXb/5xqcCegBk6zfHNz4V0AMgW795vvFKWA+AbP0GuMWIE6A0XwnrAZAtYGvzlbAeANkC1j8UAMkC1qEO4PmHEgMkAeYHAyA5hSmpA+TEASzD75HTCCA3iXWpA8ypA5SG3yU5OYCaOIBl+MMCk8sCLnUA2/C3NSYHUFIHqA8IQGYyZBn+0uTkAFzqAHPDH1ud3JJYeUgAMitZueHvDWsFkJjGN39xmxCA7Rv+5LZWAIlZbHZQABKTuNqH+3TxywOMn8M0l0FoAcZXsF4LwBIngC8dAm7vDwOgkA0Bq516YIEUYCUbAooDAahkQ0C6kw4CpAALyRAQ7j41hRUgkAwByS5AhBQglgwB0e6sMEYKEEqGgOBQAEbO48uN2JEdxCMzI/NgvpE9MpQPTWVKJayz6TZH+dic2g1+9ubIsVE+OLlW2tVcb15v2/CSEAxArbKjYW2FPA8lQK6ynOttlT0uyqfHlVYyyq3I4WJ8f4Cl9I2VfGsK4WB8hYajsrPvbl9uC+NLVFyVPZ1sO+JZGF+j46ksaOc7aBhfpGQrfHPV2c2dhm+SAQFQ+fB0tvsrOcKXqal8e73eDXg1wtfpreV3tdy9UbNG+ELFRoBgdOepmg5WYQBo3NsfNAasfO9ilwjfKiu/t+/tD/cM34uVLfl9vfV+xsvwvVu8BSAe+ZtR4/Iahtfrt9zeMmAMZA2dHeplDAYB3BaAYFQI/HfIePg+stK2ud/be+2mM3XxfWan5Qan/r+9burr7ph+9H4SAPM2gGhMzwlbIkpnLM0/TgEgawPoCWDrxhMd825pTz1EQACUrQDBiNARtJVVRSdhWLw8wNqX6gJ1S8DIBxdUDsCKAQRA3Q7wcXjuKNoOF/WMvf+8OEDeDhCmg9laO1TYU0fGLw7g+xJdwG5dRl4PXVmwIaZLAABWF0BbF7Dy1ng5eKc1h5gwAwA4XQBtI7jjw5JDP7xrg6wZAQC4nQDNHdjr+LGhHy6rQZZNAQC8boCmQeB0PR5lD+tFHszCuX4AP9kTsOqurTR7WDmRw+wdAQDMewD28lTD+W8GOm9QRfk70KKhCQA/3rqCTt69fuYOWVt5ziIvXwpnvQB+8sfzj/8371k9cobkkhJqyQwAoPQHtE+fv/cC6y7vXTtprCv+v/1/fgBbNAUA2Kncbtoq408PDzeDqoX+bPoe7g4KAICdkNa+QNTRlv1zi81RBLhkqAHAkQBYDZhd3n7+8c/vasjdYwCAvZydjwcYFlQ+/X1//5DD7pvoAChHn388Nq3A3USlDmDtAdhqIWBAYQG4a6AO4OwBjA8CxbBldh1vWFAHcPfr9rFBIBw1vYTdOlUH8PYBspEA0ZgFBuC7B+ABiv75Yd8OkuzYeRmAhqdGrZEA6fBVVvCb6NQB5g0XZa2QBMf8ejAFgKwBYK6QBMcUAqupArgKSXCMXzoFgLLpqoxJhMnoRTbIO6nVAdZNAKXKCBicB6tJANRNAJ6vlMqk6qdJAVgqI6BzuxX6WQJ1gLwxMq+VirnS2AgAAGhOTbavEsltYyNAHcBqvi6Dx0AksdsGeROtMoDT0jHXKpHckgyeUwKwlSL5gCgIdBOxMoDbAjBwDHyU3muoJg4wMJKnw6aYWiaCMABeG4CrksodUx1AHcBuzeu1SiDLDXUAdYB5K8DvKoGsNNQBdAJYKpnMNtQB1AGyEXc7jSjmHe0rIQYALJVSptY+DQIC6Ljfra8LfBwFO+z+U/MA647dOisfd/PU0DFQCSQA3YlgNbJrQRfBQAB1535tLTkAugopyAGgHcBTuIyl9gwAApB379iXg+6ca15p6L1VZhIAPbcstJxFPKQbuwbOXwNAMCCa3w479of98V+IiQFYvStVDdfx29Cjv9/pP7epwAewd2ts8nnE4TfviLsFv/wAAM6AtUrrf5ud+Nu4q2jdfb3J/ZtPf/+ZCoEU4PGnvv7sBcmfYmJNFcAdulr97sv9l7epEIcPEAlUTRXAow5gMwBxgDkDaJ2tTx8gYwDiACUD6NuzYAAMAGsGIA5Qa7p5iwGwAOQMAP8gFyoAnwEYQMNjHHgALAYgDuBou4mZARgABYCr/Q4OBsAHUFEC8BiAATS81QERgM0AGl7twwCIAObanuhkALwAESWAjAEYAPn+OAOo/Xqp9aFGBsAJEDIAcQCfEsCaAbBvDTGABoCCEEDNANh3RhhAA0DFAHQAch/7xoAOgAUDEAcIGIAOgO73PDEASoCYAYgDJHQALI2vfGYAvAA+A1AHSBmAOEBBBsAx8cpDBsAHUDEAcYAldYAFA1ABcHV+AIcB8AJEDEAcIKYOkDAAFQDPR78oqKUH+NR7AAOkDEAcoCAO8I12DEgQXX8dAJguvwaA8A9BCWDv6XkNX0HBBIDu8gMDxKkgDfBNCMoAuJIfPADOyw8GgDH6QQLgS35QANbdX6gvvwD43J51lwrSANgbAzAAAzAAAzAAAzAAAzAAAzAAAzAAAzAAAzAAAzAAAzAAAzAAAzAAA5BoV7MzBmAA2gAXtAGuGeAVbYBLBjiiDXAyO6YNcD4jXgrOiANcPQKcUQcgXQhcPwKQzoMnjwCk08BjEqAdBZ/On3IUvPoOQDgKXn4HIFwMn3wHOCYeAggHgaufAK9ohwDCY+D8J8CM+AggmwgvfwEcER8BRPPA8wggmgcuNwCOiY8AkmHwevP8KXaBrQ5AMAxudwCCmXCnA5CLArsdgFwU2OsAxLrA5ayhEYqDV03nTykOnjcC0BkEr2cz0gLXs9Z2RjcA/MyFZ7TPn0If6Dn/g48Dr2e97bdDvvznsyHtUAmuXs+Gtjenp4d29qev3zSe6j+qT4i8hFrjSgAAAFd6VFh0UmF3IHByb2ZpbGUgdHlwZSBpcHRjAAB4nOPyDAhxVigoyk/LzEnlUgADIwsuYwsTIxNLkxQDEyBEgDTDZAMjs1Qgy9jUyMTMxBzEB8uASKBKLgDqFxF08kI1lQAAAABJRU5ErkJggg=="


def getFavicon192Png() -> str:
    return "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"


def getFaviconPng() -> str:
    return getFavicon192Png()


def getFavicon180Png() -> str:
    return "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"


def getSafariTabSvg() -> str:
    return "PD94bWwgdmVyc2lvbj0iMS4wIiBzdGFuZGFsb25lPSJubyI/Pgo8IURPQ1RZUEUgc3ZnIFBVQkxJQyAiLS8vVzNDLy9EVEQgU1ZHIDIwMDEwOTA0Ly9FTiIKICJodHRwOi8vd3d3LnczLm9yZy9UUi8yMDAxL1JFQy1TVkctMjAwMTA5MDQvRFREL3N2ZzEwLmR0ZCI+CjxzdmcgdmVyc2lvbj0iMS4wIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiB3aWR0aD0iNTEyLjAwMDAwMHB0IiBoZWlnaHQ9IjUxMi4wMDAwMDBwdCIgdmlld0JveD0iMCAwIDUxMi4wMDAwMDAgNTEyLjAwMDAwMCIKIHByZXNlcnZlQXNwZWN0UmF0aW89InhNaWRZTWlkIG1lZXQiPgo8bWV0YWRhdGE+CkNyZWF0ZWQgYnkgcG90cmFjZSAxLjE0LCB3cml0dGVuIGJ5IFBldGVyIFNlbGluZ2VyIDIwMDEtMjAxNwo8L21ldGFkYXRhPgo8ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgwLjAwMDAwMCw1MTIuMDAwMDAwKSBzY2FsZSgwLjEwMDAwMCwtMC4xMDAwMDApIgpmaWxsPSIjMDAwMDAwIiBzdHJva2U9Im5vbmUiPgo8cGF0aCBkPSJNMzkzIDUxMDYgYy0xODYgLTQ1IC0zNDUgLTIwNyAtMzgyIC0zODggLTggLTM4IC0xMSAtNjc3IC05IC0yMTgzCmwzIC0yMTMwIDIyIC02MCBjNjcgLTE3NSAyMjAgLTMwNiAzOTMgLTMzNSA0NiAtOCA2ODQgLTEwIDIxODAgLTggbDIxMTUgMyA2OAoyNyBjODYgMzUgMTQxIDczIDIwNSAxNDMgNjAgNjYgMTA2IDE1NiAxMjIgMjQwIDggNDQgMTAgNjMzIDggMjE4MCBsLTMgMjEyMAotMjMgNTkgYy02NCAxNjkgLTIxMyAzMDAgLTM4MCAzMzUgLTgyIDE3IC00MjQ4IDE0IC00MzE5IC0zeiBtMTQ3MyAtNzgzIGM1Ci0xNiAtMzAgLTI4MyAtODYgLTY3MyAtMTAxIC02OTQgLTEwOCAtNzc0IC03NiAtOTE1IDQ2IC0yMDAgMTU5IC0zNjkgMjk4Ci00NDIgNDggLTI1IDYzIC0yOCAxNTMgLTI4IDkzIDAgMTA1IDIgMTY2IDMyIDc2IDM4IDE4NyAxNDcgMjU3IDI1MyAxMDEgMTUzCjIxNSA0MTkgMjc0IDYzOCBsMzEgMTE3IDkgNTE1IGM1IDI4MyAxMCA1MTUgMTEgNTE2IDEgMSAxMDIgNSAyMjQgOCBsMjIzIDgKMTEgLTI2IGMxMCAtMjEgLTcgLTEzNCAtMTAxIC02NzEgLTEyMyAtNzA4IC0xMTYgLTY0MSAtODkgLTkyMCAzNiAtMzY4IDEyNQotNTA1IDMyOSAtNTA1IDEwNSAwIDE1NyAyNiAyNDUgMTIzIGw2OSA3NSA0MyAtMjkgNDIgLTI5IC0yOSAtNjkgYy04OSAtMjE3Ci0yMjcgLTM3MyAtMzc2IC00MjcgLTExNSAtNDIgLTI4MiAtNDIgLTM2NCAxIC05OSA1MSAtMTY4IDIxMyAtMjA1IDQ4MSAtMTYKMTE4IC00NCAzNTcgLTQ1IDM4MiAwIDI4IC0zMCAxMCAtMzkgLTI1IC01IC0yMSAtMTkgLTc1IC0zMCAtMTE5IC0zMCAtMTE5Ci04NyAtMjc2IC0xMzMgLTM2OCAtMTM4IC0yNzcgLTMyMyAtNDA1IC01NjcgLTM5NCAtMTI2IDYgLTE3MiAyOCAtMjcxIDEyNwotNTYgNTcgLTkwIDEwMyAtMTM0IDE4NCAtMzIgNTkgLTY1IDEwNyAtNzMgMTA3IC0xMiAwIC0xMyAtMzAgLTggLTE5NyAxMAotMzIzIDIzIC01NTEgNTEgLTg1NiAxNCAtMTU5IDIyIC0yOTIgMTggLTI5NyAtMjAgLTE3IC0zNzEgLTEzMyAtMzk5IC0xMzIKLTcyIDUgLTY4IC0xMyAtNjEgMjUxIDE4IDY0NyA0OSAxMDAxIDEyNiAxNDYzIGwzMCAxNzYgMCA4NDEgMCA4NDAgMTM4IDQgYzc1CjEgMTgxIDQgMjM0IDUgbDk4IDIgNiAtMjd6Ii8+CjwvZz4KPC9zdmc+Cg=="


def getFaviconIco() -> str:
    return "AAABAAEAMDAQAAEABABoBgAAFgAAACgAAAAwAAAAYAAAAAEABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA2NjYAOzs7AERERABFRUUAT09PAGNjYwB8fHwAk5OTAKysrADGxsYA2traAOjo6ADx8fEA+/v7AP///wAAAAAAIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIjMzIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiEBMiIiIiIiIiIiIiIiIiIiIiIiIiIiMWp1EiIiIiIiIiIiIiIiIiIiIiIiIiIiMH7dkyIiIiIiIiIiIiIiIiIiIiIiIiIiMH7esyIiIiIiIiIiIiIiIiIiIiIiIiIiMH7ekTIiIiIiIiIiIiIiIiIiIiIiIiIiMH7ekTIiIiIiIiIiIiIiIiIiIiIiIiIiMG7egDIiIiIiIiIiIiIiIiIiIiIiIiIiMW7egDIiIiIiIiIiIiIiIiIiIiIiIiIiMW7ecDIiIiIiIiIiIiIiIiIiIiIiIiIiMV7ecDMiMyIiIjMzMiIiIiIiIiIiIiIiMV3uYSAiATIiMgEQEyIiIiIiIiIiIiIiMkzuYEiqlRMiI3mYUTIiIiIiIiIiIiIiMjvuYq7u7nEzCO3u1hMiIiIiIiIiIiIiIxruWO3d3eYSTO3e7VEyIiIiIiIiIiIiIxntfd7u7etAbt7bvpEyIiIiIiIiIiIiIwjt3elle+5wjuxSN+YTIiIiIiIiIiIiIwft3oARBL6gnucDIHYTIiIiIiIiIiIiIxXt6hMzMV3lnsQjMxEyIiIiIiIiIiIiIyTO5hMiIwfnrqIiIjMiIiIiIiIiIiIiIyS+xCMiIyO6vpEyIiIiIiIiIiIiIiIiIyS+oiIiIjB+3pAyIiIiIiIiIiIiIiIiIyS+oTIiIjJM7oAyIiIiIiIiIiIiIiIiIyS+oiIiIiMZ7oAyIiIiIiIiIiIiIiIiIyTOxCMiIiMG7pEyIiIiIiIiIiIiIiIiIyTO5RMiIiMV3rMiIiIiIiIiIiIiIiIiIyTO5hMiIiMkvtUTIiIiIiIiIiIiIiIiIyTO5wMiIiMjvuYTIiIiIiIiIiIiIiIiIyTO6AMiIiMjvucDIiIiIiIiIiIiIiIiIyTO6RMiIiIjvugDIiIiIiIiIiIiIiIiIyTO6iIiIiIjvuoTIiIiIiIiIiIiIiIiIyTO7EIyIiIjvutCMiIiIiIiIiIiIiIiIyTO7lEyIiIiru5RMiIiIiIiIiIiIiIiIyTO3mEyIiIirt5hMiIiIiIiIiIiIiIiIyTO3nAyIiIirt6AMiIiIiIiIiIiIiIiIySJmnEyIiIyiZpxMiIiIiIiIiIiIiIiIiIRESIiIiIiERESIiIiIiIiIiIiIiIiIiIzMzIiIiIiMzMyIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiIiAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"


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


def getStyleCss() -> str:
    return "Ym9keSB7CiAgICBmb250LWZhbWlseTogR2FyYW1vbmQsIEJhc2tlcnZpbGxlLCBCYXNrZXJ2aWxsZSBPbGQgRmFjZSwgVGltZXMgTmV3IFJvbWFuLCBzZXJpZjsKfQoKYSB7CiAgICBjb2xvcjogcmdiKDEwMCwgMTAwLCAxMDApOwogICAgdHJhbnNpdGlvbjogMC43NXM7CiAgICB0ZXh0LWRlY29yYXRpb246IHVuZGVybGluZSAjQkJCIGRvdHRlZCAxcHg7Cn0KCmE6YWN0aXZlIHsKICAgIGNvbG9yOiByZ2IoNTAsIDUwLCA1MCk7CiAgICB0cmFuc2l0aW9uOiAwLjFzOwp9CgpociB7CiAgICBjb2xvcjogI0VFRTsKfQoKdGFibGUgewogICAgbWFyZ2luOiAzMHB4Owp9CgouZGF0YSB0ZCB7CiAgICBwYWRkaW5nOiA1cHg7CiAgICBib3JkZXItYm90dG9tOiBkb3R0ZWQgMXB4ICNBQUE7Cn0KCmJvZHkucmF3IGEgewogICAgdGV4dC1kZWNvcmF0aW9uOiBub25lOwp9Cgpib2R5LnJhdyB0YWJsZSB7CiAgICBtYXJnaW46IDMwcHg7Cn0KCmJvZHkucmF3IHRkLCB0aCB7CiAgICBwYWRkaW5nOiAxMHB4IDI1cHg7Cn0KCmJvZHkucmF3IHRoZWFkIHsKICAgIGNvbG9yOiAjRkZGOwogICAgYmFja2dyb3VuZDogIzU1NTsKfQoKYm9keS5yYXcgdGQ6bnRoLWNoaWxkKGV2ZW4pIHsKICAgIHRleHQtYWxpZ246IHJpZ2h0Owp9Cgpib2R5LnJhdyB0cjpudGgtY2hpbGQoZXZlbikgewogICAgYmFja2dyb3VuZDogI0VFRTsKfQoKYm9keS5yYXcgLmluZm8gewogICAgdGV4dC1hbGlnbjogY2VudGVyOwp9CgpzdmcudHVydGxlIHsKICAgIHdpZHRoOiAxMDBweDsKICAgIGhlaWdodDogMTAwcHg7CiAgICBvcGFjaXR5OiAzNSU7CiAgICB0cmFuc2l0aW9uOiAwLjc1czsKfQoKc3ZnLnR1cnRsZTphY3RpdmUgewogICAgb3BhY2l0eTogNzAlOwogICAgdHJhbnNpdGlvbjogMC4xczsKfQoKLnJvdC0xODAgewogICAgdHJhbnNmb3JtOiByb3RhdGUoLTE4MGRlZyk7Cn0KCi5yb3QtMTM1IHsKICAgIHRyYW5zZm9ybTogcm90YXRlKC0xMzVkZWcpOwp9Cgoucm90LTkwIHsKICAgIHRyYW5zZm9ybTogcm90YXRlKC05MGRlZyk7Cn0KCi5yb3QtNDUgewogICAgdHJhbnNmb3JtOiByb3RhdGUoLTQ1ZGVnKTsKfQoKLnJvdDQ1IHsKICAgIHRyYW5zZm9ybTogcm90YXRlKDQ1ZGVnKTsKfQoKLnJvdDkwIHsKICAgIHRyYW5zZm9ybTogcm90YXRlKDkwZGVnKTsKfQoKLnJvdDEzNSB7CiAgICB0cmFuc2Zvcm06IHJvdGF0ZSgxMzVkZWcpOwp9Cgoucm90MTgwIHsKICAgIHRyYW5zZm9ybTogcm90YXRlKDE4MGRlZyk7Cn0KCi5kcml2ZSB7CiAgICBoZWlnaHQ6IDQwMHB4Owp9Cgouc2ltcGxlIHsKICAgIGhlaWdodDogOTAwcHg7Cn0KCi5wcm8gewogICAgaGVpZ2h0OiAxMDAwcHg7Cn0KCi5wYW5lbCB7CiAgICB3aWR0aDogNjAwcHg7CiAgICBtYXJnaW46IGF1dG87CiAgICB0ZXh0LWFsaWduOiBjZW50ZXI7Cn0KCi5saW5rcyB7CiAgICB3aWR0aDogMzUwcHg7CiAgICBwYWRkaW5nOiAwOwogICAgbWFyZ2luOiAxMDBweCBhdXRvOwogICAgYm9yZGVyLXRvcDogMDsKICAgIGJvcmRlcjogMXB4IHNvbGlkICNCQkI7CiAgICBib3JkZXItcmFkaXVzOiAxNXB4IDE1cHggMCAwOwogICAgZm9udC1zaXplOiAyMHB4OwogICAgY29sb3I6ICM4ODg7Cn0KCi5saW5rcyBsaSB7CiAgICBsaXN0LXN0eWxlOiBub25lOwogICAgYmFja2dyb3VuZDogI0VFRTsKICAgIHBhZGRpbmc6IDEwcHggMjBweDsKICAgIGJvcmRlci10b3A6IDFweCBzb2xpZCAjQ0NDOwp9CgoubGlua3MgbGk6Zmlyc3QtY2hpbGQgewogICAgY29sb3I6ICNGRkY7CiAgICBiYWNrZ3JvdW5kOiAjNTU1OwogICAgYm9yZGVyOiBub25lOwogICAgYm9yZGVyLXJhZGl1czogMTBweCAxMHB4IDAgMDsKfQo="


def getLicenseHtml() -> str:
    return "PCFET0NUWVBFIGh0bWw+CjxodG1sPgogICAgPGhlYWQ+CiAgICAgICAgPG1ldGEgbmFtZT0ndmlld3BvcnQnIGNvbnRlbnQ9J3dpZHRoPTYxMCc+CiAgICAgICAgPG1ldGEgY2hhcnNldD0ndXRmLTgnPgogICAgICAgIDxtZXRhIG5hbWU9J2F1dGhvcicgY29udGVudD0nU3phYsOzIEzDoXN6bMOzIEFuZHLDoXMgLy8gaHUtenphJz4KICAgICAgICA8bGluayByZWw9J2F1dGhvcicgaHJlZj0naHR0cHM6Ly96emEuaHUnPgogICAgICAgIDxsaW5rIHJlbD0nbGljZW5zZScgaHJlZj0nL2xpY2Vuc2UuaHRtbCc+CiAgICAgICAgPGxpbmsgcmVsPSdoZWxwJyBocmVmPSdodHRwczovL3Vib3QuaHUnPgogICAgICAgIDxsaW5rIHJlbD0naWNvbicgdHlwZT0naW1hZ2UvcG5nJyBocmVmPScvYW5kcm9pZC1jaHJvbWUtNTEyeDUxMi5wbmcnIHNpemVzPSc1MTJ4NTEyJz4KICAgICAgICA8bGluayByZWw9J2ljb24nIHR5cGU9J2ltYWdlL3BuZycgaHJlZj0nL2FuZHJvaWQtY2hyb21lLTE5MngxOTIucG5nJyBzaXplcz0nMTkyeDE5Mic+CiAgICAgICAgPGxpbmsgcmVsPSdpY29uJyB0eXBlPSdpbWFnZS9wbmcnIGhyZWY9Jy9mYXZpY29uLnBuZycgc2l6ZXM9JzE5MngxOTInPgogICAgICAgIDxsaW5rIHJlbD0naWNvbicgdHlwZT0naW1hZ2UvcG5nJyBocmVmPScvZmF2aWNvbi0zMngzMi5wbmcnIHNpemVzPSczMngzMic+CiAgICAgICAgPGxpbmsgcmVsPSdpY29uJyB0eXBlPSdpbWFnZS9wbmcnIGhyZWY9Jy9mYXZpY29uLTE2eDE2LnBuZycgc2l6ZXM9JzE2eDE2Jz4KICAgICAgICA8bGluayByZWw9J2ljb24nIHR5cGU9J2ltYWdlL3gtaWNvbicgaHJlZj0nL2Zhdmljb24uaWNvJz4KICAgICAgICA8bGluayByZWw9J21hbmlmZXN0JyBocmVmPScvc2l0ZS53ZWJtYW5pZmVzdCc+CiAgICAgICAgPGxpbmsgcmVsPSdzdHlsZXNoZWV0JyBocmVmPScvc3R5bGUuY3NzJz4KICAgICAgICA8dGl0bGU+zrxCb3QgTUlUIExpY2Vuc2U8L3RpdGxlPgogICAgPC9oZWFkPgogICAgPGJvZHk+CiAgICAgICAgPGgxPgogICAgICAgICAgICBUaGUgbGljZW5zZSBvZiB0aGUgzrxCb3QgZmlybXdhcmUKICAgICAgICA8L2gxPgogICAgICAgIFRoaXMgZmlsZSBpcyBwYXJ0IG9mIHVCb3RfZmlybXdhcmUuPGJyPgogICAgICAgIDxhIGhyZWY9J2h0dHBzOi8venphLmh1L3VCb3RfZmlybXdhcmUnIHRhcmdldD0nX2JsYW5rJz5odHRwczovL3p6YS5odS91Qm90X2Zpcm13YXJlPC9hPjxicj4KICAgICAgICA8YSBocmVmPSdodHRwczovL2dpdC56emEuaHUvdUJvdF9maXJtd2FyZScgdGFyZ2V0PSdfYmxhbmsnPmh0dHBzOi8vZ2l0Lnp6YS5odS91Qm90X2Zpcm13YXJlPC9hPjxicj48YnI+PGJyPgogICAgICAgIDxoMj4KICAgICAgICAgICAgTUlUIExpY2Vuc2UKICAgICAgICA8L2gyPgogICAgICAgIENvcHlyaWdodCAoYykgMjAyMC0yMDIxIFN6YWLDsyBMw6FzemzDsyBBbmRyw6FzIC8vIGh1LXp6YTxicj48YnI+CiAgICAgICAgUGVybWlzc2lvbiBpcyBoZXJlYnkgZ3JhbnRlZCwgZnJlZSBvZiBjaGFyZ2UsIHRvIGFueSBwZXJzb24gb2J0YWluaW5nIGEgY29weTxicj4KICAgICAgICBvZiB0aGlzIHNvZnR3YXJlIGFuZCBhc3NvY2lhdGVkIGRvY3VtZW50YXRpb24gZmlsZXMgKHRoZSAiU29mdHdhcmUiKSwgdG8gZGVhbDxicj4KICAgICAgICBpbiB0aGUgU29mdHdhcmUgd2l0aG91dCByZXN0cmljdGlvbiwgaW5jbHVkaW5nIHdpdGhvdXQgbGltaXRhdGlvbiB0aGUgcmlnaHRzPGJyPgogICAgICAgIHRvIHVzZSwgY29weSwgbW9kaWZ5LCBtZXJnZSwgcHVibGlzaCwgZGlzdHJpYnV0ZSwgc3VibGljZW5zZSwgYW5kL29yIHNlbGw8YnI+CiAgICAgICAgY29waWVzIG9mIHRoZSBTb2Z0d2FyZSwgYW5kIHRvIHBlcm1pdCBwZXJzb25zIHRvIHdob20gdGhlIFNvZnR3YXJlIGlzPGJyPgogICAgICAgIGZ1cm5pc2hlZCB0byBkbyBzbywgc3ViamVjdCB0byB0aGUgZm9sbG93aW5nIGNvbmRpdGlvbnM6PGJyPjxicj4KICAgICAgICBUaGUgYWJvdmUgY29weXJpZ2h0IG5vdGljZSBhbmQgdGhpcyBwZXJtaXNzaW9uIG5vdGljZSBzaGFsbCBiZSBpbmNsdWRlZCBpbiBhbGw8YnI+CiAgICAgICAgY29waWVzIG9yIHN1YnN0YW50aWFsIHBvcnRpb25zIG9mIHRoZSBTb2Z0d2FyZS48YnI+PGJyPgogICAgICAgIFRIRSBTT0ZUV0FSRSBJUyBQUk9WSURFRCAiQVMgSVMiLCBXSVRIT1VUIFdBUlJBTlRZIE9GIEFOWSBLSU5ELCBFWFBSRVNTIE9SPGJyPgogICAgICAgIElNUExJRUQsIElOQ0xVRElORyBCVVQgTk9UIExJTUlURUQgVE8gVEhFIFdBUlJBTlRJRVMgT0YgTUVSQ0hBTlRBQklMSVRZLDxicj4KICAgICAgICBGSVRORVNTIEZPUiBBIFBBUlRJQ1VMQVIgUFVSUE9TRSBBTkQgTk9OSU5GUklOR0VNRU5ULiBJTiBOTyBFVkVOVCBTSEFMTCBUSEU8YnI+CiAgICAgICAgQVVUSE9SUyBPUiBDT1BZUklHSFQgSE9MREVSUyBCRSBMSUFCTEUgRk9SIEFOWSBDTEFJTSwgREFNQUdFUyBPUiBPVEhFUjxicj4KICAgICAgICBMSUFCSUxJVFksIFdIRVRIRVIgSU4gQU4gQUNUSU9OIE9GIENPTlRSQUNULCBUT1JUIE9SIE9USEVSV0lTRSwgQVJJU0lORyBGUk9NLDxicj4KICAgICAgICBPVVQgT0YgT1IgSU4gQ09OTkVDVElPTiBXSVRIIFRIRSBTT0ZUV0FSRSBPUiBUSEUgVVNFIE9SIE9USEVSIERFQUxJTkdTIElOIFRIRTxicj4KICAgICAgICBTT0ZUV0FSRS48YnI+CiAgICA8L2JvZHk+CjwvaHRtbD4K"


def getPanelDatetime() -> str:
    return "ICAgICAgICA8dGl0bGU+zrxCb3QgU2V0dGluZ3MgLSBEYXRlICYgVGltZTwvdGl0bGU+CiAgICA8L2hlYWQ+CiAgICA8Ym9keT4KICAgICAgICA8dWwgY2xhc3M9ImxpbmtzIj4KICAgICAgICAgICAgPGxpPkRhdGUgJiBUaW1lPC9saT4KPCEtLQojIU1pY3JvUHl0aG9uCmR0ID0gY29uZmlnLmRhdGV0aW1lKCkKcmV0dXJuICIgICAgICAgICAgICA8bGk+PHRhYmxlIGNsYXNzPVwiaW5saW5lXCI+PHRyPjx0ZD57fS4gezowMmR9LiB7OjAyZH0uPC90ZD48dGQ+ezowMmR9IDogezowMmR9IDogezowMmR9PC90ZD48L3RyPjwvdGFibGU+PC9saT4iLmZvcm1hdChkdFswXSwgZHRbMV0sIGR0WzJdLCBkdFs0XSwgZHRbNV0sIGR0WzZdKQotLT4KICAgICAgICAgICAgPGxpPjxjZW50ZXI+PGlucHV0IHR5cGU9ImRhdGUiIGlkPSJkYXRlIj4mbmJzcDsmbmJzcDsmbmJzcDsmbmJzcDsmbmJzcDsmbmJzcDs8aW5wdXQgdHlwZT0idGltZSIgaWQ9InRpbWUiPjwvY2VudGVyPjwvbGk+CiAgICAgICAgICAgIDxsaT48YSBocmVmPSJfZGF0ZXRpbWUiIG9uY2xpY2s9InNlbmQoMSkiPlNhdmU8L2E+PC9saT4KICAgICAgICAgICAgPGxpPjxhIGhyZWY9Il9zZXR0aW5ncyI+QmFjayB0byBzZXR0aW5nczwvYT48L2xpPgogICAgICAgIDwvdWw+CgogICAgICAgIDxzY3JpcHQ+CiAgICAgICAgICAgIGZ1bmN0aW9uIHNlbmQodmFsdWUpIHt7CiAgICAgICAgICAgICAgICBsZXQgeGhyID0gbmV3IFhNTEh0dHBSZXF1ZXN0KCk7CiAgICAgICAgICAgICAgICB4aHIub3BlbigiR0VUIiwgIi9jb21tYW5kL1RJTUVfIiArIGRvY3VtZW50LmdldEVsZW1lbnRCeUlkKCJkYXRlIikudmFsdWUgKyAiXyIgKyBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCgidGltZSIpLnZhbHVlLnJlcGxhY2UoIjoiLCAiLSIpKTsKICAgICAgICAgICAgICAgIHhoci5zZXRSZXF1ZXN0SGVhZGVyKCJDb250ZW50LVR5cGUiLCAiYXBwbGljYXRpb24vanNvbiIpOwogICAgICAgICAgICAgICAgeGhyLnNlbmQoKTsKICAgICAgICAgICAgfX0KICAgICAgICA8L3NjcmlwdD4KICAgIDwvYm9keT4KPC9odG1sPgo="


def getPanelDrive() -> str:
    return "ICAgICAgICA8dGl0bGU+zrxCb3QgRHJpdmU8L3RpdGxlPgogICAgPC9oZWFkPgogICAgPGJvZHk+CiAgICAgICAgPHRhYmxlIGNsYXNzPSJkcml2ZSBwYW5lbCI+CiAgICAgICAgICAgIDx0cj4KICAgICAgICAgICAgICAgIDx0ZD48c3ZnIG9uY2xpY2s9InNlbmQoJ0snKSIgY2xhc3M9InR1cnRsZSBhcnJvdyByb3QtNDUiPjx1c2UgeGxpbms6aHJlZj0idHVydGxlLnN2ZyNhcnJvdyI+PC91c2U+PC9zdmc+PC90ZD4KICAgICAgICAgICAgICAgIDx0ZD48c3ZnIG9uY2xpY2s9InNlbmQoJ0YnKSIgY2xhc3M9InR1cnRsZSBhcnJvdyI+PHVzZSB4bGluazpocmVmPSJ0dXJ0bGUuc3ZnI2Fycm93Ij48L3VzZT48L3N2Zz48L3RkPgogICAgICAgICAgICAgICAgPHRkPjxzdmcgb25jbGljaz0ic2VuZCgnUScpIiBjbGFzcz0idHVydGxlIGFycm93IHJvdDQ1Ij48dXNlIHhsaW5rOmhyZWY9InR1cnRsZS5zdmcjYXJyb3ciPjwvdXNlPjwvc3ZnPjwvdGQ+CiAgICAgICAgICAgIDwvdHI+CiAgICAgICAgICAgIDx0cj4KICAgICAgICAgICAgICAgIDx0ZD48c3ZnIG9uY2xpY2s9InNlbmQoJ0wnKSIgY2xhc3M9InR1cnRsZSBhcnJvdyByb3QtOTAiPjx1c2UgeGxpbms6aHJlZj0idHVydGxlLnN2ZyNhcnJvdyI+PC91c2U+PC9zdmc+PC90ZD4KICAgICAgICAgICAgICAgIDx0ZD48c3ZnIG9uY2xpY2s9InNlbmQoJ0InKSIgY2xhc3M9InR1cnRsZSBhcnJvdyByb3QxODAiPjx1c2UgeGxpbms6aHJlZj0idHVydGxlLnN2ZyNhcnJvdyI+PC91c2U+PC9zdmc+PC90ZD4KICAgICAgICAgICAgICAgIDx0ZD48c3ZnIG9uY2xpY2s9InNlbmQoJ1InKSIgY2xhc3M9InR1cnRsZSBhcnJvdyByb3Q5MCI+PHVzZSB4bGluazpocmVmPSJ0dXJ0bGUuc3ZnI2Fycm93Ij48L3VzZT48L3N2Zz48L3RkPgogICAgICAgICAgICA8L3RyPgogICAgICAgIDwvdGFibGU+CgogICAgICAgIDxzY3JpcHQ+CiAgICAgICAgICAgIGZ1bmN0aW9uIHNlbmQodmFsdWUpIHt7CiAgICAgICAgICAgICAgICBsZXQgeGhyID0gbmV3IFhNTEh0dHBSZXF1ZXN0KCk7CiAgICAgICAgICAgICAgICB4aHIub3BlbigiR0VUIiwgIi9jb21tYW5kL0RSSVZFXyIgKyB2YWx1ZSk7CiAgICAgICAgICAgICAgICB4aHIuc2V0UmVxdWVzdEhlYWRlcigiQ29udGVudC1UeXBlIiwgImFwcGxpY2F0aW9uL2pzb24iKTsKICAgICAgICAgICAgICAgIHhoci5zZW5kKCk7CiAgICAgICAgICAgIH19CiAgICAgICAgPC9zY3JpcHQ+CiAgICA8L2JvZHk+CjwvaHRtbD4K"


def getPanelGo() -> str:
    return "ICAgICAgICA8dGl0bGU+zrxCb3QgR288L3RpdGxlPgogICAgPC9oZWFkPgogICAgPGJvZHk+CiAgICAgICAgPHRhYmxlIGNsYXNzPSdzaW1wbGUgcGFuZWwnPgogICAgICAgICAgICA8dHI+CiAgICAgICAgICAgICAgICA8dGQ+PC90ZD4KICAgICAgICAgICAgICAgIDx0ZD48c3ZnIG9uY2xpY2s9J3NlbmQoMSknIGNsYXNzPSd0dXJ0bGUgYXJyb3cnPjx1c2UgeGxpbms6aHJlZj0ndHVydGxlLnN2ZyNhcnJvdyc+PC91c2U+PC9zdmc+PC90ZD4KICAgICAgICAgICAgICAgIDx0ZD48L3RkPgogICAgICAgICAgICA8L3RyPgogICAgICAgICAgICA8dHI+CiAgICAgICAgICAgICAgICA8dGQ+PHN2ZyBvbmNsaWNrPSdzZW5kKDEyOCknIGNsYXNzPSd0dXJ0bGUgYXJyb3cgcm90LTkwJz48dXNlIHhsaW5rOmhyZWY9J3R1cnRsZS5zdmcjYXJyb3cnPjwvdXNlPjwvc3ZnPjwvdGQ+CiAgICAgICAgICAgICAgICA8dGQ+PHN2ZyBvbmNsaWNrPSdzZW5kKDY0KScgY2xhc3M9J3R1cnRsZSBwbGF5Jz48dXNlIHhsaW5rOmhyZWY9J3R1cnRsZS5zdmcjcGxheSc+PC91c2U+PC9zdmc+PC90ZD4KICAgICAgICAgICAgICAgIDx0ZD48c3ZnIG9uY2xpY2s9J3NlbmQoMTYpJyBjbGFzcz0ndHVydGxlIGFycm93IHJvdDkwJz48dXNlIHhsaW5rOmhyZWY9J3R1cnRsZS5zdmcjYXJyb3cnPjwvdXNlPjwvc3ZnPjwvdGQ+CiAgICAgICAgICAgIDwvdHI+CiAgICAgICAgICAgIDx0cj4KICAgICAgICAgICAgICAgIDx0ZD48L3RkPgogICAgICAgICAgICAgICAgPHRkPjxzdmcgb25jbGljaz0nc2VuZCgzMiknIGNsYXNzPSd0dXJ0bGUgYXJyb3cgcm90MTgwJz48dXNlIHhsaW5rOmhyZWY9J3R1cnRsZS5zdmcjYXJyb3cnPjwvdXNlPjwvc3ZnPjwvdGQ+CiAgICAgICAgICAgICAgICA8dGQ+PC90ZD4KICAgICAgICAgICAgPC90cj4KICAgICAgICAgICAgPHRyPgogICAgICAgICAgICAgICAgPHRkIGNvbHNwYW49JzMnIHN0eWxlPSdoZWlnaHQ6MTAwcHg7Jz48L3RkPgogICAgICAgICAgICA8L3RyPgogICAgICAgICAgICA8dHI+CiAgICAgICAgICAgICAgICA8dGQ+PHN2ZyBvbmNsaWNrPSdzZW5kKDUxMiknIGNsYXNzPSd0dXJ0bGUgY3Jvc3MnPjx1c2UgeGxpbms6aHJlZj0ndHVydGxlLnN2ZyNjcm9zcyc+PC91c2U+PC9zdmc+PC90ZD4KICAgICAgICAgICAgICAgIDx0ZD48c3ZnIG9uY2xpY2s9J3NlbmQoMiknIGNsYXNzPSd0dXJ0bGUgcGF1c2UnPjx1c2UgeGxpbms6aHJlZj0ndHVydGxlLnN2ZyNwYXVzZSc+PC91c2U+PC9zdmc+PC90ZD4KICAgICAgICAgICAgICAgIDx0ZD48c3ZnIG9uY2xpY2s9J3NlbmQoMjU2KScgY2xhc3M9J3R1cnRsZSB1bmRvJz48dXNlIHhsaW5rOmhyZWY9J3R1cnRsZS5zdmcjdW5kbyc+PC91c2U+PC9zdmc+PC90ZD4KICAgICAgICAgICAgPC90cj4KICAgICAgICA8L3RhYmxlPgoKICAgICAgICA8c2NyaXB0PgogICAgICAgICAgICBmdW5jdGlvbiBzZW5kKHZhbHVlKSB7ewogICAgICAgICAgICAgICAgbGV0IHhociA9IG5ldyBYTUxIdHRwUmVxdWVzdCgpOwogICAgICAgICAgICAgICAgeGhyLm9wZW4oIkdFVCIsICIvY29tbWFuZC9QUkVTU18iICsgdmFsdWUpOwogICAgICAgICAgICAgICAgeGhyLnNldFJlcXVlc3RIZWFkZXIoIkNvbnRlbnQtVHlwZSIsICJhcHBsaWNhdGlvbi9qc29uIik7CiAgICAgICAgICAgICAgICB4aHIuc2VuZCgpOwogICAgICAgICAgICB9fQogICAgICAgIDwvc2NyaXB0PgogICAgPC9ib2R5Pgo8L2h0bWw+Cg=="


def getPanelHead() -> str:
    return "PCFET0NUWVBFIGh0bWw+CjxodG1sPgogICAgPGhlYWQ+CiAgICAgICAgPG1ldGEgbmFtZT0ndmlld3BvcnQnIGNvbnRlbnQ9J3dpZHRoPTYxMCc+CiAgICAgICAgPG1ldGEgY2hhcnNldD0ndXRmLTgnPgogICAgICAgIDxtZXRhIG5hbWU9J2F1dGhvcicgY29udGVudD0nU3phYsOzIEzDoXN6bMOzIEFuZHLDoXMgLy8gaHUtenphJz4KICAgICAgICA8bGluayByZWw9J2F1dGhvcicgaHJlZj0naHR0cHM6Ly96emEuaHUnPgogICAgICAgIDxsaW5rIHJlbD0nbGljZW5zZScgaHJlZj0nL2xpY2Vuc2UuaHRtbCc+CiAgICAgICAgPGxpbmsgcmVsPSdoZWxwJyBocmVmPSdodHRwczovL3Vib3QuaHUnPgogICAgICAgIDxsaW5rIHJlbD0naWNvbicgdHlwZT0naW1hZ2UvcG5nJyBocmVmPScvYW5kcm9pZC1jaHJvbWUtNTEyeDUxMi5wbmcnIHNpemVzPSc1MTJ4NTEyJz4KICAgICAgICA8bGluayByZWw9J2ljb24nIHR5cGU9J2ltYWdlL3BuZycgaHJlZj0nL2FuZHJvaWQtY2hyb21lLTE5MngxOTIucG5nJyBzaXplcz0nMTkyeDE5Mic+CiAgICAgICAgPGxpbmsgcmVsPSdpY29uJyB0eXBlPSdpbWFnZS9wbmcnIGhyZWY9Jy9mYXZpY29uLnBuZycgc2l6ZXM9JzE5MngxOTInPgogICAgICAgIDxsaW5rIHJlbD0naWNvbicgdHlwZT0naW1hZ2UvcG5nJyBocmVmPScvZmF2aWNvbi0zMngzMi5wbmcnIHNpemVzPSczMngzMic+CiAgICAgICAgPGxpbmsgcmVsPSdpY29uJyB0eXBlPSdpbWFnZS9wbmcnIGhyZWY9Jy9mYXZpY29uLTE2eDE2LnBuZycgc2l6ZXM9JzE2eDE2Jz4KICAgICAgICA8bGluayByZWw9J2ljb24nIHR5cGU9J2ltYWdlL3gtaWNvbicgaHJlZj0nL2Zhdmljb24uaWNvJz4KICAgICAgICA8bGluayByZWw9J21hbmlmZXN0JyBocmVmPScvc2l0ZS53ZWJtYW5pZmVzdCc+CiAgICAgICAgPGxpbmsgcmVsPSdzdHlsZXNoZWV0JyBocmVmPScvc3R5bGUuY3NzJz4K"


def getPanelPro() -> str:
    return "ICAgICAgICA8dGl0bGU+zrxCb3QgUHJvZmVzc2lvbmFsPC90aXRsZT4KICAgIDwvaGVhZD4KICAgIDxib2R5PgogICAgICAgIDx0YWJsZSBjbGFzcz0icHJvIHBhbmVsIj4KICAgICAgICAgICAgPHRyPgogICAgICAgICAgICAgICAgPHRkPjxzdmcgb25jbGljaz0ic2VuZCgxMjgpIiBjbGFzcz0idHVydGxlIGFycm93IHJvdC00NSI+PHVzZSB4bGluazpocmVmPSJ0dXJ0bGUuc3ZnI2Fycm93Ij48L3VzZT48L3N2Zz48L3RkPgogICAgICAgICAgICAgICAgPHRkPjxzdmcgb25jbGljaz0ic2VuZCgxKSIgY2xhc3M9InR1cnRsZSBhcnJvdyI+PHVzZSB4bGluazpocmVmPSJ0dXJ0bGUuc3ZnI2Fycm93Ij48L3VzZT48L3N2Zz48L3RkPgogICAgICAgICAgICAgICAgPHRkPjxzdmcgb25jbGljaz0ic2VuZCgxNikiIGNsYXNzPSJ0dXJ0bGUgYXJyb3cgcm90NDUiPjx1c2UgeGxpbms6aHJlZj0idHVydGxlLnN2ZyNhcnJvdyI+PC91c2U+PC9zdmc+PC90ZD4KICAgICAgICAgICAgPC90cj4KICAgICAgICAgICAgPHRyPgogICAgICAgICAgICAgICAgPHRkPjxzdmcgb25jbGljaz0ic2VuZCgxMjgpIiBjbGFzcz0idHVydGxlIGFycm93IHJvdC05MCI+PHVzZSB4bGluazpocmVmPSJ0dXJ0bGUuc3ZnI2Fycm93Ij48L3VzZT48L3N2Zz48L3RkPgogICAgICAgICAgICAgICAgPHRkPjxzdmcgb25jbGljaz0ic2VuZCg2NCkiIGNsYXNzPSJ0dXJ0bGUgcGxheSI+PHVzZSB4bGluazpocmVmPSJ0dXJ0bGUuc3ZnI3BsYXkiPjwvdXNlPjwvc3ZnPjwvdGQ+CiAgICAgICAgICAgICAgICA8dGQ+PHN2ZyBvbmNsaWNrPSJzZW5kKDE2KSIgY2xhc3M9InR1cnRsZSBhcnJvdyByb3Q5MCI+PHVzZSB4bGluazpocmVmPSJ0dXJ0bGUuc3ZnI2Fycm93Ij48L3VzZT48L3N2Zz48L3RkPgogICAgICAgICAgICA8L3RyPgogICAgICAgICAgICA8dHI+CiAgICAgICAgICAgICAgICA8dGQ+PHN2ZyBvbmNsaWNrPSJzZW5kKDIpIiBjbGFzcz0idHVydGxlIHBhdXNlIj48dXNlIHhsaW5rOmhyZWY9InR1cnRsZS5zdmcjcGF1c2UiPjwvdXNlPjwvc3ZnPjwvdGQ+CiAgICAgICAgICAgICAgICA8dGQ+PHN2ZyBvbmNsaWNrPSJzZW5kKDMyKSIgY2xhc3M9InR1cnRsZSBhcnJvdyByb3QxODAiPjx1c2UgeGxpbms6aHJlZj0idHVydGxlLnN2ZyNhcnJvdyI+PC91c2U+PC9zdmc+PC90ZD4KICAgICAgICAgICAgICAgIDx0ZD48c3ZnIG9uY2xpY2s9InNlbmQoNCkiIGNsYXNzPSJ0dXJ0bGUgcmVwZWF0Ij48dXNlIHhsaW5rOmhyZWY9InR1cnRsZS5zdmcjcmVwZWF0Ij48L3VzZT48L3N2Zz48L3RkPgogICAgICAgICAgICA8L3RyPgogICAgICAgICAgICA8dHI+CiAgICAgICAgICAgICAgICA8dGQ+PHN2ZyBvbmNsaWNrPSJzZW5kKDUxMikiIGNsYXNzPSJ0dXJ0bGUgY3Jvc3MiPjx1c2UgeGxpbms6aHJlZj0idHVydGxlLnN2ZyNjcm9zcyI+PC91c2U+PC9zdmc+PC90ZD4KICAgICAgICAgICAgICAgIDx0ZD48c3ZnIG9uY2xpY2s9InNlbmQoMjU2KSIgY2xhc3M9InR1cnRsZSB1bmRvIj48dXNlIHhsaW5rOmhyZWY9InR1cnRsZS5zdmcjdW5kbyI+PC91c2U+PC9zdmc+PC90ZD4KICAgICAgICAgICAgICAgIDx0ZD48c3ZnIG9uY2xpY2s9InNlbmQoOCkiIGNsYXNzPSJ0dXJ0bGUgY3Jvc3Mgcm90NDUiPjx1c2UgeGxpbms6aHJlZj0idHVydGxlLnN2ZyNjcm9zcyI+PC91c2U+PC9zdmc+PC90ZD4KICAgICAgICAgICAgPC90cj4KICAgICAgICAgICAgPHRyPgogICAgICAgICAgICAgICAgPHRkPjxzdmcgb25jbGljaz0ic2VuZCg2KSIgY2xhc3M9InR1cnRsZSBmMSI+PHVzZSB4bGluazpocmVmPSJ0dXJ0bGUuc3ZnI0YxIj48L3VzZT48L3N2Zz48L3RkPgogICAgICAgICAgICAgICAgPHRkPjxzdmcgb25jbGljaz0ic2VuZCgxMCkiIGNsYXNzPSJ0dXJ0bGUgZjIiPjx1c2UgeGxpbms6aHJlZj0idHVydGxlLnN2ZyNGMiI+PC91c2U+PC9zdmc+PC90ZD4KICAgICAgICAgICAgICAgIDx0ZD48c3ZnIG9uY2xpY2s9InNlbmQoMTIpIiBjbGFzcz0idHVydGxlIGYzIj48dXNlIHhsaW5rOmhyZWY9InR1cnRsZS5zdmcjRjMiPjwvdXNlPjwvc3ZnPjwvdGQ+CiAgICAgICAgICAgIDwvdHI+CiAgICAgICAgPC90YWJsZT4KCiAgICAgICAgPHNjcmlwdD4KICAgICAgICAgICAgZnVuY3Rpb24gc2VuZCh2YWx1ZSkge3sKICAgICAgICAgICAgICAgIGxldCB4aHIgPSBuZXcgWE1MSHR0cFJlcXVlc3QoKTsKICAgICAgICAgICAgICAgIHhoci5vcGVuKCJHRVQiLCAiL2NvbW1hbmQvUFJFU1NfIiArIHZhbHVlKTsKICAgICAgICAgICAgICAgIHhoci5zZXRSZXF1ZXN0SGVhZGVyKCJDb250ZW50LVR5cGUiLCAiYXBwbGljYXRpb24vanNvbiIpOwogICAgICAgICAgICAgICAgeGhyLnNlbmQoKTsKICAgICAgICAgICAgfX0KICAgICAgICA8L3NjcmlwdD4KICAgIDwvYm9keT4KPC9odG1sPgo="


def getPanelSettings() -> str:
    return "ICAgICAgICA8dGl0bGU+zrxCb3QgU2V0dGluZ3M8L3RpdGxlPgogICAgPC9oZWFkPgogICAgPGJvZHk+CiAgICAgICAgPHVsIGNsYXNzPSJsaW5rcyI+CiAgICAgICAgICAgIDxsaT5TZXR0aW5nczwvbGk+CiAgICAgICAgICAgIDxsaT48YSBocmVmPSJfZGF0ZXRpbWUiPkRhdGUgJiBUaW1lPC9hPjwvbGk+CiAgICAgICAgICAgIDxsaT48YSBocmVmPSIiPjwvYT48L2xpPgogICAgICAgICAgICA8bGk+PGEgaHJlZj0iIj48L2E+PC9saT4KICAgICAgICA8L3VsPgogICAgPC9ib2R5Pgo8L2h0bWw+Cg=="


files = {
    "turtle.svg":                 (getTurtleSvg,        ("image/svg+xml; charset=UTF-8",), "getTurtleSvg"),

    "android-chrome-512x512.png": (getFavicon512Png,    ("image/png; charset=UTF-8",), "getFavicon512Png"),
    "android-chrome-192x192.png": (getFavicon192Png,    ("image/png; charset=UTF-8",), "getFavicon192Png"),
    "favicon.png":                (getFaviconPng,       ("image/png; charset=UTF-8",), "getFaviconPng"),
    "apple-touch-icon.png":       (getFavicon180Png,    ("image/png; charset=UTF-8",), "getFavicon180Png"),
    "safari-pinned-tab.svg":      (getSafariTabSvg,     ("image/svg+xml; charset=UTF-8",), "getSafariTabSvg"),
    "favicon.ico":                (getFaviconIco,       ("image/vnd.microsoft.icon; charset=UTF-8",), "getFaviconIco"),
    "mstile-150x150.png":         (getMsTilePng,        ("image/png; charset=UTF-8",), "getMsTilePng"),
    "favicon-32x32.png":          (getFavicon32Png,     ("image/png; charset=UTF-8",), "getFavicon32Png"),
    "favicon-16x16.png":          (getFavicon16Png,     ("image/png; charset=UTF-8",), "getFavicon16Png"),

    "site.webmanifest":           (getSiteWebmanifest,  ("application/manifest+json; charset=UTF-8",), "getSiteWebmanifest"),
    "browserconfig.xml":          (getBrowserconfigXml, ("application/xml; charset=UTF-8",), "getBrowserconfigXml"),
    "style.css":                  (getStyleCss,         ("text/css; charset=UTF-8",), "getStyleCss"),
    "license.html":               (getLicenseHtml,      ("text/html; charset=UTF-8",), "getLicenseHtml"),

    "_panel__datetime.html":      (getPanelDatetime,    ("text/html; charset=UTF-8",), "getPanelDatetime"),
    "_panel_drive.html":          (getPanelDrive,       ("text/html; charset=UTF-8",), "getPanelDrive"),
    "_panel_go.html":             (getPanelGo,          ("text/html; charset=UTF-8",), "getPanelGo"),
    "_panel___head.html":         (getPanelHead,        ("text/html; charset=UTF-8",), "getPanelHead"),
    "_panel_pro.html":            (getPanelPro,         ("text/html; charset=UTF-8",), "getPanelPro"),
    "_panel_settings.html":       (getPanelSettings,    ("text/html; charset=UTF-8",), "getPanelSettings")
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

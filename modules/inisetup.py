import flashbdev, network, ubinascii, ujson, uos

firmware = (0, 1, 193)
initDatetime = (2021, 7, 21, 0, 2, 0, 0, 0)

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
    "period"        : 250,
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

def getFaviconPng() -> str:
    return "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"


def getFaviconIco() -> str:
    return getFaviconPng()


def getLicenseHtml() -> str:
    return "PCFET0NUWVBFIGh0bWw+CjxodG1sPgogICAgPGhlYWQ+CiAgICAgICAgPG1ldGEgbmFtZT0ndmlld3BvcnQnIGNvbnRlbnQ9J3dpZHRoPTYxMCc+CiAgICAgICAgPG1ldGEgY2hhcnNldD0ndXRmLTgnPgogICAgICAgIDxtZXRhIG5hbWU9J2F1dGhvcicgY29udGVudD0nU3phYsOzIEzDoXN6bMOzIEFuZHLDoXMgLy8gaHUtenphJz4KICAgICAgICA8bGluayByZWw9J2F1dGhvcicgaHJlZj0naHR0cHM6Ly96emEuaHUnPgogICAgICAgIDxsaW5rIHJlbD0nbGljZW5zZScgaHJlZj0nL2xpY2Vuc2UuaHRtbCc+CiAgICAgICAgPGxpbmsgcmVsPSdoZWxwJyBocmVmPSdodHRwczovL3Vib3QuaHUnPgogICAgICAgIDxsaW5rIHJlbD0naWNvbicgdHlwZT0naW1hZ2UvcG5nJyBocmVmPScvZmF2aWNvbi5wbmcnIHNpemVzPScxMjh4MTI4Jz4KICAgICAgICA8bGluayByZWw9J3Nob3J0Y3V0IGljb24nIHR5cGU9J2ltYWdlL3gtaWNvbicgaHJlZj0nL2Zhdmljb24uaWNvJz4KICAgICAgICA8dGl0bGU+zrxCb3QgTUlUIExpY2Vuc2U8L3RpdGxlPgogICAgICAgIDxzdHlsZT4KICAgICAgICAgICAgYm9keSAgICAgeyBmb250LWZhbWlseTogR2FyYW1vbmQsIEJhc2tlcnZpbGxlLCBCYXNrZXJ2aWxsZSBPbGQgRmFjZSwgVGltZXMgTmV3IFJvbWFuLCBzZXJpZjsgfQogICAgICAgICAgICBhICAgICAgICB7IGNvbG9yOiByZ2IoMTAwLCAxMDAsIDEwMCk7IHRyYW5zaXRpb246IDAuNzVzOyB9CiAgICAgICAgICAgIGE6YWN0aXZlIHsgY29sb3I6IHJnYig1MCwgNTAsIDUwKTsgdHJhbnNpdGlvbjogMC4xczsgfQogICAgICAgIDwvc3R5bGU+CiAgICA8L2hlYWQ+CiAgICA8Ym9keT4KICAgICAgICA8aDE+CiAgICAgICAgICAgIFRoZSBsaWNlbnNlIG9mIHRoZSDOvEJvdCBmaXJtd2FyZQogICAgICAgIDwvaDE+CiAgICAgICAgVGhpcyBmaWxlIGlzIHBhcnQgb2YgdUJvdF9maXJtd2FyZS48YnI+CiAgICAgICAgPGEgaHJlZj0naHR0cHM6Ly96emEuaHUvdUJvdF9maXJtd2FyZScgdGFyZ2V0PSdfYmxhbmsnPmh0dHBzOi8venphLmh1L3VCb3RfZmlybXdhcmU8L2E+PGJyPgogICAgICAgIDxhIGhyZWY9J2h0dHBzOi8vZ2l0Lnp6YS5odS91Qm90X2Zpcm13YXJlJyB0YXJnZXQ9J19ibGFuayc+aHR0cHM6Ly9naXQuenphLmh1L3VCb3RfZmlybXdhcmU8L2E+PGJyPjxicj48YnI+CiAgICAgICAgPGgyPgogICAgICAgICAgICBNSVQgTGljZW5zZQogICAgICAgIDwvaDI+CiAgICAgICAgQ29weXJpZ2h0IChjKSAyMDIwLTIwMjEgU3phYsOzIEzDoXN6bMOzIEFuZHLDoXMgLy8gaHUtenphPGJyPjxicj4KICAgICAgICBQZXJtaXNzaW9uIGlzIGhlcmVieSBncmFudGVkLCBmcmVlIG9mIGNoYXJnZSwgdG8gYW55IHBlcnNvbiBvYnRhaW5pbmcgYSBjb3B5PGJyPgogICAgICAgIG9mIHRoaXMgc29mdHdhcmUgYW5kIGFzc29jaWF0ZWQgZG9jdW1lbnRhdGlvbiBmaWxlcyAodGhlICJTb2Z0d2FyZSIpLCB0byBkZWFsPGJyPgogICAgICAgIGluIHRoZSBTb2Z0d2FyZSB3aXRob3V0IHJlc3RyaWN0aW9uLCBpbmNsdWRpbmcgd2l0aG91dCBsaW1pdGF0aW9uIHRoZSByaWdodHM8YnI+CiAgICAgICAgdG8gdXNlLCBjb3B5LCBtb2RpZnksIG1lcmdlLCBwdWJsaXNoLCBkaXN0cmlidXRlLCBzdWJsaWNlbnNlLCBhbmQvb3Igc2VsbDxicj4KICAgICAgICBjb3BpZXMgb2YgdGhlIFNvZnR3YXJlLCBhbmQgdG8gcGVybWl0IHBlcnNvbnMgdG8gd2hvbSB0aGUgU29mdHdhcmUgaXM8YnI+CiAgICAgICAgZnVybmlzaGVkIHRvIGRvIHNvLCBzdWJqZWN0IHRvIHRoZSBmb2xsb3dpbmcgY29uZGl0aW9uczo8YnI+PGJyPgogICAgICAgIFRoZSBhYm92ZSBjb3B5cmlnaHQgbm90aWNlIGFuZCB0aGlzIHBlcm1pc3Npb24gbm90aWNlIHNoYWxsIGJlIGluY2x1ZGVkIGluIGFsbDxicj4KICAgICAgICBjb3BpZXMgb3Igc3Vic3RhbnRpYWwgcG9ydGlvbnMgb2YgdGhlIFNvZnR3YXJlLjxicj48YnI+CiAgICAgICAgVEhFIFNPRlRXQVJFIElTIFBST1ZJREVEICJBUyBJUyIsIFdJVEhPVVQgV0FSUkFOVFkgT0YgQU5ZIEtJTkQsIEVYUFJFU1MgT1I8YnI+CiAgICAgICAgSU1QTElFRCwgSU5DTFVESU5HIEJVVCBOT1QgTElNSVRFRCBUTyBUSEUgV0FSUkFOVElFUyBPRiBNRVJDSEFOVEFCSUxJVFksPGJyPgogICAgICAgIEZJVE5FU1MgRk9SIEEgUEFSVElDVUxBUiBQVVJQT1NFIEFORCBOT05JTkZSSU5HRU1FTlQuIElOIE5PIEVWRU5UIFNIQUxMIFRIRTxicj4KICAgICAgICBBVVRIT1JTIE9SIENPUFlSSUdIVCBIT0xERVJTIEJFIExJQUJMRSBGT1IgQU5ZIENMQUlNLCBEQU1BR0VTIE9SIE9USEVSPGJyPgogICAgICAgIExJQUJJTElUWSwgV0hFVEhFUiBJTiBBTiBBQ1RJT04gT0YgQ09OVFJBQ1QsIFRPUlQgT1IgT1RIRVJXSVNFLCBBUklTSU5HIEZST00sPGJyPgogICAgICAgIE9VVCBPRiBPUiBJTiBDT05ORUNUSU9OIFdJVEggVEhFIFNPRlRXQVJFIE9SIFRIRSBVU0UgT1IgT1RIRVIgREVBTElOR1MgSU4gVEhFPGJyPgogICAgICAgIFNPRlRXQVJFLjxicj4KICAgIDwvYm9keT4KPC9odG1sPgo="


def getStyleCss() -> str:
    return "Ym9keSB7CiAgICAgZm9udC1mYW1pbHk6IEdhcmFtb25kLCBCYXNrZXJ2aWxsZSwgQmFza2VydmlsbGUgT2xkIEZhY2UsIFRpbWVzIE5ldyBSb21hbiwgc2VyaWY7Cn0KCmEgewogICAgIGNvbG9yOiByZ2IoMTAwLCAxMDAsIDEwMCk7CiAgICAgdHJhbnNpdGlvbjogMC43NXM7CiAgICAgdGV4dC1kZWNvcmF0aW9uOiB1bmRlcmxpbmUgI0JCQiBkb3R0ZWQgMXB4Owp9CgphOmFjdGl2ZSB7CiAgICAgY29sb3I6IHJnYig1MCwgNTAsIDUwKTsKICAgICB0cmFuc2l0aW9uOiAwLjFzOwp9CgpociB7CiAgICAgY29sb3I6ICNFRUU7Cn0KCnRhYmxlIHsKICAgICBtYXJnaW46IDMwcHg7Cn0KCi5kYXRhIHRkIHsKICAgICBwYWRkaW5nOiA1cHg7CiAgICAgYm9yZGVyLWJvdHRvbTogZG90dGVkIDFweCAjQUFBOwp9Cgpib2R5LnJhdyBhIHsKICAgICB0ZXh0LWRlY29yYXRpb246IG5vbmU7Cn0KCmJvZHkucmF3IHRhYmxlIHsKICAgICBtYXJnaW46IDMwcHg7Cn0KCmJvZHkucmF3IHRkLCB0aCB7CiAgICAgcGFkZGluZzogMTBweCAyNXB4Owp9Cgpib2R5LnJhdyB0aGVhZCB7CiAgICAgY29sb3I6ICNGRkY7CiAgICAgYmFja2dyb3VuZDogIzU1NTsKfQoKYm9keS5yYXcgdGQ6bnRoLWNoaWxkKGV2ZW4pIHsKICAgICB0ZXh0LWFsaWduOiByaWdodDsKfQoKYm9keS5yYXcgdHI6bnRoLWNoaWxkKGV2ZW4pIHsKICAgICBiYWNrZ3JvdW5kOiAjRUVFOwp9Cgpib2R5LnJhdyAuaW5mbyB7CiAgICAgdGV4dC1hbGlnbjogY2VudGVyOwp9CgpzdmcgewogICAgIHdpZHRoOiAxMDBweDsKICAgICBoZWlnaHQ6IDEwMHB4OwogICAgIGZpbGw6IHJnYigxNjAsIDE2MCwgMTYwKTsKICAgICB0cmFuc2l0aW9uOiAwLjc1czsKfQoKc3ZnOmFjdGl2ZSB7CiAgICAgZmlsbDogcmdiKDgwLCA4MCwgODApOwogICAgIHRyYW5zaXRpb246IDAuMXM7Cn0KCi5kcml2ZSB7CiAgICAgaGVpZ2h0OiA0MDBweDsKfQoKLnNpbXBsZSB7CiAgICAgaGVpZ2h0OiA5MDBweDsKfQoKLnBybyB7CiAgICAgaGVpZ2h0OiAxMDAwcHg7Cn0KCi5wYW5lbCB7CiAgICAgd2lkdGg6IDYwMHB4OwogICAgIG1hcmdpbjogYXV0bzsKICAgICB0ZXh0LWFsaWduOiBjZW50ZXI7Cn0KCi5saW5rcyB7CiAgICAgd2lkdGg6IDM1MHB4OwogICAgIHBhZGRpbmc6IDA7CiAgICAgbWFyZ2luOiAxMDBweCBhdXRvOwogICAgIGJvcmRlci10b3A6IDA7CiAgICAgYm9yZGVyOiAxcHggc29saWQgI0JCQjsKICAgICBib3JkZXItcmFkaXVzOiAxNXB4IDE1cHggMCAwOwogICAgIGZvbnQtc2l6ZTogMjBweDsKICAgICBjb2xvcjogIzg4ODsKfQoKLmxpbmtzIGxpIHsKICAgICBsaXN0LXN0eWxlOiBub25lOwogICAgIGJhY2tncm91bmQ6ICNFRUU7CiAgICAgcGFkZGluZzogMTBweCAyMHB4OwogICAgIGJvcmRlci10b3A6IDFweCBzb2xpZCAjQ0NDOwp9CgoubGlua3MgbGk6Zmlyc3QtY2hpbGQgewogICAgIGNvbG9yOiAjRkZGOwogICAgIGJhY2tncm91bmQ6ICM1NTU7CiAgICAgYm9yZGVyOiBub25lOwogICAgIGJvcmRlci1yYWRpdXM6IDEwcHggMTBweCAwIDA7Cn0KIAo="


def getTurtleSvg() -> str:
    return "PHN2ZyBzdHlsZT0nZGlzcGxheTpub25lJyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnPgogICAgPGRlZnM+CiAgICAgICAgPHN5bWJvbCBpZD0nYXJyb3cnIHdpZHRoPScxMDAnIGhlaWdodD0nMTAwJyB2aWV3Qm94PScwIDAgNDAwIDQwMCcgeG1sbnM6dj0naHR0cHM6Ly92ZWN0YS5pby9uYW5vJz4KICAgICAgICAgICAgPHBhdGggZD0nTTE4Ni42NjcgMy43MjlsLTkgLjk3NkM3MS42MDUgMTUuODUxLTguNTg5IDExNi44MTIgNC41MzcgMjIyLjY2NyAyNC44NzIgMzg2LjY0OCAyMjMuMDQgNDU1LjcyMyAzMzkuMzgxIDMzOS4zODEgNDU0LjYxNyAyMjQuMTQ1IDM4Ny45MDIgMjcuMzg3IDIyNiA0Ljk5N2MtNy4yNjItMS4wMDQtMzQuMjAyLTEuODczLTM5LjMzMy0xLjI2OE0yMDYuNzYzIDQzbDk1LjQ0NiAxMzUuNjY3IDEwLjM3MSAxNC41OTJjMS41NDMgMi4wMjggMS41ODQgMi4yMjEuNDAzIDEuODkxLS43MjQtLjIwMy0zLjcxNi0uODYtNi42NS0xLjQ2TDI5MiAxOTAuNjhsLTE5LTQuMDA0LTE3LjYyNC0zLjgwN2MtMTkuMTExLTQuMzItMTkuNDQ2LTMuNzU2LTE1LjcwMyAyNi40NjRsMS42NzEgMTUuMzM0IDEwLjA0OSA5Ni42NjZMMjUzLjY3OCAzNDRsMS4zOTUgMTQuODMzLjQ1MyA0LjVIMTQ5LjE2M2wuMzg4LTIuNWMuMjEzLTEuMzc1LjU3Mi00LjkuNzk3LTcuODMzczEuMjc1LTEzLjQzMyAyLjMzMi0yMy4zMzNsNi42MzctNjRjOS4yMjctODcuNzQzIDguNTM2LTc5Ljc3NSA3LjEwNi04MS45NTYtMS41MDMtMi4yOTYtNC4wMy0zLjIxOC03LjM5My0yLjctMy4wMDkuNDY0LTMxLjQ1NSA2LjA1Ny01Ni4yOTMgMTEuMDY5LTguOTQ1IDEuODA1LTE2LjM2IDMuMTg2LTE2LjQ3OCAzLjA2OHM0LjczMy02Ljk0OSAxMC43NzktMTUuMTgxbDE3LjE0NC0yMy4zNzdMMTUwLjY4NiAxMDdsMTYuODk0LTIzIDE3LjY5MS0yNCAxMy41NjItMTguNTA2YzEuODgyLTIuNjYyIDMuNjE2LTQuNjEyIDMuODU1LTQuMzM0czIuMDczIDIuOTA3IDQuMDc1IDUuODQnIGZpbGwtcnVsZT0nZXZlbm9kZCcvPgogICAgICAgIDwvc3ltYm9sPgoKICAgICAgICA8c3ltYm9sIGlkPSdwbGF5JyB3aWR0aD0nMTAwJyBoZWlnaHQ9JzEwMCcgdmlld0JveD0nMCAwIDQwMCA0MDAnIHhtbG5zOnY9J2h0dHBzOi8vdmVjdGEuaW8vbmFubyc+CiAgICAgICAgICAgIDxwYXRoIGQ9J00xODYuNjY3IDMuNzI5bC05IC45NzZDNzEuNjA1IDE1Ljg1MS04LjU4OSAxMTYuODEyIDQuNTM3IDIyMi42NjcgMjQuODcyIDM4Ni42NDggMjIzLjA0IDQ1NS43MjMgMzM5LjM4MSAzMzkuMzgxIDQ1NC42MTcgMjI0LjE0NSAzODcuOTAyIDI3LjM4NyAyMjYgNC45OTdjLTcuMjYyLTEuMDA0LTM0LjIwMi0xLjg3My0zOS4zMzMtMS4yNjhtLTk2LjU4MiA5OC42NDhjNC44MjQgMi40NDQgOC44MDcgNi42OTggMTAuNDk1IDExLjIxbDEuNDIgMy43OTZ2MTY1LjQyNmwtMi4wMTIgNC4yMTZjLTcuODA0IDE2LjM1Mi0zMC41ODUgMTYuMjM1LTM4Ljc1MS0uMTk5bC0xLjU3LTMuMTU5LS4xNzUtODIuMzAzYy0uMTk0LTkxLjU2OC0uNDMzLTg2LjQxNyA0LjMwNS05Mi44NzMgNS41OTMtNy42MjMgMTcuNzM4LTEwLjQ0NyAyNi4yODgtNi4xMTRtNjkuODE3LTEuNzM4YzEuMjI1LjM1MSA5LjMyMyA0LjUyMSAxNy45OTYgOS4yNjZMMjkzIDE3Mi42NTRjMzMuNDU4IDE4LjEwMiA0NS44MTQgMjUuMDQxIDQ2LjM0MSAyNi4wMjcgMS4xNDQgMi4xMzctMS4wOTcgMy41OTYtMjcuNjc0IDE4LjAyMWwtNDUgMjQuNDY3TDIyOSAyNjEuNjc3bC00My4zMzMgMjMuNjY1Yy0yOS40NzggMTYuMTQ4LTMyLjgzNiAxNi45OTMtMzYuODI4IDkuMjYtMS42NDItMy4xODEtLjgzNy0xODkuNDI1LjgyOC0xOTEuMjkgMi41ODktMi45MDIgNi4xNzQtMy44MzggMTAuMjM1LTIuNjczJyBmaWxsLXJ1bGU9J2V2ZW5vZGQnLz4KICAgICAgICA8L3N5bWJvbD4KCiAgICAgICAgPHN5bWJvbCBpZD0ncGF1c2UnIHdpZHRoPScxMDAnIGhlaWdodD0nMTAwJyB2aWV3Qm94PScwIDAgNDAwIDQwMCcgeG1sbnM6dj0naHR0cHM6Ly92ZWN0YS5pby9uYW5vJz4KICAgICAgICAgICAgPHBhdGggZD0nTTE4Ni42NjcgMy43MjlsLTkgLjk3NkM0Mi4zNTEgMTguOTI2LTM3LjI4OCAxNjguMjU0IDI1LjI5NyAyOTAuNDExYzY0Ljc2MyAxMjYuNDA5IDI0MC41NyAxNDQuMDAzIDMyOC45NzYgMzIuOTIyQzQ0OS40OTkgMjAzLjY4MiAzNzcuOTA0IDI2LjAwNSAyMjYgNC45OTdjLTcuMjYyLTEuMDA0LTM0LjIwMi0xLjg3My0zOS4zMzMtMS4yNjhtLTIxLjI0OCA5OC42NDhjNC44MjMgMi40NDQgOC44MDYgNi42OTggMTAuNDk0IDExLjIxbDEuNDIgMy43OTZWMjgxLjk1bC0xLjQzNiAzLjgzOGMtNi40NzIgMTcuMjk4LTMwLjkyNiAxNy45NDQtMzkuMzI3IDEuMDM4bC0xLjU3LTMuMTU5LS4xNzQtODIuMzAzYy0uMTk1LTkxLjU2OC0uNDMzLTg2LjQxNyA0LjMwNC05Mi44NzMgNS41OTMtNy42MjMgMTcuNzM4LTEwLjQ0NyAyNi4yODktNi4xMTRtODguNjY2IDBjNC44MjQgMi40NDQgOC44MDcgNi42OTggMTAuNDk1IDExLjIxbDEuNDIgMy43OTZWMjgxLjk1bC0xLjQzNiAzLjgzOGMtNi40NzIgMTcuMjk4LTMwLjkyNiAxNy45NDQtMzkuMzI3IDEuMDM4bC0xLjU3LTMuMTU5LS4xNzUtODIuMzAzYy0uMTk0LTkxLjU2OC0uNDMzLTg2LjQxNyA0LjMwNS05Mi44NzMgNS41OTMtNy42MjMgMTcuNzM4LTEwLjQ0NyAyNi4yODgtNi4xMTQnIGZpbGwtcnVsZT0nZXZlbm9kZCcvPgogICAgICAgIDwvc3ltYm9sPgoKICAgICAgICA8c3ltYm9sIGlkPSdyZXBlYXQnIHdpZHRoPScxMDAnIGhlaWdodD0nMTAwJyB2aWV3Qm94PScwIDAgNDAwIDQwMCcgeG1sbnM6dj0naHR0cHM6Ly92ZWN0YS5pby9uYW5vJz4KICAgICAgICAgICAgPHBhdGggZD0nTTE4Ni42NjcgMy43MjlsLTkgLjk3NkM0Mi4zNTEgMTguOTI2LTM3LjI4OCAxNjguMjU0IDI1LjI5NyAyOTAuNDExYzY0Ljc2MyAxMjYuNDA5IDI0MC41NyAxNDQuMDAzIDMyOC45NzYgMzIuOTIyQzQ0OS40OTkgMjAzLjY4MiAzNzcuOTA0IDI2LjAwNSAyMjYgNC45OTdjLTcuMjYyLTEuMDA0LTM0LjIwMi0xLjg3My0zOS4zMzMtMS4yNjhtMjIuNjY2IDU0Ljk1NWMzMC4xNzUgMi4yODIgNjEuMDA4IDE1LjExNSA4Mi40OTYgMzQuMzM1bDQuMjc4IDMuODI2IDMuMTEzLTIuOTczIDEyLjk3OC0xMi41ODljMTIuMjU4LTExLjk1IDE0LjM2Ny0xMi45NjUgMjAuODMtMTAuMDMgNy4zOTQgMy4zNTkgNy4wNDkuNzEgNi44MjcgNTIuNDY2bC0uMTg4IDQ0LjA1Mi0xLjkyMyAyLjUyYy0zLjk2NyA1LjIwMS0yLjA2OCA1LjAxMS01MC4yNjUgNS4wMjgtNDkuODYzLjAxNy00OC4yNDIuMjM2LTUxLjU1OS02Ljk4Ni0zLjE2OC02LjkwMS0yLjY5My03LjczNSAxMy45MDQtMjQuNDI2bDEzLjY4My0xMy43NTktNC43Ny0zLjkwN2MtMzYuODU3LTMwLjE5Mi05MS4wMzUtMjcuNDE4LTEyNC43NTkgNi4zODgtNTIuNTgxIDUyLjcxLTI1LjUxOCAxNDIuNDI5IDQ3LjQ3NSAxNTcuMzg4IDQ1LjI1NCA5LjI3NCA5Mi4zNS0xNy41OTYgMTA2LjQ4Mi02MC43NTMgMi40NzQtNy41NTUuMjg0LTYuOTAyIDIzLjkyNy03LjEyNGwyMC42MzgtLjE5NCAyLjE2NSAxLjgyMWMyLjg4MSAyLjQyNSAyLjU4MiA1Ljg1OC0xLjYxNCAxOC41NjYtNDIuNzMyIDEyOS40MTktMjI1LjE5IDEyNy41OTgtMjY3LjI0OS0yLjY2NkMzOC43MTQgMTU1Ljc3IDEwMC41MSA2NS4wNDkgMTg5LjA2MSA1OC43MTNjMTAuNzEyLS43NjYgMTAuNTMtLjc2NiAyMC4yNzItLjAyOScgZmlsbC1ydWxlPSdldmVub2RkJy8+CiAgICAgICAgPC9zeW1ib2w+CgogICAgICAgIDxzeW1ib2wgaWQ9J0YxJyB3aWR0aD0nMTAwJyBoZWlnaHQ9JzEwMCcgdmlld0JveD0nMCAwIDQwMCA0MDAnIHhtbG5zOnY9J2h0dHBzOi8vdmVjdGEuaW8vbmFubyc+CiAgICAgICAgICAgIDxwYXRoIGQ9J00xODYuNjY3IDMuNzI5bC05IC45NzZDNDIuMzUxIDE4LjkyNi0zNy4yODggMTY4LjI1NCAyNS4yOTcgMjkwLjQxMWM2NC43NjMgMTI2LjQwOSAyNDAuNTcgMTQ0LjAwMyAzMjguOTc2IDMyLjkyMkM0NDkuNDk5IDIwMy42ODIgMzc3LjkwNCAyNi4wMDUgMjI2IDQuOTk3Yy03LjI2Mi0xLjAwNC0zNC4yMDItMS44NzMtMzkuMzMzLTEuMjY4bTIyLjMwOCA4NC44OTZjLjIxMi4zNDQtMS4zMjEgOS43NzctMy40MDcgMjAuOTYxbC0zLjc5MyAyMC4zMzUtMi41OTkuNDM5Yy0zLjI1Ni41NS0yLjQxMiAyLjM2Ni02Ljk5LTE1LjAyN2wtMy45NDgtMTUtNTkuNTcxLS4zNDd2NzQuODc3bDIyLjA2Mi0uMzUxYzI1Ljk5Ny0uNDE0IDIzLjA2My44NTEgMjYuODc1LTExLjU4NWwyLjgzOC05LjI2IDYuNTU4LS4zOTItLjIxMSA1My43MjVoLTYuNGwtMi45MTMtOS42NjdjLTMuODUxLTEyLjc3OS0uODA5LTExLjQzMi0yNi43NDctMTEuODQ1bC0yMi4wNjItLjM1MXYzNi4zODRjMCA0Mi4zMzktMS4xODYgMzcuNDI2IDkuODQ4IDQwLjgxOGw5LjQ4NSAyLjkxN2MxLjM3Ny40MjUgMS43MDIuOTk3IDEuODcyIDMuMjk2bC4yMDUgMi43ODFIODMuMzk0bC0uNDQ3LTIuMzgzYy0uNTgxLTMuMDkzLS42OC0zLjAyOCA5LjA1My01LjkxMiA0LjU4My0xLjM1OCA4Ljc4My0yLjkwOCA5LjMzMy0zLjQ0NCAxLjA4Ni0xLjA1OCAxLjU3OS0xNTMuODcuNTA5LTE1Ny42NzYtLjU1MS0xLjk1OS0uOTY4LTIuMTU4LTExLjUwOS01LjQ5Mkw4MyA5NC4xMDZsLS40MS01LjQzMSA0OC4yMDUtLjE3NSA2Mi45OTktLjMzOGM4LjY4NC0uMDk1IDE0Ljk1NC4wOTYgMTUuMTgxLjQ2M202Mi42MTUgNjIuMDQyYy0xLjc1NCA1My4zMTEtMS45ODMgNzIuMjY2LTEuMTUxIDk1LjI0My41MzUgMTQuNzc4LS40IDEzLjUyNCAxMi41NjEgMTYuODQ4IDExLjA5MiAyLjg0NiAxMi4zMzMgMy41MiAxMi4zMzMgNi43MDN2MS44NzJoLTc0bC0uMTExLTEuNjY2LS4xNjYtMi43OTJjLS4wNDUtLjkwOSAyLjEwMS0xLjY2NSAxMS4xOTUtMy45NDIgNi4xODgtMS41NDkgMTEuNzM4LTMuMzA0IDEyLjMzNC0zLjkgMS4wMzQtMS4wMzYgMS43NDEtOTIuOTI5LjcyMi05My45NDgtLjE2OS0uMTY5LTUuNTU3LS44MDItMTEuOTc0LTEuNDA2LTE1LjMxMy0xLjQ0My0xNC41MjItMS4yMy0xNS4wNS00LjA0OS0uNTk4LTMuMTg3LTEuMzQtMi45MDQgMTQuMjE1LTUuNDA2TDI1NyAxNTAuMDcyYzEzLjgzNS0yLjUgMTQuNjkxLTIuNDY1IDE0LjU5LjU5NScgZmlsbC1ydWxlPSdldmVub2RkJy8+CiAgICAgICAgPC9zeW1ib2w+CgogICAgICAgIDxzeW1ib2wgaWQ9J0YyJyB3aWR0aD0nMTAwJyBoZWlnaHQ9JzEwMCcgdmlld0JveD0nMCAwIDQwMCA0MDAnIHhtbG5zOnY9J2h0dHBzOi8vdmVjdGEuaW8vbmFubyc+CiAgICAgICAgICAgIDxwYXRoIGQ9J00xODYuNjY3IDMuNzI5bC05IC45NzZDNDIuMzUxIDE4LjkyNi0zNy4yODggMTY4LjI1NCAyNS4yOTcgMjkwLjQxMWM2NC43NjMgMTI2LjQwOSAyNDAuNTcgMTQ0LjAwMyAzMjguOTc2IDMyLjkyMkM0NDkuNDk5IDIwMy42ODIgMzc3LjkwNCAyNi4wMDUgMjI2IDQuOTk3Yy03LjI2Mi0xLjAwNC0zNC4yMDItMS44NzMtMzkuMzMzLTEuMjY4bTIyLjMwOCA4NC44OTZjLjIxMi4zNDQtMS4zMjEgOS43NzctMy40MDcgMjAuOTYxbC0zLjc5MyAyMC4zMzUtMi41OTkuNDM5Yy0zLjI1Ni41NS0yLjQxMiAyLjM2Ni02Ljk5LTE1LjAyN2wtMy45NDgtMTUtNTkuNTcxLS4zNDd2NzQuODc3bDIyLjA2Mi0uMzUxYzI1Ljk5Ny0uNDE0IDIzLjA2My44NTEgMjYuODc1LTExLjU4NWwyLjgzOC05LjI2IDYuNTU4LS4zOTItLjIxMSA1My43MjVoLTYuNGwtMi45MTMtOS42NjdjLTMuODUxLTEyLjc3OS0uODA5LTExLjQzMi0yNi43NDctMTEuODQ1bC0yMi4wNjItLjM1MXYzNi4zODRjMCA0Mi4zMzktMS4xODYgMzcuNDI2IDkuODQ4IDQwLjgxOGw5LjQ4NSAyLjkxN2MxLjM3Ny40MjUgMS43MDIuOTk3IDEuODcyIDMuMjk2bC4yMDUgMi43ODFIODMuMzk0bC0uNDQ3LTIuMzgzYy0uNTgxLTMuMDkzLS42OC0zLjAyOCA5LjA1My01LjkxMiA0LjU4My0xLjM1OCA4Ljc4My0yLjkwOCA5LjMzMy0zLjQ0NCAxLjA4Ni0xLjA1OCAxLjU3OS0xNTMuODcuNTA5LTE1Ny42NzYtLjU1MS0xLjk1OS0uOTY4LTIuMTU4LTExLjUwOS01LjQ5Mkw4MyA5NC4xMDZsLS40MS01LjQzMSA0OC4yMDUtLjE3NSA2Mi45OTktLjMzOGM4LjY4NC0uMDk1IDE0Ljk1NC4wOTYgMTUuMTgxLjQ2M204Mi42OTIgNjAuMDNDMzA5LjI0MyAxNTQuMjk3IDMxOCAxNjQuODQ0IDMxOCAxODAuMzcxYzAgMjEuOTktMTQuNDQ5IDM4LjUyMi01Ni41NDQgNjQuNjk1TDI1MS45MTEgMjUxbDMyLjE3Mi4xNzNjMTcuNjk0LjA5NSAzMi4zODktLjA1NSAzMi42NTYtLjMzM3MyLjY0OC01LjIyMiA1LjI5My0xMC45ODVsNC44MDktMTAuNDc4IDIuNzQ2LS41NTZjMS42NTgtLjMzNiAyLjg0Ny0uMzA3IDMgLjA3My4yOTQuNzI4LTEuODQ0IDM4LjY5LTIuMzA1IDQwLjkzOWwtLjMwNyAxLjVIMjI0LjA2bC0uMzMxLTIuMTY2Yy0uMTgyLTEuMTkyLS40NTctMy41NzEtLjYxLTUuMjg3bC0uMjc4LTMuMTIgOS43NDYtNi40NzVjNDUtMjkuODk0IDYwLjMzMi00Ny4zNzIgNTguNTI1LTY2LjcxNy0xLjk4Ny0yMS4yNzktMjcuMDE3LTI5LjU5MS01My45OTItMTcuOTI5LTYuMTY4IDIuNjY3LTUuNzE3IDIuNzczLTguMzktMS45NjItMi42NDktNC42OTUtMi43OTItNC4yNTggMi40MzctNy40NTUgMjAuMTE4LTEyLjI5OSA0My45OTUtMTYuODY0IDYwLjUtMTEuNTY3JyBmaWxsLXJ1bGU9J2V2ZW5vZGQnLz4KICAgICAgICA8L3N5bWJvbD4KCiAgICAgICAgPHN5bWJvbCBpZD0nRjMnIHdpZHRoPScxMDAnIGhlaWdodD0nMTAwJyB2aWV3Qm94PScwIDAgNDAwIDQwMCcgeG1sbnM6dj0naHR0cHM6Ly92ZWN0YS5pby9uYW5vJz4KICAgICAgICAgICAgPHBhdGggZD0nTTE4Ni42NjcgMy43MjlsLTkgLjk3NkM0Mi4zNTEgMTguOTI2LTM3LjI4OCAxNjguMjU0IDI1LjI5NyAyOTAuNDExYzY0Ljc2MyAxMjYuNDA5IDI0MC41NyAxNDQuMDAzIDMyOC45NzYgMzIuOTIyQzQ0OS40OTkgMjAzLjY4MiAzNzcuOTA0IDI2LjAwNSAyMjYgNC45OTdjLTcuMjYyLTEuMDA0LTM0LjIwMi0xLjg3My0zOS4zMzMtMS4yNjhtMjIuMzA4IDg0Ljg5NmMuMjEyLjM0NC0xLjMyMSA5Ljc3Ny0zLjQwNyAyMC45NjFsLTMuNzkzIDIwLjMzNS0yLjU5OS40MzljLTMuMjU2LjU1LTIuNDEyIDIuMzY2LTYuOTktMTUuMDI3bC0zLjk0OC0xNS01OS41NzEtLjM0N3Y3NC44NzdsMjIuMDYyLS4zNTFjMjUuOTk3LS40MTQgMjMuMDYzLjg1MSAyNi44NzUtMTEuNTg1bDIuODM4LTkuMjYgNi41NTgtLjM5Mi0uMjExIDUzLjcyNWgtNi40bC0yLjkxMy05LjY2N2MtMy44NTEtMTIuNzc5LS44MDktMTEuNDMyLTI2Ljc0Ny0xMS44NDVsLTIyLjA2Mi0uMzUxdjM2LjM4NGMwIDQyLjMzOS0xLjE4NiAzNy40MjYgOS44NDggNDAuODE4bDkuNDg1IDIuOTE3YzEuMzc3LjQyNSAxLjcwMi45OTcgMS44NzIgMy4yOTZsLjIwNSAyLjc4MUg4My4zOTRsLS40NDctMi4zODNjLS41ODEtMy4wOTMtLjY4LTMuMDI4IDkuMDUzLTUuOTEyIDQuNTgzLTEuMzU4IDguNzgzLTIuOTA4IDkuMzMzLTMuNDQ0IDEuMDg2LTEuMDU4IDEuNTc5LTE1My44Ny41MDktMTU3LjY3Ni0uNTUxLTEuOTU5LS45NjgtMi4xNTgtMTEuNTA5LTUuNDkyTDgzIDk0LjEwNmwtLjQxLTUuNDMxIDQ4LjIwNS0uMTc1IDYyLjk5OS0uMzM4YzguNjg0LS4wOTUgMTQuOTU0LjA5NiAxNS4xODEuNDYzbTc5LjM1OCA1OS45OGMyMC4xNzIgNS4zNDggMzEuMzM0IDE3LjIzMSAzMS4zMzQgMzMuMzYgMCAxOC41NzYtMTEuOCAzMS44NDktMzYuODM0IDQxLjQzMy01LjM2MiAyLjA1My01LjI1NSAyLjMyIDEuMTMgMi44MTMgMzAuODQ1IDIuMzc4IDQ5LjUxNCAyNC44MjcgNDIuNzI1IDUxLjM3NC03LjY5MyAzMC4wNzktNDUuMzYzIDQ5LjY5MS0xMDEuNDE1IDUyLjc5OS05LjUwMS41MjctOC44NTIuODgtOS42MTctNS4yMzZsLS40NjUtMy43MjcgMi4yMzgtLjM1YzEuMjMxLS4xOTMgNC4zMzgtLjUyOSA2LjkwNC0uNzQ4IDQ3LjAyNC00LjAxIDc1Ljc3OS0yMi45NDMgNzUuOTIxLTQ5Ljk5LjEyNi0yNC4wOS0xOC45MTQtMzcuMzkyLTQ5LjE4NS0zNC4zNjEtNC40MjMuNDQzLTguMjM1LjkyNS04LjQ3MSAxLjA3LS41MjQuMzI0LTEuMjQ3LTMuODE0LTEuMjU3LTcuMTk2LS4wMDktMi43NzUtLjQwMS0yLjU3OCA3LjY1OS0zLjg0MiAzMi4xOTgtNS4wNDkgNDkuNTk0LTI0LjMzMSA0MS40OTEtNDUuOTg3LTYuNzYzLTE4LjA3Ni0zNi45NzgtMjIuNDctNjMuMzkyLTkuMjItMi4xNDUgMS4wNzYtMy45NzYgMS44NjItNC4wNjkgMS43NDctMS4wMzctMS4yOTYtNS4wMy04LjA1LTUuMDMtOC41MDkgMC0xLjczNSAxNy41My0xMC41NDQgMjYuNjY3LTEzLjQwMSAxMy44MTctNC4zMTkgMzEuODY0LTUuMTU4IDQzLjY2Ni0yLjAyOScgZmlsbC1ydWxlPSdldmVub2RkJy8+CiAgICAgICAgPC9zeW1ib2w+CgogICAgICAgIDxzeW1ib2wgaWQ9J3VuZG8nIHdpZHRoPScxMDAnIGhlaWdodD0nMTAwJyB2aWV3Qm94PScwIDAgNDAwIDQwMCcgeG1sbnM6dj0naHR0cHM6Ly92ZWN0YS5pby9uYW5vJz4KICAgICAgICAgICAgPHBhdGggZD0nTTE4Ni42NjcgMy43MjlsLTkgLjk3NkM3MS42MDUgMTUuODUxLTguNTg5IDExNi44MTIgNC41MzcgMjIyLjY2NyAyNC44NzIgMzg2LjY0OCAyMjMuMDQgNDU1LjcyMyAzMzkuMzgxIDMzOS4zODEgNDU0LjYxNyAyMjQuMTQ1IDM4Ny45MDIgMjcuMzg3IDIyNiA0Ljk5N2MtNy4yNjItMS4wMDQtMzQuMjAyLTEuODczLTM5LjMzMy0xLjI2OG0tNCAzNS41MzNjNi4zNDMgMi42MzcgNi4yNzcgMi4yODMgNi41NDkgMzQuNjkxLjEzMSAxNS42MDkuNDM2IDI4LjU2NS42NzggMjguNzkyczQuOTM5IDEuMDQzIDEwLjQzOSAxLjgxNkMyOTYuMTE2IDExOC4wMTYgMzU4LjM2IDIxMC43MTEgMzM0LjI1NiAzMDRjLTMuNzIzIDE0LjQwOC0xNi4wMDkgNDIuOTk5LTE2LjMxNSAzNy45NjctNC4xMzctNjguMDE2LTU4LjU5Mi0xMjUuNTM2LTEyNC4xMDgtMTMxLjA5M2wtNC41LS4zODItLjA3OSAyMi4yNTRjLS4xMTEgMzEuNDUtLjI2IDM0LjQ5NC0xLjc4MyAzNi41NTItMi45OTkgNC4wNTEtOC4wNTUgNS43NDEtMTIuMjYxIDQuMDk5LTMuMjc4LTEuMjgtMTE3LjY5MS05Ni4zNzctMTMwLjY1MS0xMDguNTk0LTguNTY1LTguMDc0LTcuNzA4LTEwLjg0MSA3LjMzOC0yMy42OTdMMTY4LjE1NiA0NC4xMmM3LjYyMi02LjE5MSA5LjY2Mi02Ljg3NCAxNC41MTEtNC44NTgnIGZpbGwtcnVsZT0nZXZlbm9kZCcvPgogICAgICAgIDwvc3ltYm9sPgoKICAgICAgICA8c3ltYm9sIGlkPSdjcm9zcycgd2lkdGg9JzEwMCcgaGVpZ2h0PScxMDAnIHZpZXdCb3g9JzAgMCA0MDAgNDAwJyB4bWxuczp2PSdodHRwczovL3ZlY3RhLmlvL25hbm8nPgogICAgICAgICAgICA8cGF0aCBkPSdNMTg2LjY2NyAzLjcyOWwtOSAuOTc2QzcxLjYwNSAxNS44NTEtOC41ODkgMTE2LjgxMiA0LjUzNyAyMjIuNjY3IDI0Ljg3MiAzODYuNjQ4IDIyMy4wNCA0NTUuNzIzIDMzOS4zODEgMzM5LjM4MSA0NTQuNjE3IDIyNC4xNDUgMzg3LjkwMiAyNy4zODcgMjI2IDQuOTk3Yy03LjI2Mi0xLjAwNC0zNC4yMDItMS44NzMtMzkuMzMzLTEuMjY4TTk4LjgwMSA2OS40MTZjNy44MzIgMS42NjIgNy41OTggMS40NTQgNTUuNTMyIDQ5LjMwNWw0NS4zMzQgNDUuMjU0TDI0NSAxMTguNzI0YzQ4LjUyMS00OC40MzMgNDcuNzUxLTQ3Ljc1NSA1Ni4yMDItNDkuNDE4IDE1LjkwNi0zLjEyOSAzMS44MjkgMTIuNzEyIDI4LjgwNSAyOC42NTgtMS41MDYgNy45NDEtLjUxIDYuODE2LTQ5LjE5MiA1NS41MzRsLTQ1Ljc5NyA0NS44MzEgNDUuNDIyIDQ1LjUwMmM0NC43MTggNDQuNzk2IDQ2LjkwMyA0Ny4xNzcgNDguNzc2IDUzLjE2OSA2LjM3NiAyMC4zOTQtMTUuNjExIDM5LjE0Ni0zNC43NTggMjkuNjQ1LTIuNzQzLTEuMzYxLTEyLjgzMS0xMS4wOC00OC43OTMtNDcuMDE0bC00NS45OTgtNDUuMjk4Yy0uMzY1IDAtMjEuMDY0IDIwLjM4NC00NS45OTkgNDUuMjk4LTQ4LjM0NSA0OC4zMDctNDcuODE3IDQ3Ljg0LTU1Ljk5MiA0OS40ODJDODAuOTE4IDMzMy40NzggNjQuODcyIDMxNC43OCA3MC4xMTggMjk4YzEuODczLTUuOTkyIDQuMDU3LTguMzczIDQ4Ljc3NS01My4xNjlsNDUuNDIyLTQ1LjUwMi00NS43OTctNDUuODMxYy00OC42ODItNDguNzE4LTQ3LjY4Ni00Ny41OTMtNDkuMTkxLTU1LjUzNC0zLjA5OC0xNi4zMzQgMTMuMDk5LTMyLjAyMiAyOS40NzQtMjguNTQ4JyBmaWxsLXJ1bGU9J2V2ZW5vZGQnLz4KICAgICAgICA8L3N5bWJvbD4KICAgIDwvZGVmcz4KPC9zdmc+Cg=="


files = {
    "turtle.svg":   (getTurtleSvg,  ("image/svg+xml; charset=UTF-8",), "getTurtleSvg"),
    "favicon.png":  (getFaviconPng, ("image/png",), "getFaviconPng"),
    "favicon.ico":  (getFaviconIco, ("image/png",), "getFaviconIco"),
    "style.css":    (getStyleCss,   ("text/css; charset=UTF-8",), "getStyleCss"),
    "license.html": (getLicenseHtml, ("text/html; charset=UTF-8",), "getLicenseHtml")
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

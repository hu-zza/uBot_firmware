import flashbdev, network, ubinascii, ujson, uos

firmware = (0, 1, 192)
initDatetime = (2021, 7, 20, 0, 23, 40, 0, 0)

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


files = {
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

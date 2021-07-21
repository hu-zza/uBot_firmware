"""
    uBot_firmware   // The firmware of the μBot, the educational floor robot. (A MicroPython port to ESP8266 with additional modules.)

    This file is part of uBot_firmware.
    [https://zza.hu/uBot_firmware]
    [https://git.zza.hu/uBot_firmware]


    MIT License

    Copyright (c) 2020-2021 Szabó László András // hu-zza

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

import gc, uos

import ubot_config as config
import ubot_turtle as turtle



###########
## GENERAL

def getSimplePage() -> str:
    return ("<!DOCTYPE html>\r\n"
            "<html>\r\n"
            "    <head>\r\n"
            "        <meta name='viewport' content='width=450'>\r\n"
            "        <meta charset='utf-8'>\r\n"
            "        <meta name='author' content='Szabó László András // hu-zza'>\r\n"
            "        <link rel='author' href='https://zza.hu'>\r\n"
            "        <link rel='license' href='/license.html'>\r\n"
            "        <link rel='help' href='https://ubot.hu'>\r\n"
            "        <link rel='icon' type='image/png' href='/android-chrome-512x512.png' sizes='512x512'>\r\n"
            "        <link rel='icon' type='image/png' href='/android-chrome-192x192.png' sizes='192x192'>\r\n"
            "        <link rel='icon' type='image/png' href='/favicon.png' sizes='192x192'>\r\n"
            "        <link rel='icon' type='image/png' href='/favicon-32x32.png' sizes='32x32'>\r\n"
            "        <link rel='icon' type='image/png' href='/favicon-16x16.png' sizes='16x16'>\r\n"
            "        <link rel='icon' type='image/x-icon' href='/favicon.ico'>\r\n"
            "        <link rel='shortcut icon' type='image/x-icon' href='/favicon.ico'>\r\n"
            "        <link rel='manifest' href='/site.webmanifest'>\r\n"
            "        <link rel='stylesheet' href='/style.css'>\r\n"
            "        <title>μBot | {title}</title>\r\n"
            "    </head>\r\n"
            "    <body>\r\n"
            "        <h1>{title}</h1>\r\n"
            "        {body}\r\n"
            "    </body>\r\n"
            "</html>\r\n\r\n")


def getPageHeadStart() -> str:
    return ("<!DOCTYPE html>\r\n"
            "<html>\r\n"
            "    <head>\r\n"
            "        <meta name='viewport' content='width=610'>\r\n"
            "        <meta charset='utf-8'>\r\n"
            "        <meta name='author' content='Szabó László András // hu-zza'>\r\n"
            "        <link rel='author' href='https://zza.hu'>\r\n"
            "        <link rel='license' href='/license.html'>\r\n"
            "        <link rel='help' href='https://ubot.hu'>\r\n"
            "        <link rel='icon' type='image/png' href='/android-chrome-512x512.png' sizes='512x512'>\r\n"
            "        <link rel='icon' type='image/png' href='/android-chrome-192x192.png' sizes='192x192'>\r\n"
            "        <link rel='icon' type='image/png' href='/favicon.png' sizes='192x192'>\r\n"
            "        <link rel='icon' type='image/png' href='/favicon-32x32.png' sizes='32x32'>\r\n"
            "        <link rel='icon' type='image/png' href='/favicon-16x16.png' sizes='16x16'>\r\n"
            "        <link rel='icon' type='image/x-icon' href='/favicon.ico'>\r\n"
            "        <link rel='shortcut icon' type='image/x-icon' href='/favicon.ico'>\r\n"
            "        <link rel='manifest' href='/site.webmanifest'>\r\n"
            "        <link rel='stylesheet' href='/style.css'>\r\n")


def getPageHeadEnd() -> str:
    return ("        <title>{}</title>\r\n"
            "    </head>\r\n"
            "    <body class='{}'>\r\n")


def getPageFooter() -> str:
    return ("    </body>\r\n"
            "</html>\r\n\r\n")


###########
## PANELS

def getTurtlePanel() -> str:
    return ("        <h3>Commands</h3>\r\n"
            "            {commands}\r\n"
            "        <br><br><hr><hr>\r\n"
            "        <h3>Program</h3>\r\n"
            "            {program}\r\n").format(commands = turtle.getCommandArray(), program  = turtle.getProgramArray())


def getSystemPanel() -> str:
    freeMemory, allocatedMemory = gc.mem_free(), gc.mem_alloc()
    allMemory = freeMemory + allocatedMemory
    freeMemoryPercent = freeMemory * 100 // allMemory

    stat = uos.statvfs("/")
    freeSpace = stat[4] * stat[0]       # f_bavail * f_bsize
    allSpace = stat[2] * stat[1]        # f_blocks * f_frsize
    freeSpacePercent = freeSpace * 100 // allSpace

    year, month, day, weekday, hour, minute, second, millisecond = config.datetime()
    uid = config.get("system", "id")
    idA = " - ".join(uid[i:i + 4] for i in range(0, 16, 4))
    idB = " - ".join(uid[i:i + 4] for i in range(16, 32, 4))

    major, minor, patch = config.get("system", "firmware")

    return ("        <h3>System info</h3>\r\n"
            "            <table class='data'>\r\n"
            "                <tr><td> <strong>Power on count:</strong> </td><td>{powerOns}</td><td>  </td></tr>\r\n"
            "                <tr><td> <strong>Firmware:</strong> </td><td>{major}.{minor}.{patch}</td><td><a href='/license.html'>MIT License</a></td></tr>\r\n"
            "                <tr><td> <strong>Free memory:</strong> </td><td>{freeMemoryPercent}%</td><td>{freeMemory} / {allMemory}</td></tr>\r\n"
            "                <tr><td> <strong>Free space:</strong> </td><td>{freeSpacePercent}%</td><td>{freeSpace} / {allSpace}</td></tr>\r\n"
            "                <tr><td> <strong>System RTC:</strong> </td><td colspan='2'>{year}. {month:02d}. {day:02d}.&nbsp;&nbsp;&nbsp;{hour:02d} : {minute:02d} : {second:02d}</td></tr>\r\n"
            "                <tr><td> <strong>μBot ID:</strong> </td><td colspan='2'>{idA}<br>{idB}</td></tr>"
            "            </table>\r\n").format(powerOns = config.get("system", "power_ons"),
                                               major = major, minor = minor, patch = patch,
                                               freeMemoryPercent = freeMemoryPercent, freeMemory = freeMemory, allMemory = allMemory,
                                               freeSpacePercent = freeSpacePercent, freeSpace = freeSpace, allSpace = allSpace,
                                               year = year, month = month, day = day, hour = hour, minute = minute, second = second,
                                               idA = idA, idB = idB)


def getServiceStatusPanel() -> str:
    moduleMap = {config.get(module, "name"): config.get(module, "active") for module in config.getModules()}

    statusReport = ""
    for name in sorted(moduleMap.keys()):
        statusReport += "                <tr><td> <strong>{}</strong> </td><td>{}</td><td>  </td></tr>\r\n"\
                        .format(name, moduleMap.get(name))

    return ("        <h3>Service status</h3>\r\n"
            "            <table class='data'>\r\n"
            + statusReport +
            "            </table>\r\n")


def getApPanel() -> str:
    return ("        <h3>Access point</h3>\r\n"
            "            <table class='data'>\r\n"
            "                <tr><td> <strong>Active:</strong> </td><td>{isApUp}</td><td>  </td></tr>\r\n"
            "                <tr><td> <strong>SSID:</strong> </td><td>{ssid}</td><td>  </td></tr>\r\n"
            "                <tr><td> <strong>Password:</strong> </td><td>{uBot_pwd}</td><td> </td></tr>\r\n"
            "                <tr><td> <strong>MAC address:</strong> </td><td colspan='2'>{macAddress}</tr>\r\n"
            "                <tr><td> <strong>IP address:</strong> </td><td>{ipAddress}</td><td>{subnetMask}</td></tr>\r\n"
            "                <tr><td> <strong>Gateway:</strong> </td><td>{gateway}</td><td> </td></tr>"
            "                <tr><td> <strong>DNS:</strong> </td><td>{dns}</td><td> </td></tr>"
            "            </table>\r\n").format(isApUp = config.get("ap", "active"),
                                               ssid = config.get("ap", "ssid"),
                                               uBot_pwd = config.get("ap", "password"),
                                               macAddress = config.get("ap", "mac").replace(":", " : "),
                                               ipAddress = config.get("ap", "ip"),
                                               subnetMask = config.get("ap", "netmask"),
                                               gateway = config.get("ap", "gateway"),
                                               dns = config.get("ap", "dns"))


def getDrivePanel() -> str:
    return ("        <table class='drive panel'>\r\n"
            "            <tr>\r\n"
            "                <td><img src='/turtle_arrow.svg' onclick='send(\"K\")' class='turtle arrow rot-45'></td>\r\n"
            "                <td><img src='/turtle_arrow.svg' onclick='send(\"F\")' class='turtle arrow'></td>\r\n"
            "                <td><img src='/turtle_arrow.svg' onclick='send(\"Q\")' class='turtle arrow rot45'></td>\r\n"
            "            </tr>\r\n"
            "            <tr>\r\n"
            "                <td><img src='/turtle_arrow.svg' onclick='send(\"L\")' class='turtle arrow rot-90'></td>\r\n"
            "                <td><img src='/turtle_arrow.svg' onclick='send(\"B\")' class='turtle arrow rot180'></td>\r\n"
            "                <td><img src='/turtle_arrow.svg' onclick='send(\"R\")' class='turtle arrow rot90'></td>\r\n"
            "            </tr>\r\n"
            "        </table>\r\n")


def getSimplePanel() -> str:
    return ("        <table class='simple panel'>\r\n"
            "            <tr>\r\n"
            "                <td></td>\r\n"
            "                <td><img src='/turtle_arrow.svg' onclick='send(1)' class='turtle arrow'></td>\r\n"
            "                <td></td>\r\n"
            "            </tr>\r\n"
            "            <tr>\r\n"
            "                <td><img src='/turtle_arrow.svg' onclick='send(128)' class='turtle arrow rot-90'></td>\r\n"
            "                <td><img src='/turtle_play.svg' onclick='send(64)' class='turtle play'></td>\r\n"
            "                <td><img src='/turtle_arrow.svg' onclick='send(16)' class='turtle arrow rot90'></td>\r\n"
            "            </tr>\r\n"
            "            <tr>\r\n"
            "                <td></td>\r\n"
            "                <td><img src='/turtle_arrow.svg' onclick='send(32)' class='turtle arrow rot180'></td>\r\n"
            "                <td></td>\r\n"
            "            </tr>\r\n"
            "            <tr>\r\n"
            "                <td colspan='3' style='height:100px;'></td>\r\n"
            "            </tr>\r\n"
            "            <tr>\r\n"
            "                <td><img src='/turtle_cross.svg' onclick='send(512)' class='turtle cross'></td>\r\n"
            "                <td><img src='/turtle_pause.svg' onclick='send(2)' class='turtle pause'></td>\r\n"
            "                <td><img src='/turtle_undo.svg' onclick='send(256)' class='turtle undo'></td>\r\n"
            "            </tr>\r\n"
            "        </table>\r\n")


def getProPanel() -> str:
    return ("        <table class='pro panel'>\r\n"
            "            <tr>\r\n"
            "                <td><img src='/turtle_arrow.svg' onclick='send(128)' class='turtle arrow rot-45'></td>\r\n"
            "                <td><img src='/turtle_arrow.svg' onclick='send(1)' class='turtle arrow'></td>\r\n"
            "                <td><img src='/turtle_arrow.svg' onclick='send(16)' class='turtle arrow rot45'></td>\r\n"
            "            </tr>\r\n"
            "            <tr>\r\n"
            "                <td><img src='/turtle_arrow.svg' onclick='send(128)' class='turtle arrow rot-90'></td>\r\n"
            "                <td><img src='/turtle_play.svg' onclick='send(64)' class='turtle play'></td>\r\n"
            "                <td><img src='/turtle_arrow.svg' onclick='send(16)' class='turtle arrow rot90'></td>\r\n"
            "            </tr>\r\n"
            "            <tr>\r\n"
            "                <td><img src='/turtle_pause.svg' onclick='send(2)' class='turtle pause'></td>\r\n"
            "                <td><img src='/turtle_arrow.svg' onclick='send(32)' class='turtle arrow rot180'></td>\r\n"
            "                <td><img src='/turtle_repeat.svg' onclick='send(4)' class='turtle repeat'></td>\r\n"
            "            </tr>\r\n"
            "            <tr>\r\n"
            "                <td><img src='/turtle_cross.svg' onclick='send(512)' class='turtle cross'></td>\r\n"
            "                <td><img src='/turtle_undo.svg' onclick='send(256)' class='turtle undo'></td>\r\n"
            "                <td><img src='/turtle_cross.svg' onclick='send(8)' class='turtle cross rot45'></td>\r\n"
            "            </tr>\r\n"
            "            <tr>\r\n"
            "                <td><img src='/turtle_f1.svg' onclick='send(6)' class='turtle f1'></td>\r\n"
            "                <td><img src='/turtle_f2.svg' onclick='send(10)' class='turtle f2'></td>\r\n"
            "                <td><img src='/turtle_f3.svg' onclick='send(12)' class='turtle f3'></td>\r\n"
            "            </tr>\r\n"
            "        </table>\r\n")


def getSettingsPanel() -> str:
    return ("        <ul class='links'>\r\n"
            "            <li>Settings</li>\r\n"
            "            <li><a href='_datetime'>Date & Time</a></li>\r\n"
            "            <li><a href=''></a></li>\r\n"
            "            <li><a href=''></a></li>\r\n"
            "        </ul>\r\n")


def getDateTimePanel() -> str:
    dt = config.datetime()
    return ("        <ul class='links'>\r\n"
            "            <li>Date & Time</li>\r\n"
            "            <li><table style='width: 100%; text-align: center;'><tr><td>{}. {:02d}. {:02d}.</td><td>{:02d} : {:02d} : {:02d}</td></tr></table></li>\r\n"
            "            <li><center><input type='date' id='date'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type='time' id='time'></center></li>\r\n"
            "            <li><a href='_datetime' onclick='send(1)'>Save</a></li>\r\n"
            "            <li><a href='_settings'>Back to settings</a></li>\r\n"
            "        </ul>\r\n").format(dt[0], dt[1], dt[2], dt[4], dt[5], dt[6])


_sender =  ("\r\n"
            "        <script>\r\n"
            "            function send(value) {{\r\n"
            "                let xhr = new XMLHttpRequest();\r\n"
            "                xhr.open('GET', '/command/{});\r\n"
            "                xhr.setRequestHeader('Content-Type', 'application/json');\r\n"
            "                xhr.send();\r\n"
            "            }}\r\n"
            "        </script>\r\n")


def getTurtleMoveSender() -> str:
    return _sender.format("DRIVE_' + value")


def getButtonPressSender() -> str:
    return _sender.format("PRESS_' + value")


def getDateTimeSender() -> str:
    return _sender.format("TIME_' + document.getElementById(\"date\").value +"
                          " \"_\" + document.getElementById(\"time\").value")


def linkSitePathToExistingPath(path: str, existingPath: str) -> None:
    title[path] = title.get(existingPath)
    parts[path] = parts.get(existingPath)


############
## CATALOGS


title = {
    "/_settings"    : "μBot Settings",
    "/_datetime"    : "μBot Settings - Date & Time",
    "/debug"        : "μBot Debug - Dashboard",
    "/_system"      : "μBot Debug - System info",
    "/_services"    : "μBot Debug - Service status",
    "/_ap"          : "μBot Debug - Access point",

    "/turtle"       : "μBot TurtleCode",
    "/drive"        : "μBot Drive",
    "/simple"       : "μBot Simple",
    "/pro"          : "μBot Professional"
}

parts = {
    "/_settings"    : (getSettingsPanel,),
    "/_datetime"    : (getDateTimePanel, getDateTimeSender),
    "/debug"        : (),
    "/_system"      : (getSystemPanel,),
    "/_services"    : (getServiceStatusPanel,),
    "/_ap"          : (getApPanel,),

    "/turtle"       : (getTurtlePanel,),

    "/drive"        : (getDrivePanel, getTurtleMoveSender),

    "/simple"       : (getSimplePanel, getButtonPressSender),

    "/pro"          : (getProPanel, getButtonPressSender)
}

debugPanels = {
    "System info"    : "/_system",
    "Service status" : "/_services",
    "Access point"   : "/_ap"
}

linkSitePathToExistingPath("/", "/simple")
linkSitePathToExistingPath("/professional", "/pro")
linkSitePathToExistingPath("/turtlecode", "/turtle")

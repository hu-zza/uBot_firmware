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


############
## CATALOGS

title = {
    "/debug"        : "μBot Debug - Dashboard",
    "/_system"      : "μBot Debug - System info",
    "/_services"    : "μBot Debug - Service status",
    "/_ap"          : "μBot Debug - Access point",
    "/turtle"       : "μBot TurtleCode"
}

parts = {
    "/debug"        : (),
    "/_system"      : (getSystemPanel,),
    "/_services"    : (getServiceStatusPanel,),
    "/_ap"          : (getApPanel,),
    "/turtle"       : (getTurtlePanel,)
}

debugPanels = {
    "System info"    : "/_system",
    "Service status" : "/_services",
    "Access point"   : "/_ap"
}

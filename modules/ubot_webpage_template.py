def getPage():
    return ("<!DOCTYPE html>\n"
            "<html>\n"
            "    <head>\n"
            "        <meta charset='utf-8'>\n"
            "        <title>{title}</title>\n"
            "        <style>\n"
            "{style}\n"
            "        </style>\n"
            "    </head>\n"
            "    <body>\n"
            "{body}\n"
            "    </body>\n"
            "</html>\n\n"
           )


def getStyle():
    return ("            .exceptions tr:nth-child(even) {background: #EEE}\n"
            "            .exceptions col:nth-child(1) {width: 40px;}\n"
            "            .exceptions col:nth-child(2) {width: 250px;}\n"
            "            .exceptions col:nth-child(3) {width: 500px;}\n"
            "            .panel{margin:auto; font-size:100px; text-align:center;}\n"
            "            .command{width:500px; height:750px;}\n"
            "            .drive{width:500px; height:500px;}\n"
           )


def getDebug():
    return ("        <h3>Commands</h3>\n"
            "            {commands}\n"
            "        <br><br><hr><hr>\n"
            "        <h3>Program</h3>\n"
            "    {program}\n"
            "        <br><br><hr><hr>\n"
            "        <h3>System</h3>\n"
            "            <strong>Memory:</strong> {freeMemory}%\n"
            "        <br><br><hr><hr>\n"
            "        <h3>Exceptions</h3>\n"
            "            {exceptions}\n")


def getDrive():
    return ("        <h3>Drive mode</h3>\n"
            "        <table class = 'drive panel'>\n"
            "            <tr>\n"
            "                <td>&#8598;</td><td>&#11014;</td><td>&#8599;</td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td>&#11013;</td><td></td><td>&#10145;</td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td></td><td>&#11015;</td><td></td>\n"
            "            </tr>\n"
            "        </table>\n")


def getCommand():
    return ("        <h3>Command mode</h3>\n"
            "        <table class = 'command panel'>\n"
            "            <tr>\n"
            "                <td>&#8598;</td><td>&#11014;</td><td>&#8599;</td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td>&#11013;</td><td>&#9199;</td><td>&#10145;</td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td>&#9208;</td><td>&#11015;</td><td>&#128257;</td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td>&#10060;</td><td>&#10133;</td><td>&#11178;</td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td>&#9312;</td><td>&#9313;</td><td>&#9314;</td>\n"
            "            </tr>\n"
            "        </table>\n")

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


def getArrow():
    return ("            .arrow {"
            "                    width: 100px;"
            "                    height: 100px;"
            "                    background-image: url(data:image/svg+xml;base64,PHN2ZyBpZD0ic3ZnIiB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHdpZHRoPSI0MDAiIGhlaWdodD0iNDAwIiB2aWV3Qm94PSIwLCAwLCA0MDAsNDAwIj48ZyBpZD0ic3ZnZyI+PHBhdGggaWQ9InBhdGgwIiBkPSJNMTg2LjY2NyAzLjcyOSBDIDE4NS4zODMgMy44ODAsMTgxLjMzMyA0LjMxOSwxNzcuNjY3IDQuNzA1IEMgNzEuNjA1IDE1Ljg1MSwtOC41ODkgMTE2LjgxMiw0LjUzNyAyMjIuNjY3IEMgMjQuODcyIDM4Ni42NDgsMjIzLjA0MCA0NTUuNzIzLDMzOS4zODEgMzM5LjM4MSBDIDQ1NC42MTcgMjI0LjE0NSwzODcuOTAyIDI3LjM4NywyMjYuMDAwIDQuOTk3IEMgMjE4LjczOCAzLjk5MywxOTEuNzk4IDMuMTI0LDE4Ni42NjcgMy43MjkgTTIwNi43NjMgNDMuMDAwIEMgMjEwLjM1MyA0OC4yNTgsMjMxLjIzMCA3Ny45NDksMjM4LjY0MCA4OC4zMzMgQyAyNDAuNzMzIDkxLjI2NywyNDMuNzcwIDk1LjU3NywyNDUuMzg5IDk3LjkxMSBDIDI0OS4wNzggMTAzLjIyOSwyNTEuMzA2IDEwNi4zOTcsMjc0LjYxMiAxMzkuNDU4IEMgMjg1LjAzMiAxNTQuMjM5LDI5Ny40NTAgMTcxLjg4MywzMDIuMjA5IDE3OC42NjcgQyAzMDYuOTY3IDE4NS40NTAsMzExLjYzNCAxOTIuMDE3LDMxMi41ODAgMTkzLjI1OSBDIDMxNC4xMjMgMTk1LjI4NywzMTQuMTY0IDE5NS40ODAsMzEyLjk4MyAxOTUuMTUwIEMgMzEyLjI1OSAxOTQuOTQ3LDMwOS4yNjcgMTk0LjI5MCwzMDYuMzMzIDE5My42OTAgQyAzMDMuNDAwIDE5My4wOTAsMjk2Ljk1MCAxOTEuNzM2LDI5Mi4wMDAgMTkwLjY4MCBDIDI4Ny4wNTAgMTg5LjYyNCwyNzguNTAwIDE4Ny44MjIsMjczLjAwMCAxODYuNjc2IEMgMjY3LjUwMCAxODUuNTMwLDI1OS41NjkgMTgzLjgxNywyNTUuMzc2IDE4Mi44NjkgQyAyMzYuMjY1IDE3OC41NDksMjM1LjkzMCAxNzkuMTEzLDIzOS42NzMgMjA5LjMzMyBDIDI0MC4xOTUgMjEzLjU1MCwyNDAuOTQ3IDIyMC40NTAsMjQxLjM0NCAyMjQuNjY3IEMgMjQyLjQ2OCAyMzYuNjIyLDI0OC43ODIgMjk3LjM1NywyNTEuMzkzIDMyMS4zMzMgQyAyNTIuMTMyIDMyOC4xMTcsMjUzLjE2MCAzMzguMzE3LDI1My42NzggMzQ0LjAwMCBDIDI1NC4xOTYgMzQ5LjY4MywyNTQuODIzIDM1Ni4zNTgsMjU1LjA3MyAzNTguODMzIEwgMjU1LjUyNiAzNjMuMzMzIDIwMi4zNDUgMzYzLjMzMyBMIDE0OS4xNjMgMzYzLjMzMyAxNDkuNTUxIDM2MC44MzMgQyAxNDkuNzY0IDM1OS40NTgsMTUwLjEyMyAzNTUuOTMzLDE1MC4zNDggMzUzLjAwMCBDIDE1MC41NzMgMzUwLjA2NywxNTEuNjIzIDMzOS41NjcsMTUyLjY4MCAzMjkuNjY3IEMgMTUzLjczOCAzMTkuNzY3LDE1NS4wNjQgMzA3LjAxNywxNTUuNjI4IDMwMS4zMzMgQyAxNTYuMTkyIDI5NS42NTAsMTU3Ljg1MiAyNzkuNjAwLDE1OS4zMTcgMjY1LjY2NyBDIDE2OC41NDQgMTc3LjkyNCwxNjcuODUzIDE4NS44OTIsMTY2LjQyMyAxODMuNzExIEMgMTY0LjkyMCAxODEuNDE1LDE2Mi4zOTMgMTgwLjQ5MywxNTkuMDMwIDE4MS4wMTEgQyAxNTYuMDIxIDE4MS40NzUsMTI3LjU3NSAxODcuMDY4LDEwMi43MzcgMTkyLjA4MCBDIDkzLjc5MiAxOTMuODg1LDg2LjM3NyAxOTUuMjY2LDg2LjI1OSAxOTUuMTQ4IEMgODYuMTQyIDE5NS4wMzEsOTAuOTkyIDE4OC4xOTksOTcuMDM4IDE3OS45NjcgQyAxMDMuMDgzIDE3MS43MzUsMTEwLjc5OCAxNjEuMjE1LDExNC4xODIgMTU2LjU5MCBDIDEyMC4zNDEgMTQ4LjE3MCwxMzMuMTYwIDEzMC43NTUsMTUwLjY4NiAxMDcuMDAwIEMgMTU1LjgyNSAxMDAuMDMzLDE2My40MjggODkuNjgzLDE2Ny41ODAgODQuMDAwIEMgMTcxLjczMyA3OC4zMTcsMTc5LjY5NCA2Ny41MTcsMTg1LjI3MSA2MC4wMDAgQyAxOTAuODQ5IDUyLjQ4MywxOTYuOTUyIDQ0LjE1NSwxOTguODMzIDQxLjQ5NCBDIDIwMC43MTUgMzguODMyLDIwMi40NDkgMzYuODgyLDIwMi42ODggMzcuMTYwIEMgMjAyLjkyNyAzNy40MzksMjA0Ljc2MSA0MC4wNjcsMjA2Ljc2MyA0My4wMDAgIiBzdHJva2U9Im5vbmUiIGZpbGw9IiMwMDAwMDAiIGZpbGwtcnVsZT0iZXZlbm9kZCI+PC9wYXRoPjwvZz48L3N2Zz4=);"
            "            }"
           )


def getPlay():
    return ("            .play {"
            "                    width: 100px;"
            "                    height: 100px;"
            "                    background-image: url(data:image/svg+xml;base64,PHN2ZyBpZD0ic3ZnIiB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHdpZHRoPSI0MDAiIGhlaWdodD0iNDAwIiB2aWV3Qm94PSIwLCAwLCA0MDAsNDAwIj48ZyBpZD0ic3ZnZyI+PHBhdGggaWQ9InBhdGgwIiBkPSJNMTg2LjY2NyAzLjcyOSBDIDE4NS4zODMgMy44ODAsMTgxLjMzMyA0LjMxOSwxNzcuNjY3IDQuNzA1IEMgNzEuNjA1IDE1Ljg1MSwtOC41ODkgMTE2LjgxMiw0LjUzNyAyMjIuNjY3IEMgMjQuODcyIDM4Ni42NDgsMjIzLjA0MCA0NTUuNzIzLDMzOS4zODEgMzM5LjM4MSBDIDQ1NC42MTcgMjI0LjE0NSwzODcuOTAyIDI3LjM4NywyMjYuMDAwIDQuOTk3IEMgMjE4LjczOCAzLjk5MywxOTEuNzk4IDMuMTI0LDE4Ni42NjcgMy43MjkgTTkwLjA4NSAxMDIuMzc3IEMgOTQuOTA5IDEwNC44MjEsOTguODkyIDEwOS4wNzUsMTAwLjU4MCAxMTMuNTg3IEwgMTAyLjAwMCAxMTcuMzgzIDEwMi4wMDAgMjAwLjA5NiBMIDEwMi4wMDAgMjgyLjgwOSA5OS45ODggMjg3LjAyNSBDIDkyLjE4NCAzMDMuMzc3LDY5LjQwMyAzMDMuMjYwLDYxLjIzNyAyODYuODI2IEwgNTkuNjY3IDI4My42NjcgNTkuNDkyIDIwMS4zNjQgQyA1OS4yOTggMTA5Ljc5Niw1OS4wNTkgMTE0Ljk0Nyw2My43OTcgMTA4LjQ5MSBDIDY5LjM5MCAxMDAuODY4LDgxLjUzNSA5OC4wNDQsOTAuMDg1IDEwMi4zNzcgTTE1OS45MDIgMTAwLjYzOSBDIDE2MS4xMjcgMTAwLjk5MCwxNjkuMjI1IDEwNS4xNjAsMTc3Ljg5OCAxMDkuOTA1IEMgMjAwLjgyOSAxMjIuNDUzLDIyMS42OTYgMTMzLjgzMSwyMjYuNjY3IDEzNi40OTcgQyAyMzcuMDIxIDE0Mi4wNTIsMjQ4LjcwNSAxNDguNDA2LDI1My4zMzMgMTUwLjk5OSBDIDI1Ni4wODMgMTUyLjUzOSwyNjAuNzMzIDE1NS4wODYsMjYzLjY2NyAxNTYuNjU5IEMgMjY2LjYwMCAxNTguMjMxLDI3My42NTAgMTYyLjA2OCwyNzkuMzMzIDE2NS4xODQgQyAyODUuMDE3IDE2OC4zMDEsMjkxLjE2NyAxNzEuNjYyLDI5My4wMDAgMTcyLjY1NCBDIDMyNi40NTggMTkwLjc1NiwzMzguODE0IDE5Ny42OTUsMzM5LjM0MSAxOTguNjgxIEMgMzQwLjQ4NSAyMDAuODE4LDMzOC4yNDQgMjAyLjI3NywzMTEuNjY3IDIxNi43MDIgQyAyOTcuMzY3IDIyNC40NjQsMjc3LjExNyAyMzUuNDczLDI2Ni42NjcgMjQxLjE2OSBDIDI1Ni4yMTcgMjQ2Ljg2NCwyMzkuMjY3IDI1Ni4wOTIsMjI5LjAwMCAyNjEuNjc3IEMgMjE4LjczMyAyNjcuMjYxLDE5OS4yMzMgMjc3LjkxMCwxODUuNjY3IDI4NS4zNDIgQyAxNTYuMTg5IDMwMS40OTAsMTUyLjgzMSAzMDIuMzM1LDE0OC44MzkgMjk0LjYwMiBDIDE0Ny4xOTcgMjkxLjQyMSwxNDguMDAyIDEwNS4xNzcsMTQ5LjY2NyAxMDMuMzEyIEMgMTUyLjI1NiAxMDAuNDEwLDE1NS44NDEgOTkuNDc0LDE1OS45MDIgMTAwLjYzOSAiIHN0cm9rZT0ibm9uZSIgZmlsbD0iIzAwMDAwMCIgZmlsbC1ydWxlPSJldmVub2RkIj48L3BhdGg+PC9nPjwvc3ZnPg==);"
            "            }"
           )


def getUndo():
    return ("            .undo {"
            "                    width: 100px;"
            "                    height: 100px;"
            "                    background-image: url(data:image/svg+xml;base64,PHN2ZyBpZD0ic3ZnIiB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHdpZHRoPSI0MDAiIGhlaWdodD0iNDAwIiB2aWV3Qm94PSIwLCAwLCA0MDAsNDAwIj48ZyBpZD0ic3ZnZyI+PHBhdGggaWQ9InBhdGgwIiBkPSJNMTg2LjY2NyAzLjcyOSBDIDE4NS4zODMgMy44ODAsMTgxLjMzMyA0LjMxOSwxNzcuNjY3IDQuNzA1IEMgNzEuNjA1IDE1Ljg1MSwtOC41ODkgMTE2LjgxMiw0LjUzNyAyMjIuNjY3IEMgMjQuODcyIDM4Ni42NDgsMjIzLjA0MCA0NTUuNzIzLDMzOS4zODEgMzM5LjM4MSBDIDQ1NC42MTcgMjI0LjE0NSwzODcuOTAyIDI3LjM4NywyMjYuMDAwIDQuOTk3IEMgMjE4LjczOCAzLjk5MywxOTEuNzk4IDMuMTI0LDE4Ni42NjcgMy43MjkgTTE4Mi42NjcgMzkuMjYyIEMgMTg5LjAxMCA0MS44OTksMTg4Ljk0NCA0MS41NDUsMTg5LjIxNiA3My45NTMgQyAxODkuMzQ3IDg5LjU2MiwxODkuNjUyIDEwMi41MTgsMTg5Ljg5NCAxMDIuNzQ1IEMgMTkwLjEzNiAxMDIuOTcxLDE5NC44MzMgMTAzLjc4OCwyMDAuMzMzIDEwNC41NjEgQyAyOTYuMTE2IDExOC4wMTYsMzU4LjM2MCAyMTAuNzExLDMzNC4yNTYgMzA0LjAwMCBDIDMzMC41MzMgMzE4LjQwOCwzMTguMjQ3IDM0Ni45OTksMzE3Ljk0MSAzNDEuOTY3IEMgMzEzLjgwNCAyNzMuOTUxLDI1OS4zNDkgMjE2LjQzMSwxOTMuODMzIDIxMC44NzQgTCAxODkuMzMzIDIxMC40OTIgMTg5LjI1NCAyMzIuNzQ2IEMgMTg5LjE0MyAyNjQuMTk2LDE4OC45OTQgMjY3LjI0MCwxODcuNDcxIDI2OS4yOTggQyAxODQuNDcyIDI3My4zNDksMTc5LjQxNiAyNzUuMDM5LDE3NS4yMTAgMjczLjM5NyBDIDE3MS45MzIgMjcyLjExNyw1Ny41MTkgMTc3LjAyMCw0NC41NTkgMTY0LjgwMyBDIDM1Ljk5NCAxNTYuNzI5LDM2Ljg1MSAxNTMuOTYyLDUxLjg5NyAxNDEuMTA2IEMgNzQuMjYwIDEyMS45OTgsMTQ3LjY1OCA2MC43NjcsMTY4LjE1NiA0NC4xMjAgQyAxNzUuNzc4IDM3LjkyOSwxNzcuODE4IDM3LjI0NiwxODIuNjY3IDM5LjI2MiAiIHN0cm9rZT0ibm9uZSIgZmlsbD0iIzAwMDAwMCIgZmlsbC1ydWxlPSJldmVub2RkIj48L3BhdGg+PC9nPjwvc3ZnPg==);"
            "            }"
           )


def getCross():
    return ("            .cross {"
            "                    width: 100px;"
            "                    height: 100px;"
            "                    background-image: url(data:image/svg+xml;base64,PHN2ZyBpZD0ic3ZnIiB2ZXJzaW9uPSIxLjEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHdpZHRoPSI0MDAiIGhlaWdodD0iNDAwIiB2aWV3Qm94PSIwLCAwLCA0MDAsNDAwIj48ZyBpZD0ic3ZnZyI+PHBhdGggaWQ9InBhdGgwIiBkPSJNMTg2LjY2NyAzLjcyOSBDIDE4NS4zODMgMy44ODAsMTgxLjMzMyA0LjMxOSwxNzcuNjY3IDQuNzA1IEMgNzEuNjA1IDE1Ljg1MSwtOC41ODkgMTE2LjgxMiw0LjUzNyAyMjIuNjY3IEMgMjQuODcyIDM4Ni42NDgsMjIzLjA0MCA0NTUuNzIzLDMzOS4zODEgMzM5LjM4MSBDIDQ1NC42MTcgMjI0LjE0NSwzODcuOTAyIDI3LjM4NywyMjYuMDAwIDQuOTk3IEMgMjE4LjczOCAzLjk5MywxOTEuNzk4IDMuMTI0LDE4Ni42NjcgMy43MjkgTTk4LjgwMSA2OS40MTYgQyAxMDYuNjMzIDcxLjA3OCwxMDYuMzk5IDcwLjg3MCwxNTQuMzMzIDExOC43MjEgTCAxOTkuNjY3IDE2My45NzUgMjQ1LjAwMCAxMTguNzI0IEMgMjkzLjUyMSA3MC4yOTEsMjkyLjc1MSA3MC45NjksMzAxLjIwMiA2OS4zMDYgQyAzMTcuMTA4IDY2LjE3NywzMzMuMDMxIDgyLjAxOCwzMzAuMDA3IDk3Ljk2NCBDIDMyOC41MDEgMTA1LjkwNSwzMjkuNDk3IDEwNC43ODAsMjgwLjgxNSAxNTMuNDk4IEwgMjM1LjAxOCAxOTkuMzI5IDI4MC40NDAgMjQ0LjgzMSBDIDMyNS4xNTggMjg5LjYyNywzMjcuMzQzIDI5Mi4wMDgsMzI5LjIxNiAyOTguMDAwIEMgMzM1LjU5MiAzMTguMzk0LDMxMy42MDUgMzM3LjE0NiwyOTQuNDU4IDMyNy42NDUgQyAyOTEuNzE1IDMyNi4yODQsMjgxLjYyNyAzMTYuNTY1LDI0NS42NjUgMjgwLjYzMSBDIDIyMC43MzEgMjU1LjcxNywyMDAuMDMxIDIzNS4zMzMsMTk5LjY2NyAyMzUuMzMzIEMgMTk5LjMwMiAyMzUuMzMzLDE3OC42MDMgMjU1LjcxNywxNTMuNjY4IDI4MC42MzEgQyAxMDUuMzIzIDMyOC45MzgsMTA1Ljg1MSAzMjguNDcxLDk3LjY3NiAzMzAuMTEzIEMgODAuOTE4IDMzMy40NzgsNjQuODcyIDMxNC43ODAsNzAuMTE4IDI5OC4wMDAgQyA3MS45OTEgMjkyLjAwOCw3NC4xNzUgMjg5LjYyNywxMTguODkzIDI0NC44MzEgTCAxNjQuMzE1IDE5OS4zMjkgMTE4LjUxOCAxNTMuNDk4IEMgNjkuODM2IDEwNC43ODAsNzAuODMyIDEwNS45MDUsNjkuMzI3IDk3Ljk2NCBDIDY2LjIyOSA4MS42MzAsODIuNDI2IDY1Ljk0Miw5OC44MDEgNjkuNDE2ICIgc3Ryb2tlPSJub25lIiBmaWxsPSIjMDAwMDAwIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjwvcGF0aD48L2c+PC9zdmc+);"
            "            }"
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

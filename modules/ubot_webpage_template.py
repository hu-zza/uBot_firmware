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
    return ("            svg {width: 100px; height: 100px;}\n"
            "            .exceptions tr:nth-child(even) {background: #EEE}\n"
            "            .exceptions col:nth-child(1) {width: 40px;}\n"
            "            .exceptions col:nth-child(2) {width: 250px;}\n"
            "            .exceptions col:nth-child(3) {width: 500px;}\n"
            "            .panel {margin:auto; font-size:100px; text-align:center;}\n"
            "            .command {width:500px; height:750px;}\n"
            "            .drive {width:500px; height:500px;}\n"
           )


def getTurtleSvg():
    return ("         <svg style='display:none' xmlns='http://www.w3.org/2000/svg'>\n"
            "             <defs>\n"
            "                 <symbol id='arrow' width='100' height='100' viewBox='0 0 400 400' xmlns:v='https://vecta.io/nano'>\n"
            "                     <path d='M186.667 3.729l-9 .976C71.605 15.851-8.589 116.812 4.537 222.667 24.872 386.648 223.04 455.723 339.381 339.381 454.617 224.145 387.902 27.387 226 4.997c-7.262-1.004-34.202-1.873-39.333-1.268M206.763 43l95.446 135.667 10.371 14.592c1.543 2.028 1.584 2.221.403 1.891-.724-.203-3.716-.86-6.65-1.46L292 190.68l-19-4.004-17.624-3.807c-19.111-4.32-19.446-3.756-15.703 26.464l1.671 15.334 10.049 96.666L253.678 344l1.395 14.833.453 4.5H149.163l.388-2.5c.213-1.375.572-4.9.797-7.833s1.275-13.433 2.332-23.333l6.637-64c9.227-87.743 8.536-79.775 7.106-81.956-1.503-2.296-4.03-3.218-7.393-2.7-3.009.464-31.455 6.057-56.293 11.069-8.945 1.805-16.36 3.186-16.478 3.068s4.733-6.949 10.779-15.181l17.144-23.377L150.686 107l16.894-23 17.691-24 13.562-18.506c1.882-2.662 3.616-4.612 3.855-4.334s2.073 2.907 4.075 5.84' fill-rule='evenodd'/>\n"
            "                 </symbol>\n"

            "                 <symbol id='play' width='100' height='100' viewBox='0 0 400 400' xmlns:v='https://vecta.io/nano'>\n"
            "                     <path d='M186.667 3.729l-9 .976C71.605 15.851-8.589 116.812 4.537 222.667 24.872 386.648 223.04 455.723 339.381 339.381 454.617 224.145 387.902 27.387 226 4.997c-7.262-1.004-34.202-1.873-39.333-1.268m-96.582 98.648c4.824 2.444 8.807 6.698 10.495 11.21l1.42 3.796v165.426l-2.012 4.216c-7.804 16.352-30.585 16.235-38.751-.199l-1.57-3.159-.175-82.303c-.194-91.568-.433-86.417 4.305-92.873 5.593-7.623 17.738-10.447 26.288-6.114m69.817-1.738c1.225.351 9.323 4.521 17.996 9.266L293 172.654c33.458 18.102 45.814 25.041 46.341 26.027 1.144 2.137-1.097 3.596-27.674 18.021l-45 24.467L229 261.677l-43.333 23.665c-29.478 16.148-32.836 16.993-36.828 9.26-1.642-3.181-.837-189.425.828-191.29 2.589-2.902 6.174-3.838 10.235-2.673' fill-rule='evenodd'/>\n"
            "                 </symbol>\n"

            "                 <symbol id='undo' width='100' height='100' viewBox='0 0 400 400' xmlns:v='https://vecta.io/nano'>\n"
            "                     <path d='M186.667 3.729l-9 .976C71.605 15.851-8.589 116.812 4.537 222.667 24.872 386.648 223.04 455.723 339.381 339.381 454.617 224.145 387.902 27.387 226 4.997c-7.262-1.004-34.202-1.873-39.333-1.268m-4 35.533c6.343 2.637 6.277 2.283 6.549 34.691.131 15.609.436 28.565.678 28.792s4.939 1.043 10.439 1.816C296.116 118.016 358.36 210.711 334.256 304c-3.723 14.408-16.009 42.999-16.315 37.967-4.137-68.016-58.592-125.536-124.108-131.093l-4.5-.382-.079 22.254c-.111 31.45-.26 34.494-1.783 36.552-2.999 4.051-8.055 5.741-12.261 4.099-3.278-1.28-117.691-96.377-130.651-108.594-8.565-8.074-7.708-10.841 7.338-23.697L168.156 44.12c7.622-6.191 9.662-6.874 14.511-4.858' fill-rule='evenodd'/>\n"
            "                 </symbol>\n"

            "                 <symbol id='cross' width='100' height='100' viewBox='0 0 400 400' xmlns:v='https://vecta.io/nano'>\n"
            "                     <path d='M186.667 3.729l-9 .976C71.605 15.851-8.589 116.812 4.537 222.667 24.872 386.648 223.04 455.723 339.381 339.381 454.617 224.145 387.902 27.387 226 4.997c-7.262-1.004-34.202-1.873-39.333-1.268M98.801 69.416c7.832 1.662 7.598 1.454 55.532 49.305l45.334 45.254L245 118.724c48.521-48.433 47.751-47.755 56.202-49.418 15.906-3.129 31.829 12.712 28.805 28.658-1.506 7.941-.51 6.816-49.192 55.534l-45.797 45.831 45.422 45.502c44.718 44.796 46.903 47.177 48.776 53.169 6.376 20.394-15.611 39.146-34.758 29.645-2.743-1.361-12.831-11.08-48.793-47.014l-45.998-45.298c-.365 0-21.064 20.384-45.999 45.298-48.345 48.307-47.817 47.84-55.992 49.482C80.918 333.478 64.872 314.78 70.118 298c1.873-5.992 4.057-8.373 48.775-53.169l45.422-45.502-45.797-45.831c-48.682-48.718-47.686-47.593-49.191-55.534-3.098-16.334 13.099-32.022 29.474-28.548' fill-rule='evenodd'/>\n"
            "                 </symbol>\n"
            "             </defs>\n"
            "         </svg>\n"
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
            "            {exceptions}\n"
           )


def getDrive():
    return ("        <h3>Drive mode</h3>\n"
            "        <table class = 'drive panel'>\n"
            "            <tr>\n"
            "                <td><svg style='rotate: -45deg;'><use xlink:href='#arrow'></use></svg></td>\n"
            "                <td><svg><use xlink:href='#arrow'></use></svg></td>\n"
            "                <td><svg style='rotate: 45deg;'><use xlink:href='#arrow'></use></svg></td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td><svg style='rotate: -90deg;'><use xlink:href='#arrow'></use></svg></td>\n"
            "                <td></td>\n"
            "                <td><svg style='rotate: 90deg;'><use xlink:href='#arrow'></use></svg></td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td></td>\n"
            "                <td><svg style='rotate: 180deg;'><use xlink:href='#arrow'></use></svg></td>\n"
            "                <td></td>\n"
            "            </tr>\n"
            "        </table>\n"
           )


def getCommand():
    return ("        <h3>Command mode</h3>\n"
            "        <table class = 'drive panel'>\n"
            "            <tr>\n"
            "                <td><svg style='rotate: -45deg;'><use xlink:href='#arrow'></use></svg></td>\n"
            "                <td><svg><use xlink:href='#arrow'></use></svg></td>\n"
            "                <td><svg style='rotate: 45deg;'><use xlink:href='#arrow'></use></svg></td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td><svg style='rotate: -90deg;'><use xlink:href='#arrow'></use></svg></td>\n"
            "                <td><svg><use xlink:href='#play'></use></svg></td>\n"
            "                <td><svg style='rotate: 90deg;'><use xlink:href='#arrow'></use></svg></td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td>&#9208;</td>\n"
            "                <td><svg style='rotate: 180deg;'><use xlink:href='#arrow'></use></svg></td>\n"
            "                <td>&#128257;</td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td><svg><use xlink:href='#cross'></use></svg></td>\n"
            "                <td><svg style='rotate: 90deg;'><use xlink:href='#cross'></use></svg></td>\n"
            "                <td><svg><use xlink:href='#undo'></use></svg></td>\n"
            "            </tr>\n"
            "            <tr>\n"
            "                <td>&#9312;</td>\n"
            "                <td>&#9313;</td>\n"
            "                <td>&#9314;</td>\n"
            "            </tr>\n"
            "        </table>\n"
           )

def getStyle():
    return ("tr:nth-child(even) {background: #EEE}"
            ".exceptions col:nth-child(1) {width: 40px;}"
            ".exceptions col:nth-child(2) {width: 250px;}"
            ".exceptions col:nth-child(3) {width: 500px;}")

def getStats():
    return ("<h3>Commands</h3>"
            "{commands}"
            "<br><br><hr><hr>"
            "<h3>Program</h3>"
            "{program}"
            "<br><br><hr><hr>"
            "<h3>System</h3>"
            "<strong>Memory:</strong> {freeMemory}%"
            "<br><br><hr><hr>"
            "<h3>Exceptions</h3>"
            "{exceptions}")

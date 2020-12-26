def getWebPage(method, path, length, type, body):
    if length < 1:
        type = '-'
        body = '-'

    length = str(length)

    return """<html>
    <head><title>ESP Web Server</title></head>
    <body><table>
    <tr><td>Method: </td><td>""" + method + """</td></tr>
    <tr><td>Path: </td><td>"""   + path   + """</td></tr>
    <tr><td>Length: </td><td>""" + length + """</td></tr>
    <tr><td>Type: </td><td>"""   + type   + """</td></tr>
    <tr><td>Body: </td><td>"""   + body   + """</td></tr>
    </table></body>
    </html>"""

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    method = ''
    path = ''
    contentLength = 0
    contentType = ''
    body = ''

    connection, address = s.accept()
    requestFile         = connection.makefile('rwb', 0)

    while True:
        line = requestFile.readline()

        if not line:
            break
        elif line == b'\r\n':
            if 0 < contentLength:
                body = str(requestFile.read(contentLength), 'utf-8')
            break

        line = str(line, 'utf-8')

        if method == '':
            firstSpace = line.find(' ')
            pathEnd    = line.find(' HTTP')

            method = line[0:firstSpace]
            path   = line[firstSpace+1:pathEnd]

            #until payload parsing
            ledOn  = line.find(' /?led=on')
            ledOff = line.find(' /?led=off')

            if ledOn == firstSpace:
                led.value(0)
            elif ledOff == firstSpace:
                led.value(1)

        if 0 <= line.find('Content-Length:'):
            contentLength = int(line[15:].strip())

        if 0 <= line.find('Content-Type:'):
            contentType = line[13:].strip()

    connection.send('HTTP/1.1 200 OK\n')
    connection.send('Content-Type: text/html\n')
    connection.send('Connection: close\n\n')
    connection.sendall(getWebPage(method, path, contentLength, contentType, body))
    connection.close()

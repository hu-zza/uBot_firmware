def getWebPage(method, path, body):
    return """<html>
    <head><title>ESP Web Server</title></head>
    <body><table>
    <tr><td>Method:&nbsp;</td><td>""" + method + """</td></tr>
    <tr><td>Path:</td><td>""" + path + """</td></tr>
    <tr><td>Body:</td><td>""" + body + """</td></tr>
    </table></body>
    </html>"""

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    method = ''
    path = ''
    contentLength = 0 #TODO..... 
    body = ''

    connection, address = s.accept()
    print('Got a connection from %s' % str(address))

    requestFile = connection.makefile('rwb', 0)
    while True:
        line = requestFile.readline()
        if not line:
            break
        elif line == b'\r\n':
            if method == 'POST':
                body = str(requestFile.readline(), 'utf-8')
                print(body)
            break

        line = str(line, 'utf-8')
        print(line)

        if method == '':
            firstSpace = line.find(' ')
            pathEnd = line.find(' HTTP')

            method = line[0:firstSpace]
            path = line[firstSpace+1:pathEnd]


        ledOn = line.find(' /?led=on')
        ledOff = line.find(' /?led=off')

        if ledOn == firstSpace:
            print('LED ON')
            led.value(0)
        elif ledOff == firstSpace:
            print('LED OFF')
            led.value(1)

    response = getWebPage(method, path, body)
    connection.send('HTTP/1.1 200 OK\n')
    connection.send('Content-Type: text/html\n')
    connection.send('Connection: close\n\n')
    connection.sendall(response)
    connection.close()

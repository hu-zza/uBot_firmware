def getWebPage(method, path, command, request):
    html = """<html><head> <title>ESP Test Server</title> <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
    h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none;
    border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
    .button2{background-color: #4286f4;}</style></head><body> <h1>ESP Test Server</h1>
    <p>Method: <strong>"""  + method  + """</strong></p>
    <p>Path: <strong>"""    + path    + """</strong></p>
    <p>Command: <strong>""" + command + """</strong></p>
    <p>Request: <strong>""" + request + """</strong></p></body></html>"""
    return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    method = ''
    path = ''
    command = ''

    connection, address = s.accept()
    print('Got a connection from %s' % str(address))

    while True:
        line = connection.readline()
        if not line or line == b'\r\n' or line == b'':
            break

        if method == '':
            firstSpace = line.find(' ')
            pathEnd = request.find(' HTTP')

            method = str(line[0:firstSpace)])
            path = str(line[firstSpace+1:pathEnd])

        if str(line[0:4]) == 'uBot':
            command = str(line)

    ledOn = request.find(' /?led=on')
    ledOff = request.find(' /?led=off')

    if ledOn == firstSpace:
        print('LED ON')
        led.value(1)
    elif ledOff == firstSpace:
        print('LED OFF')
        led.value(0)

    response = getWebPage(method, path, command, request)
    connection.send('HTTP/1.1 200 OK\n')
    connection.send('Content-Type: text/html\n')
    connection.send('Connection: close\n\n')
    connection.sendall(response)
    connection.close()

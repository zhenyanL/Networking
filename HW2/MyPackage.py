import socket




def receive(conn, bufsize=1024):
    res = b''
    temp = conn.recv(bufsize)
    while len(temp) > 0:
        res += temp
        temp = conn.recv(bufsize)
    return res

def generateReq(method, url, version,headers,body):
    request = b''
    request += b' '.join((method,url,version)) + b'\r\n'
    for key in headers:
        request += key + b': ' + headers[key] + b'\r\n'
    request += b''.join(body)
    request += b'\r\n'
    return request




def sendByMyProxy(request):
    if len(request) == 0:
        return b''
    first_line = request.split(b'\n')[0]
    if first_line[-1] == 13: 
        delimiter =  b'\r\n'
    else:
        delimiter =  b'\n'
    content = request.split(delimiter)
    seg = content.index(b'')
    method,url,version = content[0].split(b' ')

    if method != b'GET':
        return  b' only get request'

    delimiter2 = b': '
    headers = {}
    for line in content:
        if len(line.split(delimiter2, 1)) > 1:
            headers[line.split(delimiter2,1)[0]] = line.split(delimiter2,1)[1]

    body = content[seg + 1:]
    headers[b'Connection'] = b'close'

    newReq = generateReq(method, url, version, headers, body)
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((headers[b'Host'], 80))
    conn.sendall(newReq)
    response = receive(conn)
    conn.close()

    with open('logFile.txt', 'a') as file:
         file.write(url.decode('ascii') + "\n")
    return response
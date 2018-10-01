

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = '10.142.0.3'
server_port = 8181
s.connect((server_ip, server_port))
print('Connected to server ', server_ip, ':', server_port)
# size read each time
BUF_SIZE = 16

# test cases
test = [
    [2, 2, '15', 1, '5'],
    [2, 9, '3+12*14-3', 20, '1+12/3+4-5+7-6*31+12']
]


# format request from test case
def getRequest(data):
    request = b''
    # change to bytes representation, [count,len1,expression1,len2,expression2,....]
    request += data[0].to_bytes(2, 'big')
    i = 1
    while i < len(data):
        request += data[i].to_bytes(2, 'big')
        request += data[i + 1].encode('utf-8')
        i = i+2
    return request

# receive data from server
def received(conn, buf_size):
    res = b''
    while True:
        data = conn.recv(buf_size)
        res += part
        if len(data) < buf_size:
            break
    return res
# decode data received from server
def decode(stringBack):
    num = int.from_bytes(stringBack[0:2], 'big')
    index = 2
    result = []
    result.append(num)

    for i in range(num):
        lenStr = int.from_bytes(stringBack[index: index + 2], 'big')
        strr = stringBack[index + 2: index + 2 + lenStr].decode()
        result.append(lenStr)
        result.append(strr)
        index += 2 + lenStr

    return result
# encode all testcase, send to server, receive result, and decode result
for i in range(len(test)):
    print('sent:', test[i])
    request = getRequest(test[i])
    s.sendall(request)
    response = received(s, BUF_SIZE)
    result = decode(response)
    print('result:', result)

# close connection
s.close()

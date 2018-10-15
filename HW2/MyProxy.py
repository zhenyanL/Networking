import socket
import _thread
import sys
import MyPackage

hostPort = None
instruction = 'command line instruction: python3 MyProxy.py -p port_number'

if len(sys.argv) > 2 and sys.argv[1] == '-p':
    try:
        hostPort = int(sys.argv[2])
    except ValueError:
        print('invalid port number, see instruction:'+instruction)
        quit()
else:
    print(instruction)
    quit()

hostName = socket.gethostname()
hostIp = socket.gethostbyname(hostName)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((hostIp, hostPort))
s.listen()

def handler(conn, addr):
    request = conn.recv(65535)
    print('Server connected by', addr)
    res = MyPackage.sendByMyProxy(request)
    conn.sendall(res)
    conn.close()


while True:
    print('start')
    _thread.start_new_thread(handler, s.accept())
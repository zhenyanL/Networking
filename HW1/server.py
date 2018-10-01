import socket
import _thread

# size receive each time
BUF_SIZE=16
host_name = socket.gethostname()
print('host name:', host_name)
host_ip = socket.gethostbyname(host_name)
host_port = 8181
print(host_ip, ':', host_port)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host_ip, host_port))
s.listen()

# receive data from client
def receiveReq(conn, buf_size):
    request = b''
    # loop until no data comes in
    while True:
        data = conn.recv(buf_size)
        request += data
        if len(data) < buf_size:
            break
    return request

# get result of all expression
def getResult(request):
	result = b''
	# first two bytes 
	number = int.from_bytes(request[0:2],'big')
	result += number.to_bytes(2,'big')
	index = 2
	for i in range(number):
		# len of following expression
		strLen = int.from_bytes(request[index:index+2],'big')
		# expression
		expression = request[index+2:index+2+strLen].decode()
		# calculate expression
		ans = calculate(expression)
		print('result:',ans)
		result += len(ans).to_bytes(2,'big')
		result += ans.encode()
		index += 2+strLen
	return result

# calculate expression
def calculate(expression):
    num = 0
    stack = []
    sign = "+"
    expression += 'E'
    for i in range(len(expression)):
    	# get number
        if expression[i].isdigit():
            num = 10 * num + int(expression[i])
        elif expression[i] == ' ':
        	continue
        else:
        	# if it's operators, do calculation
        	if sign == '+':
        		stack.append(num)
        	elif sign == '-':
        		stack.append(-num)
        	elif sign == '*':
        		stack.append(stack.pop()*num)
        	else:
        		stack.append(int(stack.pop()/num))
        	sign = expression[i]
        	# reset num to 0
        	num = 0
    # result is the sum of all element in stack
    return str(sum(stack))

def helper(conn,address):
	print(address,':connected')
	while True:
		request = receiveReq(conn, BUF_SIZE)
		if not request:
			break
		print('Server received:', request)
		response = getResult(request)
		conn.sendall(response)
	conn.close()


print('Server started successfully')

# server listen to client to connect supporting multi-threads
while True:
  _thread.start_new_thread(helper, s.accept())

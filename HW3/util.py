import dummy
import gbn
import ss
import struct


def get_transport_layer_by_name(name, local_port, remote_port, msg_handler):
  assert name == 'dummy' or name == 'ss' or name == 'gbn'
  if name == 'dummy':
    return dummy.DummyTransportLayer(local_port, remote_port, msg_handler)
  if name == 'ss':
    return ss.StopAndWait(local_port, remote_port, msg_handler)
  if name == 'gbn':
    return gbn.GoBackN(local_port, remote_port, msg_handler)


def packetMessage(msg_type, seq, msg):
  type_string = encodeInt16(msg_type)
  seq_string = encodeInt16(seq)
  check_sum = getCheckSum(type_string + seq_string + msg)
  check_sum_string = encodeInt16(check_sum)
  packed_msg = type_string + seq_string + check_sum_string + msg
  return packed_msg
  
def getCheckSum(msg):
  asc_num = [ord(c) for c in msg]    
  if len(asc_num)%2 > 0 : asc_num.append(0)
  check_sum = 0
  for d in range(0,len(asc_num)-1, 2):
    check_sum += asc_num[d]*256 + asc_num[d+1] 
  return check_sum & 0x7fff
  
def isOriginal(packet):
  type_string = packet[:2]
  seq_string = packet[2:4]
  check_sum_string = packet[4:6]
  data = packet[6:]
  msg_to_check = type_string + seq_string + data
  if (check_sum_string == encodeInt16(getCheckSum(msg_to_check))):
    return True
  return False
  
def getSeq(packet):
  seq_string = packet[2:4]
  return decodeInt16(seq_string)
  
def getType(packet):
  type_string = packet[:2]
  return decodeInt16(type_string)


def getMessage(packet):
  return packet[6:]

# Encode a short int to byte code using network endianess.
#
# x: int
# return: string (of length 2)
def encodeInt16(x):
  return struct.pack('!h', x)
  
  
# Decode a short int from its byte encoding.
#
# x: byte encoding of int (of length 2)
# return: int
def decodeInt16(x):
  return struct.unpack('!h', x)[0]
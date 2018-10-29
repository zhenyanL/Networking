# Usage: python file_receiver.py [dummy|ss|gbn] [file_name]
import config
import util
import functools
import os.path
import sys
import time

# def msg_handler(file_handle, msg):
#   # # print("msg_handler in file_receiver:"+msg)
#   # # file_handle.write("????????")
#   # file_handle.write(bytes.decode(msg))
#   # # file_handle.write("???????")
#   file_handle.write(msg)
#   file_handle.close()
#    # if msg is None:
#    #  file_handle.close()
#    # else:

def msg_handler(file_name, msg):
  file_handle = open(file_name,'a')
  file_handle.write(msg)
  # file_handle.write(msg)
  file_handle.close()

    


if __name__ == '__main__':
  if len(sys.argv) != 3:
    print('Usage: python file_receiver.py [dummy|ss|gbn] [file_name]')
    sys.exit(1)

  transport_layer = None
  transport_layer_name = sys.argv[1]
  file_name = sys.argv[2]
  assert not os.path.exists(file_name)
  file_handle = None
  try:
    file_handle = open(file_name, 'w')
    # file_handle.write("?????????begine")
    # testfunc = functools.partial(msg_handler,file_handle)
    # testfunc("fjdskljflkadsjflkda")

    # transport_layer = util.get_transport_layer_by_name(
    #     transport_layer_name,
    #     config.RECEIVER_LISTEN_PORT,
    #     config.SENDER_LISTEN_PORT,
    #     functools.partial(msg_handler, file_handle))
    transport_layer = util.get_transport_layer_by_name(
        transport_layer_name,
        config.RECEIVER_LISTEN_PORT,
        config.SENDER_LISTEN_PORT,
        functools.partial(msg_handler, file_name))
    while True:
      time.sleep(1)
  finally:
    if file_handle:
      file_handle.close()
    if transport_layer:
      transport_layer.shutdown()

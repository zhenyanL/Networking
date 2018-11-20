import os.path
import socket
import table
import threading
import util
import collections
import graph

_CONFIG_UPDATE_INTERVAL_SEC = 5

_MAX_UPDATE_MSG_SIZE = 1024
_BASE_ID = 8000

def _ToPort(router_id):
  return _BASE_ID + router_id

def _ToRouterId(port):
  return port - _BASE_ID


class Router:
  def __init__(self, config_filename):
    # ForwardingTable has 3 columns (DestinationId,NextHop,Cost). It's
    # threadsafe.
    self._forwarding_table = table.ForwardingTable()
    # Config file has router_id, neighbors, and link cost to reach
    # them.
    self._config_filename = config_filename
    self._router_id = None
    # Socket used to send/recv update messages (using UDP).
    self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.messages = collections.deque(maxlen = 32)
    self.threadForReceiving = threading.Thread(target = self.readMessages)


  def start(self):
    # Start a periodic closure to update config.
    self._config_updater = util.PeriodicClosure(
        self.load_config, _CONFIG_UPDATE_INTERVAL_SEC)
    self._config_updater.start()
    # TODO: init and start other threads.
    self.runningStatus = True
    self.threadForReceiving.start()
    while True: pass


  def stop(self):
    if self._config_updater:
      self._config_updater.stop()
    # TODO: clean up other threads.
    self.runningStatus = False
    self.threadForReceiving.join(1)

  def send_out_update_messages(self, entries):
    msg = bytearray()
    entry_count = len(entries)
    msg.extend(entry_count.to_bytes(2, byteorder = 'big'))
    for (dest, next_hop, cost) in entries:
      msg.extend(dest.to_bytes(2, byteorder = 'big'))
      msg.extend(cost.to_bytes(2, byteorder = 'big'))
    
    # for (dest, next_hop, cost) in entries:
    #   print("Sending update msg to router id: ", dest)
    #   self._socket.sendto(msg, ('localhost', _ToPort(dest)))


  def load_config(self):
    assert os.path.isfile(self._config_filename)
    with open(self._config_filename, 'r') as f:
      router_id = int(f.readline().strip())
      # Only set router_id when first initialize.
      if not self._router_id:
        self._socket.bind(('localhost', _ToPort(router_id)))
        self._router_id = router_id
      # TODO: read and update neighbor link cost info.
      lines = f.readlines()

      draw = []
      for line in lines:
        destination,cost = line.strip().split(",")
        draw.append([int(self._router_id),int(destination),int(cost)])

      while len(self.messages) > 0:
        (source,destination,cost) = self.messages.popleft()
        draw.append([int(source),int(destination),int(cost)])

      dist = {}
      pre = {}
      for u,v,cost in draw:
        dist[u] = float('inf')
        dist[v] = float('inf')
      dist[self._router_id] = 0

      for i in range(len(dist)-1):
        for u,v,cost in draw:
          if dist[u] != float('inf') and dist[u] + cost < dist[v]:
            dist[v] = dist[u] + cost
            pre[v] = u

      res = [(self._router_id,self._router_id,0)]
      for dest in dist:
        nextStep = dest
        while nextStep in pre and pre[nextStep] != self._router_id:
          nextStep = pre[nextStep]
        if nextStep in pre:
          res.append((dest, nextStep, dist[dest]))
      self._forwarding_table.reset(res)
      # print("current table")
      print(self._forwarding_table.snapshot())

      message = bytearray()
      cnt = len(res)
      message.extend(cnt.to_bytes(2,byteorder='big'))
      for(dest,nextStep,cost) in res:
        message.extend(dest.to_bytes(2, byteorder = 'big'))
        message.extend(cost.to_bytes(2, byteorder = 'big'))

      for(dest,nextStep,cost) in res:
        # print("send message to:", dest)
        self._socket.sendto(message,('localhost',_ToPort(dest)))

  def readMessages(self):
    bufSize = 4096
    while self.runningStatus:
      (data,addr) = self._socket.recvfrom(bufSize)
      (ip,port) = addr
      cnt = int.from_bytes(data[0:2],byteorder='big')
      i = 0
      while i < cnt:
        offset = 4*i+2
        destId = int.from_bytes(data[offset:offset+2], byteorder = 'big')
        offset += 2
        cost = int.from_bytes(data[offset:offset+2], byteorder = 'big')
        self.messages.append((_ToRouterId(port), destId, cost))
        i += 1



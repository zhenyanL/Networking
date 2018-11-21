import os.path
import socket
import table
import util
import struct
import threading

_CONFIG_UPDATE_INTERVAL_SEC = 5

_MAX_UPDATE_MSG_SIZE = 1024
_BASE_ID = 8000


def _ToPort(router_id):
    return _BASE_ID + router_id


def _ToRouterId(port):
    return port - _BASE_ID




class Router:
    def __init__(self, config_filename):
        
        self._forwarding_table = table.ForwardingTable()
        
        self._config_filename = config_filename
        self._router_id = None
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.distance = []
        self.neighbors = {} 
        self.messagesQueue = {} 
        self.threadForReceiving = threading.Thread(target = self.readMessages)

    def start(self):
        self._config_updater = util.PeriodicClosure(self.load_config, _CONFIG_UPDATE_INTERVAL_SEC)
        self._config_updater.start()

        self.runningStatus = True
        self.threadForReceiving.start()
        while True: pass


    def stop(self):
        if self._config_updater:
            self._config_updater.stop()
        self.runningStatus = False
        self.threadForReceiving.join(1)


    def load_config(self):
        assert os.path.isfile(self._config_filename)
        with open(self._config_filename, 'r') as f:
            firstTime = False
            router_id = int(f.readline().strip())
            temp = [(router_id, router_id, 0)]
            if not self._router_id:
                firstTime = True
                self._socket.bind(('localhost', _ToPort(router_id)))
                self._router_id = router_id

            for line in f.readlines():
                neighbor,cost = line.strip().split(",")
                self.neighbors[int(neighbor)] = int(cost)
                if firstTime:
                    temp.append(( int(neighbor), int(neighbor), int(cost)))
                    self._forwarding_table.reset(temp)

            self.distance = temp
        self.sendMessage()


    def sendMessage(self):
        msg = bytearray()
        entry_count = self._forwarding_table.size()
        msg.extend(entry_count.to_bytes(2, byteorder = 'big'))

        for neighborId, nextId, cost in self._forwarding_table.snapshot():
            msg.extend(neighborId.to_bytes(2, byteorder = 'big'))
            msg.extend(cost.to_bytes(2, byteorder = 'big'))
            
        for neighbor in self.neighbors:
            self._socket.sendto(msg, ('localhost', _ToPort(neighbor)))
        print(self._forwarding_table.snapshot())

        

    def readMessages(self):
        bufSize = 4096
        while self.runningStatus:
          (data,addr) = self._socket.recvfrom(bufSize)
          (ip,port) = addr
          neighbor = _ToRouterId(port)

          res = []
          cnt = struct.unpack('!H', data[:2])[0]
          i = 2
          for _ in range(cnt):
            dest_id = struct.unpack('!H', data[i:i+2])[0]
            cost = struct.unpack('!H', data[i+2:i+4])[0]
            res.append((dest_id, cost))
            i += 4
          self.messagesQueue[neighbor] = res
          self.BellmanFord()    

    def BellmanFord(self):
        flag = False
        for neighbor, temp in self.messagesQueue.items():
            for destCost in temp:
                change = False
                dest, cost = destCost
                cost2 = self.neighbors[neighbor] + cost
                arr = (dest, neighbor, cost2)

                for i in range(len(self.distance)):
                    if self.distance[i][0] == dest:
                        change = True
                        prevCost = self.distance[i][2]
                        if cost2 < prevCost:
                            flag = True
                            self.distance[i] = arr
                if not change:
                    flag = True
                    self.distance.append(arr)
        if flag:
            self._forwarding_table.reset(self.distance)
            self.sendMessage()

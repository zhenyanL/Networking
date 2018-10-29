import udt
import util
import config
import time


# Go-Back-N reliable transport protocol.
class GoBackN:
  # "msg_handler" is used to deliver messages to application layer
  # when it's ready.
  def __init__(self, local_port, remote_port, msg_handler):
    self.network_layer = udt.NetworkLayer(local_port, remote_port, self)
    self.msg_handler = msg_handler
    self.packets = []
    self.startTime = 0
    self.seqExpected = 0
    self.seqBase = 0
    self.seqNext = 0
    

  # "send" is called by application. Return true on success, false
  # otherwise.
  def send(self, msg):
    # TODO: impl protocol to send packet from application layer.
    # call self.network_layer.send() to send to network layer.
    if self.seqNext < self.seqBase + config.WINDOWN_SIZE:
      sendPacket = util.packetMessage(config.MSG_TYPE_DATA, self.seqNext, msg)
      self.packets.append(sendPacket)
      self.network_layer.send(sendPacket)
      if (self.seqBase == self.seqNext):
        self.startTime = time.time()
      self.seqNext += 1
      return True

    else:
      if time.time() > self.startTime + (config.TIMEOUT_MSEC / 1000.0):
        self.startTime = time.time()
        for i in range(self.seqBase, self.seqNext):
          print("packet resend: ", i)
          self.network_layer.send(self.packets[i])
      return False


  # "handler" to be called by network layer when packet is ready.
  def handle_arrival_msg(self):
    packet = self.network_layer.recv()
    # TODO: impl protocol to handle arrived packet from network layer.
    # call self.msg_handler() to deliver to application layer.
    packetAck = util.packetMessage(config.MSG_TYPE_ACK, self.seqExpected - 1, "Random stuff.")
    packetType = util.getType(packet)
    if packetType == config.MSG_TYPE_DATA:
      packet_seq = util.getSeq(packet)
      if util.isOriginal(packet) and self.seqExpected == packet_seq :
        msg = util.getMessage(packet)
        # print("msg_handler:"+msg)
        self.msg_handler(msg)
        packetAck = util.packetMessage(config.MSG_TYPE_ACK, self.seqExpected, "OK")
        self.network_layer.send(packetAck)
        self.seqExpected += 1
        return
      self.network_layer.send(packetAck)
      
    elif packetType == config.MSG_TYPE_ACK :
          if util.isOriginal(packet):
            self.seqBase = util.getSeq(packet) + 1
            if self.seqBase == self.seqNext:
              self.startTime = 0
            else:
              self.startTime = time.time()

  # Cleanup resources.
  def shutdown(self):
    # TODO: cleanup anything else you may have when implementing this
    # class.
    self.network_layer.shutdown()

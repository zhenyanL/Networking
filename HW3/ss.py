import udt
import util
import config
import time


# Stop-And-Wait reliable transport protocol.
class StopAndWait:
  # "msg_handler" is used to deliver messages to application layer
  # when it's ready.
  def __init__(self, local_port, remote_port, msg_handler):
    self.network_layer = udt.NetworkLayer(local_port, remote_port, self)
    self.msg_handler = msg_handler
    # the sequence sent
    self.seq = config.MSG_SEQ_ONE
    # the sequence acked by receiver
    self.seqAck = config.MSG_SEQ_ONE
    
  # "send" is called by application. Return true on success, false
  # otherwise.
  def send(self, msg):
    # TODO: impl protocol to send packet from application layer.
    # call self.network_layer.send() to send to network layer.
    self.seq ^= 1             
    packedMessage = util.packetMessage(config.MSG_TYPE_DATA, self.seq, msg)
    self.network_layer.send(packedMessage)
    start_time = time.time()
    while self.seq != self.seqAck:
      if time.time() > start_time + (config.TIMEOUT_MSEC / 1000.0):
        print("packet seq resend: ", self.seq)
        self.network_layer.send(packedMessage)
        start_time = time.time()
    return True

  # "handler" to be called by network layer when packet is ready.
  def handle_arrival_msg(self):
    packet = self.network_layer.recv()
    # TODO: impl protocol to handle arrived packet from network layer.
    # call self.msg_handler() to deliver to application layer.
    packetType = util.getType(packet)
    if packetType == config.MSG_TYPE_DATA:
      seqExpected = self.seqAck ^ 1
      if not util.isOriginal(packet) or seqExpected != util.getSeq(packet):
        print("Packet Recieved: ", repr(packet))
        ackPacket = util.packetMessage(config.MSG_TYPE_ACK, self.seqAck, "Recieve wrong packet.")
        self.network_layer.send(ackPacket)
        return
      self.seqAck ^= 1
      ackPacket = util.packetMessage(config.MSG_TYPE_ACK, self.seqAck, "Recieve right packet")
      msg = util.getMessage(packet)
      self.msg_handler(msg)
      self.network_layer.send(ackPacket)
      
    elif packetType == config.MSG_TYPE_ACK:
      packetSeq = util.getSeq(packet)
      expectSeqAck = self.seq
      if not util.isOriginal(packet) or expectSeqAck != packetSeq:
        return
      self.seqAck ^= 1
      
      
  # Cleanup resources.
  def shutdown(self):
    # TODO: cleanup anything else you may have when implementing this
    # class.
    self.network_layer.shutdown()

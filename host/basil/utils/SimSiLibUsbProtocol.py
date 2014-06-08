#
# ------------------------------------------------------------
# Copyright (c) All rights reserved
# SiLab, Institute of Physics, University of Bonn
# ------------------------------------------------------------
#
# SVN revision information:
#  $Rev::                       $:
#  $Author::                    $:
#  $Date::                      $:
#
#Initial version by Chris Higgs <chris.higgs@potentialventures.com>
#

"""
These classes are pickled and sent over a socket to communicate with the sim
Protocol is very simple, simply prefix the pickled data with a 4-byte length
"""
import pickle
import struct
import socket

class ProtocolBase(object): pass

class WriteExternalRequest(ProtocolBase):
    def __init__(self, address, data):
        self.address = address
        self.data = data

    def __str__(self):
        return "WriteExternalRequest: 0x%04x <- %s" % (self.address, self.data)

class ReadExternalRequest(ProtocolBase):
    def __init__(self, address, size):
        self.address = address
        self.size = size
    def __str__(self):
        return "ReadExternalRequest: 0x%04x (size %d)" % (self.address, self.size)

class ReadExternalResponse(ProtocolBase):
    def __init__(self, data):
        self.data = data
    def __str__(self):
        return "ReadExternalResponse: %s" % str(self.data)


class PickleInterface(ProtocolBase):

    def __init__(self, sock):
        self.sock = sock

    def send(self, obj):
        """Prepend a 4-byte length to the string"""
        assert isinstance(obj, ProtocolBase)
        string = pickle.dumps(obj)
        length = len(string)
        self.sock.sendall(struct.pack("<I", length) + string)

    def recv(self, blocking=True):
        """Receive the next object from the socket"""
        length = struct.unpack("<I", self.sock.recv(4))[0]
        return self._get_next_obj(length)

    def try_recv(self):
        """Return None immediately if nothing is waiting"""
        try:
            lenstr = self.sock.recv(4, socket.MSG_DONTWAIT)
        except socket.error:
            return None
        if len(lenstr) < 4:
            raise EOFError("Socket closed")
        length = struct.unpack("<I", lenstr)[0]
        return self._get_next_obj(length)

    def _get_next_obj(self, length):
        """Assumes we've already read the object length"""
        string = ""
        while len(string) < length:
            string += self.sock.recv(length - len(string))

        return pickle.loads(string)


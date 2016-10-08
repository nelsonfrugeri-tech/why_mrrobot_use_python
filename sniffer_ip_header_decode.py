import socket
import os
import struct
from ctypes import *

# Host to listen on
host = '192.168.1.4'


class IP(Structure):
    """Responsible for reading transfers packets on network"""

    # Maps the first 20 bytes of buffer received for an
    # IP header in friendly format
    _fields = [
        ('ihl', c_ubyte, 4),
        ('version', c_ubyte, 4),
        ('tos', c_ubyte),
        ('len', c_ushort),
        ('id', c_ushort),
        ('offset', c_ushort),
        ('ttl', c_ubyte),
        ('protocol_num', c_ubyte),
        ('sum', c_ushort),
        ('src', c_ulong),
        ('dst', c_ulong)
    ]

    def __new__(self, socket_buffer=None):
        """Receive the raw buffer and comprises the structure from it"""
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        """Map protocol constants to their names and set address"""

        self.protocol_map = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}

        self.src_address = socket.inet_ntoa(
            struct.pack('<L', self.src)
        )

        self.dst_address = socket.inet_ntoa(
            struct.pack('<L', self.dst)
        )

        # Human readable protocol
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)


if __name__ == '__main__':
    if os.name == 'nt':
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    sniffer = socket.socket(
        socket.AF_INET,
        socket.SOCK_RAW,
        socket_protocol
    )

    sniffer.bind((host, 0, ))

    # We want the IP'headers included in the capture
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    # If we're on Windows we nedd to send some IOCTLs
    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    try:
        while True:
            # Read in a single packet
            raw_buffer = sniffer.recvfrom(65565)[0]

            # Create an IP header from the first 20 bytes of the buffer
            ip_header = IP(raw_buffer[0:20])

            print 'Protocol: {0} {1} -> {2}'.format(
                ip_header.protocol,
                ip_header.src_address,
                ip_header.dst_address
            )
    except KeyboardInterrupt:
        # If we're on Windons turn off promiscuous mode
        if os.name == 'nt':
            sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

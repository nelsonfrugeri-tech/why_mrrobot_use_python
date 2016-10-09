from scapy.all import *


def print_packet(packet):
    print packet.show()


if __name__ == '__main__':
    sniff(prn=print_packet, count=1)

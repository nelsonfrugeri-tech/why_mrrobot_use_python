from scapy.all import *


# Our callback for the packets
def packet_callback(packet):
    if packet[TCP].payload:
        mail_packet = str(packet[TCP].payload)
        if 'user' in mail_packet.lower() or 'pass' in main_packet.lower():
            print '[*] Server: {}'.format(packet[IP].dst)
            print '[*] '.format(packet[IP].payload)


if __name__ == '__main__':
    """PORT: 110(POP3) 25(SMTP) 143(IMAP)
        not store packets in memory
    """
    sniff(
        filter='tcp port 110 or tcp port 25 or tcp port 143',
        prn=packet_callback,
        store=0
    )

#!/usr/bin/env python

import sys
import socket
import threading


def proxy_handler():
    pass


def server_loop(localhost, localport, remotehost, remoteport, receive_first):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((localhost, localport, ))
    except:
        print '[!!] Failed to listen on {}: {}'.format(localhost, localport)
        print '[!!] Check for other listening sockets or correct permissions'
        sys.exit(0)

    print '[*] Listening on {}: {}'.format(localhost, localport)
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # Print out the local connection information
        print '[===>] Receive incoming connection from {}: {}'.format(
            addr[0], addr[1])

        # Start a thread to talk to the remote host
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remotehost, remoteport, receive_first)
        )

        proxy_thread.start()


def main():

    # No fancy command line parsing here
    if len(sys.argv[1:]) != 5:
        print """
-----------------------------------------------------------------------------------
ERROR

Usage: ./proxy.py [localhost] [localport] [serverhost] [serverport] [receive_first]
Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True

-----------------------------------------------------------------------------------
"""
        sys.exit(0)

    # Setup local listening parameters
    localhost = sys.argv[1]
    localport = int(sys.argv[2])

    # Setup remote target
    remotehost = sys.argv[3]
    remoteport = int(sys.argv[4])

    # This tells our proxy to connect and receive data,
    # before sending to the remote host
    receive_first = sys.argv[5]

    if 'True' in receive_first:
        receive_first = True
    else:
        receive_first = False

    # Now spin up our listening socket
    server_loop(localhost, localport, remoteport, remotehost, receive_first)


if __name__ == '__main__':
    main()

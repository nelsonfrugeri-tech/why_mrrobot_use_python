#!/usr/bin/env python

import sys
import socket
import threading


def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, unicode) else 2

    for i in xrange(0, len(src), length):
        s = src[i:i + length]
        hexa = b' '.join(['%0*X' % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append( b'%04X   %-*s   %s' % (i, length*(digits + 1), hexa, text))

    print b'\n'.join(result)


def receive_from(connection):
    buffer = ''

    # We set a 2 second time out depending on your
    # target this may nedd to be adjusted
    connection.settimeout(2)

    try:
        while True:
            # Receive data from the socket
            data = connection.recv(4096)

            if not data:
                break

            buffer += data
    except:
        pass

    return buffer


def request_handler(buffer):
    """Modify any request destined for the remote host"""
    return buffer


def response_handler(buffer):
    # Modify any responses destined for the local host
    return buffer


def proxy_handler(client_socket, remotehost, remoteport, receive_first):

    # Connect to the remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remotehost, remoteport, ))

    # Receive data from the remote end if necessary
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        # Send it to our response handler
        remote_buffer = response_handler(remote_buffer)

        # If we have data to send to our local client sent it
        if len(remote_buffer):
            print '[<===] Sending {} bytes to localhost'.format(
                len(remote_buffer))
            client_socket.send(remote_buffer)

    # Now let's loop and reading from local, send to remote, send to local
    # Rinse, wash and repeat
    while True:
        # Read from localhost
        local_buffer = receive_from(client_socket)

        if len(local_buffer):
            print '[===>] Received {} bytes from localhost'.format(
                len(local_buffer))

            # Send it to our request handler
            local_buffer = request_handler(local_buffer)

            # Send off the data to the remote host
            print '[===>] Sent to remote'

        if len(remote_buffer):
            print '[<===] Received {} bytes from remote'.format(
                len(remote_buffer))
            hexdump(remote_buffer)

            # Send to our response handler
            remote_buffer = response_handler(remote_buffer)

            # Send the response to the local socket
            client_socket.send(remote_buffer)

            print '[<===] Sent to localhost'

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print '[*] No more data. Closing connections...'

            break


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

import socket


def client_tcp():
    """Get page duckduckgo.com

        AF_INET: set the default protocol IPV4
        SOCK_STREAM: set client as TCP
    """
    target_host = '127.0.0.1'
    target_port = 9000

    # Create socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect client
    client.connect((target_host, target_port, ))

    # Send data
    client.send('GET / HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n')

    # Receive data
    response = client.recv(4096)

    print response


def client_udp():
    """Send packages for localhost

        AF_INET: set the default protocol IPV4
        SOCK_DGRAM: set client as UDP
    """

    target_host = '127.0.0.1'
    target_port = 9000

    # Create socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send data
    client.sendto("Hello my friend!", (target_host, target_port, ))

    # Receive data
    data, addr = client.recvfrom(4096)

    print data


def main():
    option = -1

    while option != 0:
        option = int(raw_input(
"""
1 - Client TCP
2 - Client UDP
0 - Exit
"""))

        if option == 1:
            client_tcp()
        elif option == 2:
            client_udp()


if __name__ == '__main__':
    main()

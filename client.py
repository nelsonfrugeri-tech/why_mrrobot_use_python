import socket


def client_tcp():
    """Responsible for get page duckduckgo.com

        AF_INET: set the default protocol IPV4
        SOCK_STREAM: set client as TCP
    """
    target_host = 'www.duckduckgo.com'
    target_port = 80

    # Create socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect client
    client.connect((target_host, target_port, ))

    # Send data
    client.send('GET / HTTP/1.1\r\nHost: duckduckgo.com\r\n\r\n')

    # Receive data
    response = client.recv(4096)

    print response


def client_udp():
    print 'Client UDP'


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

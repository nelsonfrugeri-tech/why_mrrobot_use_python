import socket


def main():
    """Responsible for get page duckduckgo.com

        AF_INET: set the default protocol IPV4
        SOCK_STREAM: set client as TCP
    """
    target_host = "www.duckduckgo.com"
    target_port = 80

    # Create socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect client
    client.connect((target_host, target_port, ))

    # Send data
    client.send("GET / HTTP/1.1\r\nHost: duckduckgo.com\r\n\r\n")

    # Receive data
    response = client.recv(4096)

    print response


if __name__ == '__main__':
    main()

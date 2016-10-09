import socket
import threading


def handle_client(client_socket):
    """Thread responsible for handle client connection"""

    request = client_socket.recv(1024)

    print '[*] Receive {}'.format(request)

    client_socket.send('ACK!')

    client_socket.close()


def main():
    bind_ip = '127.0.0.1'
    bind_port = 9000

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip, bind_port, ))
    server.listen(5)

    print '[*] Listening of {}: {}'.format(bind_ip, bind_port)

    while True:
        client, addr = server.accept()

        print '[*] Accepted connection from {}: {}'.format(addr[0], addr[1])

        # Instance thread and run!
        client_handler = threading.Thread(
            target=handle_client,
            args=(client, )
        )

        client_handler.start()


if __name__ == '__main__':
    main()

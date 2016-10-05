import sys
import socket
import getopt
import threading
import subprocess


# Globals vars
listen = False
command = False
upload = False
execute = ''
target = ''
upload_destination = ''
port = 0


def usage():
    print"""
-------------------------------------------------------------------------------

NetDog Tool

Usage: netdog.py -t target_host -p port
-l --listen              -listen on [host]:[port] for incoming connections
-e --execute=file_to_run -execute the given file upon receiving a connection
-c --command             - initialize a command shell
-u --upload=destination  - upon receiving connection upload a file and write
                           to destination

Examples:

1) netdog.py -t 192.168.1.1 -p 5555 -l -c
2) netdog.py -t 192.168.1.1 -p 5555 -l -u=/home/john/Documents/install.sh
3) netdog.py -t 192.168.1.1 -p 5555 -l -e=\"cat /etc/passwd\
4) echo "Hello my friend!" | ./netdog.py -t 192.168.11.12 -p 9000

-------------------------------------------------------------------------------
"""
    sys.exit(0)


def run_command(command):

    # Remove break line
    command = command.rstrip()

    # Run command and get data of output
    try:
        output = subprocess.check_output(
            command,
            stderr=subprocess.STOUT,
            shell=True
        )
    except:
        output = 'Failed to execute command \r\n'

    return output


def client_handler(client_socket):
    global upload
    global execute
    global command

    # Check if upload
    if len(upload_destination):

        # Read bytes e write on destination
        file_buffer = ''

        # Keep read data until there isn't more available
        while True:
            data = client_socket.recv(1024)

            if not data:
                break

            file_buffer += data

        # Write bytes
        try:
            file_descriptor = open(upload_destination, 'wb')
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            # Confirm that recorded filec
            client_socket.send(
                'Successfully saved file to {} \r\n'.format(
                    upload_destination))
        except:
            client_socket.send(
                'Failed to save file to {}'.format(upload_destination))

        # Checks whether command execution
        if len(execute):
            # Run other command
            output = run_command(execute)
            client_socket.send(output)

        # Enter another loop if the command shell was executed
        if command:
            while True:
                # Render simple prompt
                client_socket.send('<NetDog: #> ')
                # Enter (Return) to continue...
                cmd_buffer = ''

                while '\n' not in cmd_buffer:
                    cmd_buffer += client_socket.recv(1024)

                    # Send back the command output
                    response = run_command(cmd_buffer)

                    # Send back the response
                    client_socket.send(response)


def server_loop():
    global target

    if not len(target):
        target = '0.0.0.0'

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port, ))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        # Open thread for client
        client_thread = threading.Thread(
            target=client_handler, args=(client_socket, ))
        client_thread.start()


def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connects to host
        client.connect((target, port, ))

        if len(buffer):
            client.send(buffer)

        while True:
            # Wait to receive data
            recv_len = 1
            response = ''

            while recv_len:

                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print response

            # Wait for further input data
            buffer = raw_input('')
            buffer += '\n'

            # Send data
            client.send(buffer)
    except:
        print '[*] Exception! Exiting'
        client.close()


def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    # Set params
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 'hle:t:c:p:cu',
            ['help', 'listen', 'execute', 'target', 'port', 'command',
                'upload'])
    except getopt.GetoptError as err:
        print str(err)

    for option, argument in opts:
        if option in ('-h', '--help'):
            usage()
        elif option in ('-l', '--listen'):
            listen = True
        elif option in ('-e', '--execute'):
            execute = argument
        elif option in ('-c', '--commandshell'):
            command = True
        elif option in ('-u', '--upload'):
            upload_destination = argument
        elif option in ('-t', '--target'):
            target = argument
        elif option in ('-p', '--port'):
            port = int(argument)
        else:
            assert False, 'Unhandled option'

    if not listen and len(target) and port > 0:
        buffer = sys.stdin.read()
        client_sender(buffer)

    if listen:
        server_loop()


if __name__ == '__main__':
    main()

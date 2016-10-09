#!/usr/bin/env python

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

1) ./netdog.py -t 192.168.1.1 -p 5555 -l -c
2) ./netdog.py -t 192.168.1.1 -p 5555 -l -u=/home/john/Documents/install.sh
3) ./netdog.py -t 192.168.1.1 -p 5555 -l -e=\"cat /etc/passwd\
4) echo "Hello my friend!" | ./netdog.py -t 192.168.11.12 -p 9000

-------------------------------------------------------------------------------
"""
    sys.exit(0)


def run_command(command):

    # Remove break line
    command = command.rstrip()

    # Run command and get the output back
    try:
        output = subprocess.check_output(
            command,
            stderr=subprocess.STDOUT,
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

        # Keep reading data until there isn't more available
        while True:
            data = client_socket.recv(1024)

            if not data:
                break

            file_buffer += data

        # Now we take these bytes and try to write them out
        try:
            file_descriptor = open(upload_destination, 'wb')
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            # Acknowledge that we wrote the file out
            client_socket.send(
                'Successfully saved file to {} \r\n'.format(
                    upload_destination))
        except:
            client_socket.send(
                'Failed to save file to {}'.format(upload_destination))

    # Check for command execution
    if len(execute):
        # Run other command
        output = run_command(execute)
        client_socket.send(output)

    # Now we go into another loop if a command shell was requested
    if command:
        while True:
            # Show a simple prompt
            client_socket.send('<NetDog: #> ')
            # Now we receive until we see a linefeed (enter key)
            cmd_buffer = ''

            while '\n' not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

                # We have a valid command so execute it and
                # send back the results
                response = run_command(cmd_buffer)

                # Send back the response
                client_socket.send(response)


def server_loop():
    global target
    global port

    if not len(target):
        target = '0.0.0.0'

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
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
        client.connect((target, port))

        if len(buffer):
            client.send(buffer)

        while True:
            # Now wait for data back
            recv_len = 1
            response = ''

            while recv_len:

                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

            print response,

            # Wait for more input
            buffer = raw_input('')
            buffer += '\n'

            # Send it off
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

    # Read the commandline options
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], 'hle:t:p:cu:',
            ['help', 'listen', 'execute', 'target', 'port', 'command',
                'upload'])
    except getopt.GetoptError as err:
        print str(err)
        usage()

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
        # Read in the buffer from the commandline
        # this will block, so send CTRL-D if not sending input
        # to stdin
        buffer = sys.stdin.read()

        # Send data off
        client_sender(buffer)

    # We are going to listen and potentially
    # upload things, execute commands and drop a shell back
    # depending on our command line options above
    if listen:
        server_loop()


if __name__ == '__main__':
    main()

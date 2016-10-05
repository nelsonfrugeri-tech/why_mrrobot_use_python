import sys
import socket
import getopt
import threading
import subprocess


# Globals vars
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
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


def main():

    if not len(sys.argv[1:]):
        usage()

    # Set params
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hle:t:c:p:cu',
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

    if not listen and len(target) and  port > 0:
        buffer = sys.stdin.read()
        client_sender(buffer)

    if listen:
        server_loop()


if __name__ == '__main__':
    main()

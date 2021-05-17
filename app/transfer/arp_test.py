import os
import re
import socket
import sys
import threading

DEFAULT_PORT = 55111
BUFFER_SIZE = 1024
SERVER_TIMEOUT = 10
CLIENT_TIMEOUT = 5

def get_devices():
    with os.popen('arp -a') as f:
        data = f.read()

    devices = []
    for line in data.split('\n'):
        parts = line.split(' ')
        if len(parts) >= 4:
            device = { "name" : parts[0], "ip" : re.sub('[()]', '', parts[1]), "mac" : parts[3] }
            if device["ip"] == '224.0.0.251' or device["ip"].split('.')[-1] == '1':
                continue
            devices.append(device)
        
    return devices

def print_devices(result):
    print("----------------------------------------------------------------------\nIP Address\t\tMAC Address\t\tDevice Name\n----------------------------------------------------------------------")
    for i in result:
        print("{}\t\t{}\t({})".format(i["ip"], i["mac"], i["name"]))

def get_files_from_server(ip):

    server_addr = (ip, DEFAULT_PORT)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(CLIENT_TIMEOUT)
    # any client ip and port
    client_addr = ('', 0)
    # bind server address to port
    client_socket.bind(client_addr)
    # connect to server
    print("trying to connect to server: {}".format(server_addr))
    try:
        client_socket.connect(server_addr)

        client_socket.send("0".encode()) ### send time last updated
        try:
            file = open("received_data.zip", 'wb')
        except Exception:
            print("Failed to create zip file for received data.")
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            print(data)
            if not data:
                break
            file.write(data)
        file.close()
        print("file written")
        client_socket.close()
    except socket.error as exc:
        print("Socket exception: %s" % exc)
        client_socket.close()

def start_server():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # closes server after timeout if no client connected
    server_socket.settimeout(SERVER_TIMEOUT)
    # get default address and bind
    server_addr = (socket.gethostbyname(socket.gethostname()), DEFAULT_PORT)
    server_socket.bind(server_addr)

    # makes socket ready for accepting connections (max 1)
    server_socket.listen(1)
    print("server waiting on socket: {}".format(server_socket.getsockname()))

    try:
        (client_socket, client_addr) = server_socket.accept()
        print("client {} connected".format(client_addr))
        msg = client_socket.recv(4096)
        if msg.decode() == "0": ### change this to check if it is an actual time
            ### compress correct files to zip and send
            try:
                file = open('test.zip', 'rb')
            except Exception:
                print("Failed to open or compress files for sending to client.")
                return
            while True:
                data = file.read(BUFFER_SIZE)
                if not data:
                    break
                client_socket.send(data)
            file.close()
            print("File sent succesfully: closing server")
            server_socket.close()
            

        else:
            print("no time received")
    except socket.timeout:
        print("No connection to server: closing server.")
        server_socket.close()
    except socket.error as exc:
        print("Socket exception: %s" % exc)
        server_socket.close()
    except Exception:
        print("An error occurred while listening to client.")
        server_socket.close()

def start_server_threaded():
    thread = threading.Thread(target=start_server)
    thread.start()

# test ----------------------------------------------

if sys.argv[1] == "server":
    start_server_threaded()
else:
    devices = get_devices()
    print_devices(devices)
    get_files_from_server('192.168.1.22')

#get_files_from_server(devices[0]["ip"])
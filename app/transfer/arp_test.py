import os
import re
import socket
import sys
import select
import queue

default_port = 55111
BUFFER_SIZE = 1024

def get_devices():
    with os.popen('arp -a') as f:
        data = f.read()

    devices = []
    for line in data.split('\n'):
        parts = line.split(' ')
        if len(parts) >= 4:
            device = { "name" : parts[0], "ip" : re.sub('[()]', '', parts[1]), "mac" : parts[3] }
            devices.append(device)
        
    return devices

def print_devices(result):
    print("-----------------------------------\nIP Address\t\tMAC Address\t\tDevice Name\n-----------------------------------")
    for i in result:
        print("{}\t\t{}\t\t({})".format(i["ip"], i["mac"], i["name"]))

def get_files_from_server(ip):

    server_addr = (ip, default_port)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # any client ip and port
    client_addr = ('', 0)
    # bind server address to port
    client_socket.bind(client_addr)
    # connect to server
    print("trying to connect to server: {}".format(server_addr))
    client_socket.connect(server_addr)

    inputs = [client_socket]
    outputs = []

    client_socket.send("0".encode())
    file = open("received_file.zip", 'wb')
    while True:
        data = client_socket.recv(BUFFER_SIZE)
        print(data)
        if not data:
            break
        file.write(data)
    file.close()
    print("file written")
    client_socket.close()

def start_server():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # get default address and bind
    server_addr = (socket.gethostbyname(socket.gethostname()), default_port)
    server_socket.bind(server_addr)

    # makes socket ready for accepting connections (max 1)
    server_socket.listen(1)
    print("server waiting on socket: {}".format(server_socket.getsockname()))

    (client_socket, client_addr) = server_socket.accept()
    print("client {} connected".format(client_addr))
    msg = client_socket.recv(4096)
    if msg.decode() == "0": # change this to check if it is an actual time
        print(msg.decode())
        # compress correct files to zip and send
        file = open('file_name.zip', 'rb')
        while True:
            data = file.read(BUFFER_SIZE)
            if not data:
                break
            client_socket.send(data)

    else:
        print("no time received")

    file.close()
    server_socket.close()
    print("server closed")
    

# test ----------------------------------------------
if sys.argv[1] == "server":
    start_server()
else:
    devices = get_devices()
    print_devices(devices)
    get_files_from_server('192.168.2.3')
#get_files_from_server(devices[0]["ip"])
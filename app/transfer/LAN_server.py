import os
import re
import socket
import threading
from logic.file_handler import make_dirs, get_newest_datetime, zip_articles, unzip_articles, DIR_TRANSFER
from datetime import datetime

class LANServer:

    def __init__(self):
        self.default_port = 55111
        self.buff_size = 1024
        self.server_timeout = 15
        self.running = False
        self.address = (-1, -1)
        self.socket = None

    def start_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.socket.settimeout(self.server_timeout)
        self.address = (socket.gethostbyname(socket.gethostname()), self.default_port)
        self.socket.bind(self.address)
        self.socket.listen(1)
        self.running = True
        print("server running on " + self.get_IP())

        try:
            (client_socket, client_addr) = self.socket.accept()
            msg = client_socket.recv(4096)

            if msg.decode() == "None":
                date_time = None
            else:
                try:
                    date_time = datetime.fromisoformat(msg.decode())
                except Exception:
                    print("Received time is not in iso format.")
                    self.socket.close()
                    self.running = False
                    return
            try:
                path = zip_articles(date_time)
                if path == None:
                    self.socket.close()
                    self.running = False
                    return
                else:
                    file = open(path, 'rb')
            except Exception:
                print("Failed to open or compress files for sending to client.")
                return
            while True:
                data = file.read(self.buff_size)
                if not data:
                    break
                client_socket.send(data)
            file.close()
            self.socket.close()
            self.running = False

        except socket.timeout:
            print("No connection to server: closing server.")
            self.socket.close()
        except socket.error as exc:
            print("Socket exception: %s" % exc)
            self.socket.close()
        except Exception:
            print("An error occurred while listening to client.")
            self.socket.close()

    def start_server_threaded(self):
        self.thread = threading.Thread(target=self.start_server)
        self.thread.start()

    def stop_server(self):
        if self.running:
            if self.socket != None:
                self.socket.close()
                self.running = False
        print("closed connection")

    def get_IP(self):
        return str(self.address[0])

    def get_port(self):
        return str(self.address[1])
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

    def start_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.socket.settimeout(self.server_timeout)
        address = (socket.gethostbyname(socket.gethostname()), self.default_port)
        self.socket.bind(address)
        self.socket.listen(1)

        #TODO


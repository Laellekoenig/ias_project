import os
import re
import socket
import subprocess
import sys
import threading
from logic.file_handler import get_newest_datetime, zip_articles, unzip_articles, DIR_TRANSFER
from datetime import datetime
import platform

class bt_server:

    def __init__(self):
        #####self.device_os = None
        self.host_mac_address = None
        self.port = 4
        self.socket = None
        self.running = False
        self.server_timeout = 5
        self.thread_running = False

    def start_server(self):
        self.thread_running = True
        self.host_mac_address = self.get_mac_address()
        if self.host_mac_address is None:
            print("Your device is currently not supported (you cannot start a bluetooth server)")
            
        print("your bluetooth server is starting now \n")
        print (self.host_mac_address)
        print("this is the address somebody else has to type in to receive the articles you have \n")

        try: #try to create a socket
            self.socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
            self.socket.settimeout(self.server_timeout)
            #####self.socket.settimeout(30)
            self.socket.bind((self.host_mac_address, self.port))
            #####print("in 30 seconds the server closes, if no client connected")
            self.socket.listen(1)
            self.running = True
            print("waiting for incoming connections...")
        except Exception:
            print("Socket creation exception")
            return
        
        while self.running:
            try: 
                client, address = self.socket.accept()
                print("client {} connected to your server and is receiving your articles now".format(address))
            except Exception::
                print("couldn't connect with client")
                self.socket.close()
                self.running = False
                return
            except socket.timeout:
                self.socket.listen(1)
                print("renew timeout")

            try:
                date_time_msg = client.recv(4096)
                date_time = datetime.fromisoformat(date_time_msg.decode())
            except Exception::
                print("something went wrong...")
                print("try to turn on your bluetooth and try again")
                client.close()
                self.socket.close()
                self.running = False
                return
            except socket.timeout:
                self.socket.listen(1)
                print("renew timeout")

            try:
                path = zip_articles(date_time)
                if path == None:
                    client.send("???!no_new_data_for_you!???")
                    client.close()
                    self.socket.close()
                    self.running = False
                    print("there are no new articles for you")
                    return
                else:
                    f = open(path, 'rb')
            except Exception:
                print("Failed to open or compress files for sending to client.")
                client.send("???!no_new_data_for_you!???")
                client.close()
                self.socket.close()
                self.running = False
                return
            except socket.timeout:
                self.socket.listen(1)
                print("renew timeout")
            #f = open("Bluetoothtest.txt", "rb")

            try:    
                data = ""
                while not data == "!?L=C)(JZB?)K)=FJ(W".encode():
                    data = f.read(1024)
                    if data == "".encode(): # sent all bits of the file
                        data = "!?L=C)(JZB?)K)=FJ(W".encode() # windows socket doesn't support flush() (problems with sending empty packet, so that receiver doesn't know when last packet arrived, therefore sending this string)
                    client.send(data)
                #client.flush()  
                print("finished sending new articles")
            except Exception::
                print("something went wrong while sending your articles")
            except socket.timeout:
                self.socket.listen(1)
                print("renew timeout")

            f.close()
            #if os.path.exists(str(Path.home()) + "/NewsTest/Articles/articles.zip"):
                #os.remove(str(Path.home()) + "/NewsTest/Articles/articles.zip")
            client.close()
            self.socket.close()
            self.running = False

        self.thread_running = False


    def get_device_os(self):
        try:
            return platform.system()
        except:
            return None

    def get_mac_address(self):
        try: #try to get bluetooth MAC-address of device, if it fails, return None
            self.device_os = platform.system()
            if self.get_device_os().lower() == "windows":
                output = subprocess.check_output("ipconfig /all").decode(encoding="437")
                pattern = '(.*)(bluetooth|Bluetooth)((.|\s)*)'
                bluetooth_part = re.search(pattern, output).group(3)
                mac_address_pattern = '[0-9a-fA-F][0-9a-fA-F]-[0-9a-fA-F][0-9a-fA-F]-[0-9a-fA-F][0-9a-fA-F]-[0-9a-fA-F][0-9a-fA-F]-[0-9a-fA-F][0-9a-fA-F]-[0-9a-fA-F][0-9a-fA-F]'
                mac_address = re.search(mac_address_pattern, bluetooth_part).group(0) # if it doesnt work, end program, didnt find bluetooth mac address on windows!
                host_mac_address = mac_address.replace("-", ":") # MAC-address needs to have ':' between the numbers, not '-'
            elif self.device_os.lower() == "darwin":
                status, output = subprocess.getstatusoutput("system_profiler SPBluetoothDataType")
                pattern = '(bluetooth|Bluetooth:)((.|\s)*)'
                bluetooth_part = re.search(pattern, output).group(2)
                mac_address_pattern = '[0-9a-fA-F][0-9a-fA-F]-[0-9a-fA-F][0-9a-fA-F]-[0-9a-fA-F][0-9a-fA-F]-[0-9a-fA-F][0-9a-fA-F]-[0-9a-fA-F][0-9a-fA-F]-[0-9a-fA-F][0-9a-fA-F]'
                mac_address = re.search(mac_address_pattern, bluetooth_part).group(0)
                host_mac_address = mac_address.replace("-", ":")
            else:
                status, output = subprocess.getstatusoutput("hciconfig")
                host_mac_address = output.split("{}:".format("hci0"))[1].split("BD Address: ")[1].split(" ")[0].strip()
            return host_mac_address
        except:
            return None

    def stop_server(self):
        """if self.running:
            if self.socket != None:
                self.socket.close()
                self.running = False
        print("closed connection")"""
        self.running = False

    def keep_alive(self):
        self.running = True

    def is_running(self):
        return self.thread_running

    def start_server_threaded(self):
        self.thread = threading.Thread(target=self.start_server)
        self.thread.start()

    def on_macOS(self):
        if platform.system().lower() == "darwin":
            return True
        else:
            return False
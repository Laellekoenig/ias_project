import os
import re
import socket
import subprocess
import sys
import threading
from logic.file_handler import get_newest_datetime, zip_articles, unzip_articles, DIR_TRANSFER
from datetime import datetime
import platform

def start_server():
    try: #try to get bluetooth MAC-address of device, if it fails, exit program
        deviceOs = platform.system()
        if deviceOs.lower() == "windows":
            output = subprocess.check_output("ipconfig /all").decode(encoding="437")
            pattern = '(.*)(bluetooth|Bluetooth)((.|\s)*)'
            bluetooth_part = re.search(pattern, output).group(3)
            mac_address_pattern = '[0-9a-fA-F][0-9a-fA-F]-[0-9a-fA-F][0-9a-fA-F]-[0-9a-fA-F][0-9a-fA-F]-[0-9a-fA-F][0-9a-fA-F]-[0-9a-fA-F][0-9a-fA-F]-[0-9a-fA-F][0-9a-fA-F]'
            mac_address = re.search(mac_address_pattern, bluetooth_part).group(0) # if it doesnt work, end program, didnt find bluetooth mac address on windows!
            mac_address = mac_address.replace("-", ":") # MAC-address needs to have ':' between the numbers, not '-'
        elif deviceOs.lower() == "darwin":
            status, output = subprocess.getstatusoutput("system_profiler SPBluetoothDataType")
            pattern = '(bluetooth|Bluetooth:)((.|\s)*)'
            bluetooth_part = re.search(pattern, output).group(2)
            mac_address_pattern = '[0-9a-fA-F][0-9a-fA-F]-[0-9a-fA-F][0-9a-fA-F]-[0-9a-fA-F][0-9a-fA-F]-[0-9a-fA-F][0-9a-fA-F]-[0-9a-fA-F][0-9a-fA-F]-[0-9a-fA-F][0-9a-fA-F]'
            mac_address = re.search(mac_address_pattern, bluetooth_part).group(0)
            mac_address = mac_address.replace("-", ":")
        else:
            status, output = subprocess.getstatusoutput("hciconfig")
            mac_address = output.split("{}:".format("hci0"))[1].split("BD Address: ")[1].split(" ")[0].strip()
    except:
        print("Your device is currently not supported (you cannot start a bluetooth server)")
        return

    print("your bluetooth server is starting now \n")
    print (mac_address)
    print("this is the address somebody else has to type in to receive the articles you have \n")

    host_mac_address = mac_address
    port = 4

    try: #try to connect with a client
        s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        s.settimeout(30)
        s.bind((host_mac_address, port))
        print("waiting for incoming connections...")
        print("in 30 seconds the server closes, if no client connected")
        s.listen(1)
        client, address = s.accept()
        print("client {} connected to your server and is receiving your articles now".format(address))

        date_time_msg = client.recv(4096)
        date_time = datetime.fromisoformat(date_time_msg.decode())
    except socket.timeout:
        print("no client connected, server gets closed")
        client.close()
        s.close()
        return
    except:
        print ("something went wrong...")
        print("try to turn on your bluetooth and try again")
        client.close()
        s.close()
        return

    try:
        path = zip_articles(date_time)
        if path == None:
            client.send("???!no_new_data_for_you!???")
            client.close()
            s.close()
            print("there are no new articles for you")
            return
        else:
            f = open(path, 'rb')
    except Exception:
        print("Failed to open or compress files for sending to client.")
        client.send("???!no_new_data_for_you!???")
        client.close()
        s.close()
        return
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
    except:
        print("something went wrong while sending your articles")

    f.close()
    #if os.path.exists(str(Path.home()) + "/NewsTest/Articles/articles.zip"):
        #os.remove(str(Path.home()) + "/NewsTest/Articles/articles.zip")
    client.close()
    s.close()

def start_client():
    address = input("Enter the xx:xx:xx:xx:xx:xx address of the device you'd like to get your articles from: ")
    print("trying to connect...")

    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    port = 4

    success = False
    while not success: # try to connect to server
        i = 0
        while i < 3: # try connecting 3 times until asking for a new input
            server_mac_address = address
            try:
                s.connect((server_mac_address, port))
                print("successfully connected")
                success = True
                i = 3
            except:
                i = i + 1
                if i > 3:
                    print("something went wrong, please try again")
                    address = input("Write quit to leave or enter the xx:xx:xx:xx:xx:xx address of the device you'd like to get your articles from: ")
                    if address == quit:
                        return
                    print("trying to connect...")
    try:
        s.send(get_newest_datetime().isoformat().encode())
        data = s.recv(1024)
        if data.decode() == "???!no_new_data_for_you!???":
            print("no new articles for you")
            return
        f = open(DIR_TRANSFER + "/received_articles.zip", 'wb')
        f.write(data)
    except:
        print("something went wrong")
        s.close()
        return

    try:
        data = s.recv(1024)
        print("receiving new articles...")

        while not data == "!?L=C)(JZB?)K)=FJ(W".encode():
            f.write(data)
            data = s.recv(1024)
        print("new articles successfully added")
        f.close()
        s.close()
        unzip_articles(DIR_TRANSFER + "/received_articles.zip")

    except:
        print("there was a problem while receiving articles...closing connection")
        f.close()
        s.close()

    #article_directory = os.listdir(articles_dir)

    #for item in article_directory:
    #    if item.endswith(".zip"):
    #        os.remove(os.path.join(articles_dir, item))

def main():
    start_server()

if __name__ == "__main__":
    main()
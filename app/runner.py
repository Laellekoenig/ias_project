import sys
from gui.main_window import MainWindow
from scraper.srf_scraper import getSRFArticles
from PyQt5 import QtWidgets as qtw
from logic.interface import LogicInterface
from logic.file_handler import zip_articles
from logic.file_handler import get_newest_datetime
from datetime import datetime

# ---------------------- client server test: --------------------------
#from transfer.LAN_client import LANClient
#from transfer.LAN_server import LANServer
#if sys.argv[1] == "server":
#    s = LANServer()
#    s.start_server()
#else:
#    c = LANClient()
#    c.start_client_threaded("192.168.2.3")

# ---------------------------------------------------------------------

#from transfer.local_network import start_server_threaded
#from transfer.bluetooth import start_server, start_client
#start_server()

#start_server_threaded()

#zip_articles('2021-04-17T08:42:00')
#print(get_newest_datetime().isoformat())
li = LogicInterface()
#li.download_new_articles()
# articles = li.get_articles()
# a = articles[1]
# li.mark_as_opened(a)
# li.bookmark_article(a)
# li.mark_as_deleted(a)
#li.download_new_articles()
#for a in li.get_articles():
#    print(a.title_0)


app = qtw.QApplication(sys.argv)
mainWindow = MainWindow(app)
app.exec()

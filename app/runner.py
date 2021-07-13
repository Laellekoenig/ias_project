import sys
from gui.main_window import MainWindow
from scraper.srf_scraper import getSRFArticles
from PyQt5 import QtWidgets as qtw
from logic.interface import LogicInterface
from logic.file_handler import zip_articles
from logic.file_handler import get_newest_datetime
from datetime import datetime

# ---------------------- bac net test: --------------------------
from bacnet.core import BACCore
from logic.article import Article

a = Article('SRF')
json_raw = a.get_json()
b = BACCore()
if not b.exists_db():
    b.setup_db('phil_sim')
else:
    b.setup_db()
#print(b.exists_user())
#b.create_user('test_user') # only if no user exists
b.create_feed('test_feed')
b.create_feed('test_feed2')
b.create_feed('test_feed3')
b.create_event('test_feed', json_raw)
#b.create_event('test_feed', "SRF - Am Gotthard ist zu Ferienbeginn Geduld gefragt")
#b.create_event('test_feed', "SRF - Am Gotthard ist zu Ferienbeginn Geduld gefragt")
#b.create_event('test_feed2', "SRF - Am Gotthard ist zu Ferienbeginn Geduld gefragt")
#b.create_event('test_feed3', "SRF - «Die selbstfahrenden Postautos kommen sehr gut an»")

#print(b.get_event_content(b.get_all_feed_ids()[1], 1))
#b.get_some_event()
#f = open('result.json', 'w')
##print(b.get_json_from_event(b.get_all_feed_ids()[1], 4))
#f.write(b.get_event_content(b.get_all_feed_ids()[1], 4)[1])
#f.close

#b.set_path_to_db("D:")
#b.export_db_to_pcap("pcap")
#b.import_from_pcap_to_db("pcap")
##b.get_user_name()
print(b.get_feednames_from_host())
print(b.get_all_feed_ids())
i = b.get_id_from_feed_name("test_feed")
print(b.get_json_from_event(i, 2))
# ---------------------------------------------------------------------

# ---------------------- client server test: --------------------------
#from transfer.LAN_client import LANClient
#from transfer.LAN_server import LANServer
#if sys.argv[1] == "server":
#    s = LANServer()
#    s.start_server()
#else:
#    c = LANClient()
#    c.start_client_threaded("192.168.2.3")
#
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

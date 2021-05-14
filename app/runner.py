import sys
from gui.main_window import MainWindow
from scraper.srf_scraper import getSRFArticles
from PyQt5 import QtWidgets as qtw
from logic.interface import LogicInterface
from transfer.network_test import scan
from transfer.network_test import display_result

scanned_output = scan('192.168.1.1/24')
display_result(scanned_output)

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

import sys
from gui.main_window import MainWindow
from scraper.srf_scraper import getSRFArticles
from PyQt5 import QtWidgets as qtw
from logic.interface import LogicInterface

li = LogicInterface()
#li.download_new_articles()
for a in li.get_articles():
    print(a.title_0)


app = qtw.QApplication(sys.argv)
mainWindow = MainWindow(app)
app.exec()

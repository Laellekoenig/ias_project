import sys
from gui.MainWindow import MainWindow
from scraper.SRFScraper import getSRFArticles
from PyQt5 import QtWidgets as qtw

app = qtw.QApplication(sys.argv)
mainWindow = MainWindow(app)
app.exec()

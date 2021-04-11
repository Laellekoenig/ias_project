import sys
import math
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc


class MainWindow(qtw.QWidget):

    def __init__(self, app):
        # initiate window
        super().__init__(windowTitle="IAS Project")

        css = self.getStyleSheet()
        self.setStyleSheet(css)
        
        #text reader
        text = qtw.QTextBrowser()
        with open("gui/test.html", "r") as html:
            text.insertHtml(html.read())
        text.setOpenExternalLinks(True)

        #article selector
        selector = qtw.QListWidget()
        entries = self.getEntries()
        selector.addItems(entries)

        # grid layout for playing items, 10 rows, 10 cols
        layout = qtw.QGridLayout()
        layout.addWidget(selector, 0, 0, 10, 2)
        layout.addWidget(text, 0, 4, 10, 7)

        self.setLayout(layout)
        self.startScreenSize(app)
        self.setMinimumSize(700, 500)
        self.show()

    def getScreenSize(self, app):
        screen = app.primaryScreen()
        size = screen.size()
        w = size.width()
        h = size.height()
        return (w, h)

    def startScreenSize(self, app):
        w, h = self.getScreenSize(app)
        RATIO = 0.7
        w = math.floor(RATIO * w)
        h = math.floor(RATIO * h)
        self.resize(w, h)

    def getStyleSheet(self):
        stylesheet = """
        QWidget {
            background-color: white;
        }
        QTextBrowser {
            background-color: white;
            border-style: none;
            border-left: 5px;
            padding-right: 100px;
            padding-left: 50px;
        }
        QTextBrowser QScrollBar {
            height: 0px;
            width: 0px;
        }
        QPushButton {
        }
        QListWidget {
            font-family: Roboto;
            font-size: 30px;
            line-height: 2;
            border-style: none;
            border-right: 1px solid lightgrey;
            spacing: 10;
        }
        QListWidget::Item {
            margin: 10px;
        }"""
        return stylesheet

    def getEntries(self):
        return ["Artikel 1", "Artikel 2", "Artikel 3", "Artikel 4", "Artikel 5"]

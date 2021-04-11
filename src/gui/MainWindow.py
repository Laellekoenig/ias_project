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
         # for styling
        text.setObjectName("article")

        # grid layout for playing items
        layout = qtw.QGridLayout()
        layout.addWidget(text, 0, 5)

        # horizontal layout for placing menu items
        menu_layout = qtw.QHBoxLayout()
        layout.addLayout(menu_layout, 0, 0)

        #menu
        menu = qtw.QListWidget()
        entries = self.getEntries()
        menu.addItems(entries)
        menu_layout.addWidget(menu)

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
        QWidget#article {
            background-color: white;
            border-style: none;
            border-left: 5px;
            padding-right: 100px;
        }
        QPushButton {
        }"""
        return stylesheet

    def getEntries(self):
        return ["hallo", "welt", "wie", "geht", "es"]

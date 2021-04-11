import sys
import math
import os
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc


class MainWindow(qtw.QWidget):

    def __init__(self, app):
        # initiate window
        super().__init__(windowTitle="IAS Project")

        css = self.getStyleSheet()
        self.setStyleSheet(css)
        self.setObjectName("main")
        
        #text reader
        text = qtw.QTextBrowser()
        self.article = text
        #with open("articles/article1.html", "r") as html:
        #    text.insertHtml(html.read())
        text.setOpenExternalLinks(True)

        #article selector
        selector = qtw.QListWidget()
        self.selector = selector
        entries = self.getArticleList()
        selector.addItems(entries)
        selector.itemSelectionChanged.connect(self.selectionChanged)

        # grid layout for playing items, 10 rows, 10 cols
        layout = qtw.QGridLayout()
        layout.addWidget(selector, 0, 0, 10, 2)
        layout.addWidget(text, 0, 4, 10, 7)

        # h layout for menu
        container = qtw.QWidget()
        container.setObjectName("container")

        menu = qtw.QHBoxLayout()

        logo = qtw.QLabel(text="News")
        logo.setObjectName("logo")
        menu.addWidget(logo)
        b1 = qtw.QPushButton(text="B1")
        b2 = qtw.QPushButton(text="B2")
        b3 = qtw.QPushButton(text="B3")
        b4 = qtw.QPushButton(text="B4")
        menu.addWidget(b1)
        menu.addWidget(b2)
        menu.addWidget(b3)
        menu.addWidget(b4)
        
        container.setLayout(menu)

        # layout of layouts
        superLayout = qtw.QGridLayout()
        superLayout.addWidget(container, 0, 0, 1, 10)
        superLayout.addLayout(layout, 2, 0, 9, 10)

        self.setLayout(superLayout)
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

    def getArticleList(self):
        files = os.listdir("articles")
        articles = []
        for item in files:
            if item.endswith(".html"):
                articles.append(item)
        return articles

    def selectionChanged(self):
        selectedArticle = self.selector.currentItem().text()
        location = "articles/" + selectedArticle
        with open(location, "r") as html:
            self.article.clear()
            self.article.insertHtml(html.read())


    def getStyleSheet(self):
        stylesheet = """
        QWidget {
            background-color: white;
            padding: 0px;
            margin: 0px;
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
            font-size: 20px;
            line-height: 2;
            border-style: none;
            border-right: 1px solid lightgrey;
            spacing: 10;
        }
        QListWidget::Item {
            margin: 10px;
        }
        #logo {
            font-size: 30px;
            font-weight: bold;
        }
        QPushButton {
            height: 50%;
            border-style: none;
            border-right: 1px solid lightgrey;
        }
        #main {
        }
        #container {
            border-bottom: 1px solid lightgrey;
        }"""
        return stylesheet

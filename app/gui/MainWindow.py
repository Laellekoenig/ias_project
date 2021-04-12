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

        self.light = True
        css = self.getLightStyleSheet()
        self.setStyleSheet(css)
        self.setObjectName("main")
        
        #text reader
        text = qtw.QTextBrowser()
        self.article = text
        self.setArticleStyle()
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
        b2 = qtw.QPushButton(text="get new articles")
        b3 = qtw.QPushButton(text="share on BAC-net")
        # TODO b2 and b3 implementation
        b4 = qtw.QPushButton(text="dark")
        b4.clicked.connect(self.switch)
        self.switch = b4
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
        files = os.listdir("data/articles")
        articles = []
        for item in files:
            if item.endswith(".html"):
                articleName = self.getArticleName(item)
                articles.append(articleName)
        return articles

    def selectionChanged(self):
        selectedArticle = self.selector.currentItem().text()
        fileName = self.getFileName(selectedArticle)
        location = "data/articles/" + fileName
        with open(location, "r") as html:
            self.article.clear()
            self.article.insertHtml(html.read())

    def switch(self):
        if self.light:
            self.switch.setText("light")
            css = self.getDarkStyleSheet()
        else:
            self.switch.setText("dark")
            css = self.getLightStyleSheet()
        
        self.setStyleSheet(css)
        self.light = not self.light

    def getArticleName(self, name):
        # cut away .html
        name = name[:-5]
        name = name.replace("_", " ")
        return name

    def getFileName(self, name):
        name = name.replace(" ", "_")
        name += ".html"
        return name

    def setArticleStyle(self):
        self.article.document().setDefaultStyleSheet(
            "body {} "
            "p {font-size: 18px; line-height: 1.5;} "
            "h1 {} "
            "h3 {color: lightgrey;}"
            "h2 {color: grey;}"
        )

    def getLightStyleSheet(self):
        stylesheet = """
        QWidget {
            background-color: white;
            color: black;
            padding: 0px;
            margin: 0px;
        }
        QTextBrowser {
            background-color: white;
            border-style: none;
            border-left: 5px;
            padding-right: 100px;
            padding-left: 50px;
            padding-top: 30px;
        }
        QTextBrowser QScrollBar {
            height: 0px;
            width: 0px;
        }
        QPushButton {
        }
        QListWidget {
            font-family: Roboto;
            font-size: 18px;
            line-height: 2;
            border-style: none;
            spacing: 10;
            padding-left: 10px;
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
        }"""
        return stylesheet

    def getDarkStyleSheet(self):
        stylesheet = """
        QWidget {
            background-color: black;
            color: white;
            padding: 0px;
            margin: 0px;
        }
        QTextBrowser {
            background-color: black;
            color: white;
            border-style: none;
            border-left: 5px;
            padding-right: 100px;
            padding-left: 50px;
            padding-top: 30px;
        }
        QScrollBar {
            height: 0px;
            width: 0px;
        }
        QPushButton {
        }
        QListWidget {
            font-family: Roboto;
            font-size: 18px;
            line-height: 2;
            border-style: none;
            border-right: 1px solid lightgrey;
            spacing: 10;
            padding-left: 10px;
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
    
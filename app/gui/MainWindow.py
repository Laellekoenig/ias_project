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

        self.loadFonts()

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

    def loadFonts(self):
        db = qtg.QFontDatabase()
        walbaum = os.getcwd() + "/data/fonts/Walbaum.ttf"
        merri_light = os.getcwd() + "/data/fonts/Merriweather-Light.ttf"
        merri_regular = os.getcwd() + "/data/fonts/Merriweather-Regular.ttf"
        merri_bold = os.getcwd() + "/data/fonts/Merriweather-Bold.ttf"
        merri_black = os.getcwd() + "/data/fonts/Merriweather-BlackItalic.ttf"
        merri_italic = os.getcwd() + "/data/fonts/Merriweather-Italic.ttf"

        db.addApplicationFont(walbaum)
        db.addApplicationFont(merri_light)
        db.addApplicationFont(merri_regular)
        db.addApplicationFont(merri_bold)
        db.addApplicationFont(merri_black)
        db.addApplicationFont(merri_italic)

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
            "body {font-family: Merriweather;} "
            "p {font-size: 18px; line-height: 1.5; font-weight: 300;} "
            "h1 {font-weight: bold; font-style: italic;} "
            "h3 {color: lightgrey;}"
            "h2 {color: grey;}"
        )

    def getLightStyleSheet(self):
        stylesheet = """
        QWidget {
            background-color: #f7f7f7;
            color: black;
            padding: 0px;
            margin: 0px;
            font-family: Merriweather;
        }
        QTextBrowser {
            background-color: #f7f7f7;
            border-style: none;
            border-left: 5px;
            padding-right: 100px;
            padding-left: 50px;
            padding-top: 10px;
        }
        QTextBrowser QScrollBar {
            height: 0px;
            width: 0px;
        }
        QListWidget QScrollBar {
            height: 0px;
            width: 0px;
        }
        QPushButton {
            font-weight: light;
            font-size: 15px;
        }
        QListWidget {
            font-family: Merriweather;
            font-size: 15px;
            line-height: 2;
            border-style: none;
            spacing: 10;
            padding-left: 10px;
        }
        QListWidget::Item {
            margin: 10px;
        }
        QListWidget::Item:selected {
            color: #f7f7f7;
            background-color: black;
            margin: 0px;
            padding: 0px;
            border-radius: 3px;
        }
        #logo {
            font-size: 40px;
            font-weight: bold;
            font-family: Walbaum Fraktur;
        }
        QPushButton {
            height: 50%;
            border-style: none;
            font-family: Merriweather;
            font-weight: bold;
        }
        #main {
        }
        #container {
            border-bottom: 1px solid lightgrey;
        }"""
        return stylesheet

    def getDarkStyleSheet(self):
        stylesheet = """
        QWidget {
            background-color: #282828;
            color: #f7f7f7;
            padding: 0px;
            margin: 0px;
            font-family: Merriweather;
        }
        QTextBrowser {
            background-color: #282828;
            color: #f7f7f7;
            border-style: none;
            border-left: 5px;
            padding-right: 100px;
            padding-left: 50px;
            padding-top: 10px;
        }
        QTextBrowser QScrollBar {
            height: 0px;
            width: 0px;
        }
        QListWidget QScrollBar {
            height: 0px;
            width: 0px;
        }
        QPushButton {
            font-weight: light;
            font-size: 15px;
        }
        QListWidget {
            font-family: Merriweather;
            font-size: 15px;
            line-height: 2;
            border-style: none;
            spacing: 10;
            padding-left: 10px;
        }
        QListWidget::Item {
            margin: 10px;
        }
        QListWidget::Item:selected {
            color: #282828;
            background-color: #f7f7f7;
            margin: 0px;
            padding: 0px;
            border-radius: 3px;
        }
        #logo {
            font-size: 40px;
            font-weight: bold;
            font-family: Walbaum Fraktur;
        }
        QPushButton {
            height: 50%;
            border-style: none;
            font-family: Merriweather;
            font-weight: bold;
        }
        #main {
        }
        #container {
            border-bottom: 1px solid lightgrey;
        }"""
        return stylesheet
    
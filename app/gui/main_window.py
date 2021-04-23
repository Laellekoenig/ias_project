import sys
import math
import os
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import qtawesome as qta
from gui.interface import Interface

class MainWindow(qtw.QWidget):

    def __init__(self, app):
        # initiate window
        super().__init__(windowTitle="IAS Project")

        # for scraping articles
        self.interface = Interface()

        # load fonts used in ui
        self.loadFonts()

        # start in light theme
        self.light = True
        css = self.getLightStyleSheet()
        self.setStyleSheet(css)

        # used for styling in css
        self.setObjectName("main")

        # grid layout for placing items, 10 rows, 10 cols
        # main part of program
        self.main = qtw.QGridLayout()

        # get menu bar
        menu = self.getMenuBar()

        # start with article view
        self.setReader();

        # master layout with menu, selector and article
        superLayout = qtw.QGridLayout()
        superLayout.setObjectName("super")
        # add menu and main
        superLayout.addWidget(menu, 0, 0, 1, 10)
        superLayout.addLayout(self.main, 2, 0, 9, 10)

        # configure window and application details and show
        self.setLayout(superLayout)
        self.startScreenSize(app)
        self.setMinimumSize(700, 500)
        self.show()

    def loadFonts(self):
        # adds custom fonts to application
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
        # application takes up 70% of screen size on start
        RATIO = 0.7
        w = math.floor(RATIO * w)
        h = math.floor(RATIO * h)
        self.resize(w, h)

    def getMenuBar(self):
        # menu bar on top of screen
        menu = qtw.QHBoxLayout()

        # logo, top left
        logo = qtw.QLabel(text="News")
        logo.setObjectName("logo")
        menu.addWidget(logo)

        # menu items
        # from left to right
        # button 1
        self.b1 = qtw.QPushButton(text="read")
        self.b1.clicked.connect(self.setReader)
        menu.addWidget(self.b1)

        # used for setting style of currently selected section
        self.selected = self.b1

        # button 2
        self.b2 = qtw.QPushButton(text="get new articles")
        self.b2.clicked.connect(self.setArticleDownloader)
        menu.addWidget(self.b2)

        # button3
        self.b3 = qtw.QPushButton(text="share on BAC-net")
        self.b3.clicked.connect(self.setBACNet)
        menu.addWidget(self.b3)

        # button 4
        self.b4 = qtw.QPushButton(text="dark")
        self.b4.clicked.connect(self.switch)
        # switch for changing UI style sheet
        self.switch = self.b4
        menu.addWidget(self.b4)

        # container for menu bar
        container = qtw.QWidget()
        # for styling
        container.setObjectName("container")
        # add menu to container
        container.setLayout(menu)

        return container

    def getArticleList(self):
        # articles must be in data/articles folder
        # must be .html files
        # name will be formatted as follows:
        # generic_article_name.html     ->      generic article name

        files = os.listdir("data/articles")
        articles = []
        for item in files:
            if item.endswith(".html"):
                articleName = self.getArticleName(item)
                articles.append(articleName)
        return articles

    def selectedArticleChanged(self):
        # change displayed article in UI on selection
        selectedArticle = self.selector.currentItem().text()
        fileName = self.getFileName(selectedArticle)
        location = "data/articles/" + fileName
        with open(location, "r") as html:
            self.article.clear()
            self.article.insertHtml(html.read())

    def switch(self):
        # switch from dark to light or vice versa
        if self.light:
            self.switch.setText("light")
            css = self.getDarkStyleSheet()
        else:
            self.switch.setText("dark")
            css = self.getLightStyleSheet()
        
        self.setStyleSheet(css)
        self.light = not self.light

        # update colors of menu bar
        self.setSelected(self.selected)

    def setSelected(self, button):
        self.selected = button
        buttons = [self.b1, self.b2, self.b3, self.b4]
        for b in buttons:
            if (self.light):
                b.setStyleSheet("color: black;")
            else:
                b.setStyleSheet("color: white")

        button.setStyleSheet("color: grey;")

    def setReader(self):
        # clear previous layout
        self.removeWidgets(self.main)

        self.setSelected(self.b1)

        # main article box, HTML reader
        text = qtw.QTextBrowser()
        self.article = text
        # css styling for article
        self.setArticleStyle()
        text.setOpenExternalLinks(True)

        #article selector, LHS of app
        selector = qtw.QListWidget()
        self.selector = selector
        # read articles from /data/articles folder
        entries = self.getArticleList()
        selector.addItems(entries)
        # add event for user input
        selector.itemSelectionChanged.connect(self.selectedArticleChanged)

        # article selector 20% of content
        self.main.addWidget(selector, 0, 0, 10, 2)
        # article 80% of content
        self.main.addWidget(text, 0, 3, 10, 8)

    def downloadArticleSelection(self):
        articles = []
        for article in self.downloadSelector.selectedItems():
            articles.append(article.text())
        self.interface.downloadArticles(articles)

        #remove downloaded articles form list
        for article in self.downloadSelector.selectedItems():
            row = self.downloadSelector.row(article)
            self.downloadSelector.takeItem(row)

    def setArticleDownloader(self):
        # clear main layout
        self.removeWidgets(self.main)
        self.setSelected(self.b2)

        # new widgets
        # title
        title = qtw.QLabel(text="Title")
        title.setObjectName("downloadTitle")

        downloadB = qtw.QPushButton(text="update from SRF")
        #downloadB.clicked.connect()
        downloadB.setObjectName("fillButton")

        # add to layout
        self.main.addWidget(title, 0, 0, 1, 1)
        self.main.addWidget(downloadB, 1, 0)

    def setBACNet(self):
        # clear main layout
        self.removeWidgets(self.main)
        self.setSelected(self.b3)

        # new widgets
        title = qtw.QLabel(text="BAC-NET")

        # add to layout
        self.main.addWidget(title)

    def removeWidgets(self, layout):
        for i in reversed(range(layout.count())):
            try:
                layout.itemAt(i).widget().setParent(None)
            except:
                layout.itemAt(i).layout().setParent(None)

    def getArticleName(self, name):
        # cut away .html
        name = name[:-5]
        # format name:  article_name -> article name
        name = name.replace("_", " ")
        return name

    def getFileName(self, name):
        # article name  -> article_name ->  article_name.html
        name = name.replace(" ", "_")
        name += ".html"
        return name

    def setArticleStyle(self):
        # style sheet for displayed article
        self.article.document().setDefaultStyleSheet(
            "body {font-family: Merriweather;} "
            "p {font-size: 18px; line-height: 1.5; font-weight: 300;} "
            "h1 {font-weight: bold; font-style: italic;} "
            "h3 {color: lightgrey;}"
            "h2 {color: grey;}"
        )

    def getLightStyleSheet(self):
        # light mode style sheet
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
        }
        #selected {
            color: red;
        }
        #fillButton {
            background-color: #AF011E;
            color: white;
            border-radius: 3px;
        }
        #fillButton:pressed {
            background-color: white;
            color: #AF011E;
            border-style: solid;
            border-width: 1px;
            border-color: #AF011E;
        }
        #downloadTitle {
            font-size: 20px;
        }"""
        return stylesheet

    def getDarkStyleSheet(self):
        # dark mode style sheet
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
        }
        #fillButton {
            background-color: #AF011E;
            color: #f7f7f7;
            border-radius: 3px;
            border-style: none;
        }
        #fillButton:pressed {
            background-color: #f7f7f7;
            color: #AF011E;
            border-style: solid;
            border-width: 1px;
            border-color: #AF011E;
        }"""
        return stylesheet
    
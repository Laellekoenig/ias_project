import os
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import qtawesome as qta
from gui.interface import Interface
import gui.utils as utils
import gui.style as style

class MainWindow(qtw.QWidget):

    def __init__(self, app):
        # initiate window
        super().__init__(windowTitle="IAS Project")

        # for interacting with other parts of program
        self.interface = Interface()

        # load fonts used in ui
        utils.load_fonts()

        # start in light theme
        self.light = True
        self.setStyleSheet(style.getLightStyleSheet())

        # used for styling in css
        self.setObjectName("main")

        # grid layout for placing items, 10 rows, 10 cols
        # main part of program
        self.main = qtw.QGridLayout()

        # get menu bar
        menu = self.get_menu_bar()

        # start with article view
        self.set_reading_section()

        # master layout with menu and active section
        superLayout = qtw.QGridLayout()
        superLayout.setObjectName("super")
        # add menu and main
        superLayout.addWidget(menu, 0, 0, 1, 10)
        superLayout.addLayout(self.main, 2, 0, 9, 10)

        # configure window and application details and show
        self.setLayout(superLayout)
        utils.starting_screen_size(self, app)
        self.setMinimumSize(700, 500)
        self.show()

    # menu bar of app
    def get_menu_bar(self):
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
        self.b1.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.b1.clicked.connect(self.set_reading_section)
        menu.addWidget(self.b1)

        # used for setting style of currently selected section
        self.selected = self.b1

        # button 2
        self.b2 = qtw.QPushButton(text="get new articles")
        self.b2.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.b2.clicked.connect(self.set_downloading_section)
        menu.addWidget(self.b2)

        # button3
        self.b3 = qtw.QPushButton(text="archive")
        self.b3.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.b3.clicked.connect(self.set_archiving_section)
        menu.addWidget(self.b3)

        # button 4
        self.b4 = qtw.QPushButton(text="dark")
        self.b4.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
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

    # main reading section of app
    def set_reading_section(self):
        # clear previous layout
        utils.remove_widgets(self.main)

        self.set_selected_menu_button(self.b1)

        # main article box, HTML reader
        text = qtw.QTextBrowser()
        self.article = text
        # css styling for article
        style.setArticleStyle(self.article)
        text.setOpenExternalLinks(True)

        #article selector, LHS of app
        selector = qtw.QListWidget()
        self.selector = selector
        # read articles from /data/articles folder
        entries = self.interface.get_downloaded_articles()
        selector.addItems(entries)
        # add event for user input
        selector.itemSelectionChanged.connect(self.selected_article_changed)
        # start with first article selected
        selector.setCurrentRow(0)
        # move cursor to start of text
        text.moveCursor(qtg.QTextCursor.Start)

        # article selector 20% of content
        self.main.addWidget(selector, 0, 0, 10, 2)
        # article 80% of content
        self.main.addWidget(text, 0, 3, 10, 8)

    # downloading and sharing section of app
    def set_downloading_section(self):
        # clear main layout
        utils.remove_widgets(self.main)
        self.set_selected_menu_button(self.b2)

        # new widgets
        downLayout = qtw.QVBoxLayout()
        downLayout.setContentsMargins(200, 30, 200, 0)
        toggleLayout = qtw.QHBoxLayout()

        toggle = qtw.QPushButton(text="download")
        toggle.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        toggle.setCheckable(True)
        toggle.setChecked(True)
        toggle.clicked.connect(self.toggle_download)
        toggle.setObjectName("toggleActive")
        self.toggle = toggle

        toggle2 = qtw.QPushButton(text="share")
        toggle2.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        toggle2.setCheckable(True)
        toggle2.setChecked(False)
        toggle2.clicked.connect(self.toggle2_download)
        toggle2.setObjectName("toggleFalse")
        self.toggle2 = toggle2

        toggleLayout.addWidget(toggle)
        toggleLayout.addWidget(toggle2)

        srfB = qtw.QPushButton(text="SRF")
        srfB.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        srfB.clicked.connect(self.interface.threaded_download)
        srfB.setObjectName("srfButton")

        blueB = qtw.QPushButton(text="bluetooth")
        blueB.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        #blueB.clicked.connect()
        blueB.setObjectName("blueButton")

        bacB = qtw.QPushButton(text="BAC-Net")
        bacB.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        # bacB.clicked.connect()
        bacB.setObjectName("bacButton")

        localB = qtw.QPushButton(text="local network")
        localB.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        # localB.clicked.connect()
        localB.setObjectName("bacButton")

        # add to download layout
        downLayout.addLayout(toggleLayout)
        downLayout.addWidget(srfB)
        downLayout.addWidget(bacB)
        downLayout.addWidget(blueB)
        downLayout.addWidget(localB)
        downLayout.addStretch()

        # add to layout
        self.main.addLayout(downLayout, 0, 0)

    # archive section of app
    def set_archiving_section(self):
        # clear main layout
        utils.remove_widgets(self.main)
        self.set_selected_menu_button(self.b3)

        # new widgets
        title = qtw.QLabel(text="archive")

        # add to layout
        self.main.addWidget(title)

    def selected_article_changed(self):
        # change displayed article in UI on selection
        selectedArticle = self.selector.currentItem().text()
        html = self.interface.get_article_html_by_title(selectedArticle)
        self.article.clear()
        self.article.insertHtml(html)
        #fileName = utils.get_file_name(selectedArticle)
        #location = "data/articles/" + fileName
        #with open(location, "r") as html:
            #self.article.clear()
            #self.article.insertHtml(html.read())

    def switch(self):
        # switch from dark to light or vice versa
        if self.light:
            self.switch.setText("light")
            css = style.getDarkStyleSheet()
        else:
            self.switch.setText("dark")
            css = style.getLightStyleSheet()
        
        self.setStyleSheet(css)
        self.light = not self.light

        # update colors of menu bar
        self.set_selected_menu_button(self.selected)

    def set_selected_menu_button(self, button):
        self.selected = button
        buttons = [self.b1, self.b2, self.b3, self.b4]
        for b in buttons:
            if (self.light):
                b.setStyleSheet("color: black;")
            else:
                b.setStyleSheet("color: white")

        button.setStyleSheet("color: grey;")

    def toggle_download(self):
        if self.toggle.isChecked():
            self.toggle.setObjectName("toggleTrue")
            self.toggle2.setChecked(False)
            self.toggle2.setObjectName("toggleFalse")
            if self.light:
                self.toggle.setStyleSheet("color: black;")
                self.toggle2.setStyleSheet("color: grey;")
            else:
                self.toggle.setStyleSheet("color: #f7f7f7;")
                self.toggle2.setStyleSheet("color: grey;")
        else:
            self.toggle.setChecked(True)

    def toggle2_download(self):
        if self.toggle2.isChecked():
            self.toggle2.setObjectName("toggleTrue")
            self.toggle.setChecked(False)
            self.toggle.setObjectName("toggleFalse")
            if self.light:
                self.toggle2.setStyleSheet("color: black;")
                self.toggle.setStyleSheet("color: grey;")
            else:
                self.toggle2.setStyleSheet("color: #f7f7f7;")
                self.toggle.setStyleSheet("color: grey;")
        else:
            self.toggle2.setChecked(True)

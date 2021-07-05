import os
import socket
import threading
import time
import queue

import PyQt5.QtCore
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import qtawesome as qta
from logic.article import Category
from gui.interface import Interface
from logic.interface import LogicInterface as Logic
import gui.utils as utils
import gui.style as style
import transfer.local_network as net
import transfer.bluetooth as tooth
from transfer.LAN_server import LANServer
from transfer.LAN_client import LANClient
from transfer.bt_server import bt_server as BTServer
from transfer.bt_client import bt_client as BTClient

class imageLabel(qtw.QLabel):
    clicked = qtc.pyqtSignal()
    def mouseReleaseEvent(self, ev):
        if ev.button() == qtc.Qt.LeftButton:
            self.clicked.emit()

class downloadingThread(qtc.QThread):
    def __init__(self, logic):
        super().__init__()
        self.logic = logic

    def run(self) -> None:
        self.logic.download_new_articles()
        #self.finished.emit()

class MainWindow(qtw.QWidget):

    def __init__(self, app):
        # diverse inits
        self.server_socket = None
        self.active_article_filter = None
        self.today_btn = None
        self.week_btn = None
        self.all_btn = None
        self.downLayout = None
        self.srfBtn = None
        self.bookmark = None
        self.bookmark_gif = None
        self.bookmark_active = False
        self.archive_selector = None
        self.archive_reader = None
        self.mdi_btn = None
        self.combo = None
        self.current_title = None
        self.downloading_thread = None

        # initiate window
        super().__init__(windowTitle="IAS Project")

        # shortcuts
        self.shortcut_book = qtw.QShortcut(qtg.QKeySequence("Ctrl+B"), self)
        self.shortcut_book.activated.connect(self.update_bookmark)

        # for interacting with other parts of program
        self.interface = Interface(self)
        self.logic = Logic()
        self.LAN_client = LANClient()
        self.LAN_server = LANServer()
        self.BT_server = BTServer()
        self.BT_client = BTClient()

        # load app icons
        utils.load_app_icons(app)

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
        #used for moving elements from one thread to another
        self.original_thread = self.main.thread()

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

    def closeEvent(self, event):
        self.LAN_server.stop_server()
        self.BT_server.stop_server()

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
        self.tab_changed()

        self.set_selected_menu_button(self.b1)

        # bookmark button before text to avoid errors when opening app
        #bookmark = qtw.QPushButton()
        #bookmark.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        #bookmark.setObjectName("bookmark")
        #bookmark.clicked.connect(self.play_bookmark)

        #bookmark_gif = qtg.QMovie(os.getcwd() + "/data/images/bookmark-animated.gif")
        #bookmark_gif.jumpToFrame(0)
        #bookmark_gif.frameChanged.connect(self.update_bookmark)
        #pixmap = bookmark_gif.currentPixmap()
        #bookmark.setIcon(qtg.QIcon(pixmap))
        #bookmark.setIconSize(qtc.QSize(40, 40))

        #self.bookmark = bookmark
        #self.bookmark_gif = bookmark_gif

        # main article box, HTML reader
        text = qtw.QTextBrowser()
        self.article = text
        # css styling for article
        style.setArticleStyle(self.article)
        text.setOpenExternalLinks(True)

        #article selector, LHS of app
        selector = qtw.QListWidget()
        self.selector = selector
        selector.setWordWrap(True)
        # read articles from /data/articles folder
        entries = self.get_article_lst()
        selector.addItems(entries)
        # add event for user input
        selector.itemSelectionChanged.connect(self.selected_article_changed)
        # start with first article selected
        selector.setCurrentRow(0)
        # move cursor to start of text
        text.moveCursor(qtg.QTextCursor.Start)

        bookmark = imageLabel()
        self.bookmark = bookmark
        bookmark.setFixedSize(50, 50)
        bookmark.setObjectName("bookmark")
        bookmark.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        bookmark.clicked.connect(self.update_bookmark)
        self.draw_bookmark()

        #test
        mdi_book = qta.icon("mdi.bookmark-outline", color="black")
        mdi_book_btn = qtw.QPushButton()
        mdi_book_btn.setObjectName("bookmark-btn")
        mdi_book_btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        mdi_book_btn.clicked.connect(self.update_bookmark)
        mdi_book_btn.setIconSize(qtc.QSize(40, 40))
        mdi_book_btn.setIcon(mdi_book)
        self.mdi_btn = mdi_book_btn
        self.draw_bookmark()

        #article filters
        self.today_btn = qtw.QPushButton(text="today")
        self.today_btn.setObjectName("filter-btn-selected")
        self.today_btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.today_btn.clicked.connect(self.switch_today)
        self.active_article_filter = self.today_btn

        self.week_btn = qtw.QPushButton(text="week")
        self.week_btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.week_btn.clicked.connect(self.switch_week)
        self.week_btn.setObjectName("filter-btn")

        self.all_btn = qtw.QPushButton(text = "all")
        self.all_btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.all_btn.clicked.connect(self.switch_all)
        self.all_btn.setObjectName("filter-btn")

        filter_layout = qtw.QHBoxLayout()
        filter_layout.setObjectName("filter-layout")
        filter_layout.addWidget(self.today_btn)
        filter_layout.addWidget(self.week_btn)
        filter_layout.addWidget(self.all_btn)

        # category chooser
        combo = qtw.QComboBox()
        combo.setObjectName("combo")
        combo.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        combo.addItem("All Categories")
        combo.addItem("Switzerland")
        combo.addItem("International")
        combo.addItem("Economics")
        combo.addItem("Culture")
        combo.addItem("Sports")
        combo.addItem("Meteo")
        combo.addItem("Panorama")
        combo.activated[str].connect(self.combo_selection_changed)
        self.combo = combo

        lhs_layout = qtw.QVBoxLayout()
        lhs_layout.addLayout(filter_layout)
        lhs_layout.addWidget(combo)
        lhs_layout.addWidget(selector)

        rhs_layout = qtw.QVBoxLayout()
        #rhs_layout.addWidget(bookmark)
        rhs_layout.addWidget(mdi_book_btn)
        rhs_layout.addStretch()

        # article selector 20% of content
        self.main.addLayout(lhs_layout, 0, 0, 100, 20)
        # article 80% of content
        self.main.addWidget(text, 0, 20, 100, 75)
        # bookmarks etc.
        self.main.addLayout(rhs_layout, 0, 95, 100, 5)

    # downloading and sharing section of app
    def set_downloading_section(self):
        if self.logic.is_updating:
            self.set_loading_screen_section()
            return
        self.tab_changed()

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
        toggle.setObjectName("toggleTrue")
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
        srfB.clicked.connect(self.handle_download)
        srfB.setObjectName("srfButton")

        blueB = qtw.QPushButton(text="bluetooth")
        blueB.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        blueB.clicked.connect(self.switch_blue)
        blueB.setObjectName("blueButton")

        bacB = qtw.QPushButton(text="BAC-Net")
        bacB.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        # bacB.clicked.connect()
        bacB.setObjectName("bacButton")

        localB = qtw.QPushButton(text="local network")
        localB.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        localB.clicked.connect(self.switch_wlan)
        localB.setObjectName("bacButton")

        on_macOS = self.BT_server.on_macOS()

        # add to download layout
        downLayout.addLayout(toggleLayout)
        downLayout.addWidget(srfB)
        downLayout.addWidget(bacB)

        #if not on_macOS:
        #    downLayout.addWidget(blueB)
        # for testing:
        downLayout.addWidget(blueB)

        downLayout.addWidget(localB)
        downLayout.addStretch()

        self.downLayout = downLayout
        self.srfBtn = srfB

        # add to layout
        self.main.addLayout(downLayout, 0, 0)

    def set_loading_screen_section(self):
        utils.remove_widgets(self.main)
        self.set_selected_menu_button(self.b2)
        self.tab_changed()

        #new widgets
        layout = qtw.QVBoxLayout()
        centering_layout = qtw.QHBoxLayout()

        if self.light:
            gif_path = os.getcwd() + "/data/images/loading_light.gif"
        else:
            gif_path = os.getcwd() + "/data/images/loading_dark.gif"
        loading = qtg.QMovie(gif_path)

        loading_label = qtw.QLabel()
        loading_label.setObjectName("gif")
        loading_label.setMovie(loading)
        loading.start()

        layout.addStretch()
        layout.addWidget(loading_label)
        layout.addStretch()

        centering_layout.addStretch()
        centering_layout.addWidget(loading_label)
        centering_layout.addStretch()

        self.main.addLayout(centering_layout, 0, 0)

    # archive section of app
    def set_archiving_section(self):
        # clear main layout
        utils.remove_widgets(self.main)
        self.set_selected_menu_button(self.b3)
        self.tab_changed()

        text = qtw.QTextBrowser()
        style.setArticleStyle(text)
        text.setOpenExternalLinks(True)
        self.archive_reader = text

        selector = qtw.QListWidget()
        self.selector = selector
        selector.setWordWrap(True)
        entries = self.get_bookmarked_article_lst()
        selector.addItems(entries)
        selector.itemSelectionChanged.connect(self.archive_article_changed)
        selector.setCurrentRow(0)
        text.moveCursor(qtg.QTextCursor.Start)

        mdi_book = qta.icon("mdi.bookmark-outline", color="black")
        mdi_book_btn = qtw.QPushButton()
        mdi_book_btn.setObjectName("bookmark-btn")
        mdi_book_btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        mdi_book_btn.clicked.connect(self.update_bookmark)
        mdi_book_btn.setIconSize(qtc.QSize(40, 40))
        mdi_book_btn.setIcon(mdi_book)
        self.mdi_btn = mdi_book_btn
        self.draw_bookmark()

        rhs_layout = qtw.QVBoxLayout()
        rhs_layout.addWidget(mdi_book_btn)
        rhs_layout.addStretch()

        self.main.addWidget(selector, 0, 0, 100, 20)
        self.main.addWidget(text, 0, 20, 100, 75)
        self.main.addLayout(rhs_layout, 0, 95, 100, 5)

    def selected_article_changed(self):
        # change displayed article in UI on selection
        selectedArticle = self.selector.currentItem().text()
        # remove new indication
        if selectedArticle.startswith("\u2022"):
            unmarked = selectedArticle[2:]
            self.selector.currentItem().setText(unmarked)

        html = self.logic.get_article_html_by_title1(selectedArticle)
        self.article.clear()
        self.article.insertHtml(html)
        is_bookmarked = self.logic.is_article_bookmarked(selectedArticle)
        if is_bookmarked:
            self.fill_mdi()
        else:
            self.draw_mdi_outline()
        #mark as read
        self.logic.mark_as_opened(selectedArticle)
        self.current_title = selectedArticle

    def archive_article_changed(self):
        selectedArticle = self.selector.currentItem().text()
        self.current_title = selectedArticle
        html = self.logic.get_article_html_by_title1(selectedArticle)
        self.archive_reader.clear()
        self.archive_reader.insertHtml(html)
        #TODO bookmarks
        is_bookmarked = self.logic.is_article_bookmarked(selectedArticle)
        if is_bookmarked:
            self.fill_mdi()
        else:
            self.draw_mdi_outline()

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

        if self.selected == self.b2 and self.logic.is_updating:
            self.set_loading_screen_section()

        #update bookmark color
        self.draw_bookmark()
        self.update_switches()

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
                self.toggle.setStyleSheet("color: grey;")
                self.toggle2.setStyleSheet("color: black;")
            else:
                self.toggle.setStyleSheet("color: grey;")
                self.toggle2.setStyleSheet("color: #f7f7f7;")
        else:
            self.toggle.setChecked(True)

        self.set_downloading_section()

    def toggle2_download(self):
        if self.toggle2.isChecked():
            self.toggle2.setObjectName("toggleTrue")
            self.toggle.setChecked(False)
            self.toggle.setObjectName("toggleFalse")
            if self.light:
                self.toggle2.setStyleSheet("color: grey;")
                self.toggle.setStyleSheet("color: black;")
            else:
                self.toggle2.setStyleSheet("color: grey;")
                self.toggle.setStyleSheet("color: #f7f7f7;")
        else:
            self.toggle2.setChecked(True)
        if not self.srfBtn == None:
            self.downLayout.removeWidget(self.srfBtn)
            self.srfBtn = None

    def switch_to_loading(self):
        if self.selected == self.b2:
            self.set_loading_screen_section()

    def finished_downloading(self):
        print(self.selected)
        if self.selected == self.b2:
            self.set_downloading_section()

    def handle_download(self):
        self.set_loading_screen_section()
        self.downloading_thread = downloadingThread(self.logic)
        self.downloading_thread.start()
        self.downloading_thread.finished.connect(self.set_reading_section)

    def switch_wlan(self):
        if self.toggle.isChecked():
            self.set_wlan_client_section()
        else:
            self.set_wlan_server_section()

    def switch_blue(self):
        if self.toggle.isChecked():
            self.set_blue_client_section()
        else:
            self.set_blue_server_section()

    def set_wlan_server_section(self):
        self.tab_changed()
        self.LAN_server.keep_alive()
        utils.remove_widgets(self.main)
        self.srfBtn = None
        self.set_selected_menu_button(self.b2)

        if not self.LAN_server.is_running():
            self.LAN_server.start_server_threaded()

        while not self.LAN_server.is_running():
            pass

        s1 = "Your IP address is: "
        t1 = qtw.QLabel(s1)
        t1.setObjectName("server-text")

        s2 = self.LAN_server.get_IP()
        t2 = qtw.QLabel(s1 + s2)
        t2.setObjectName("server-text")

        lanLayout = qtw.QVBoxLayout()
        lanLayout.addStretch()
        #lanLayout.addWidget(t1)
        lanLayout.addWidget(t2)
        #lanLayout.addWidget(t3)
        lanLayout.addStretch()

        horizontalLayout = qtw.QHBoxLayout()
        horizontalLayout.addStretch()
        horizontalLayout.addLayout(lanLayout)
        horizontalLayout.addStretch()

        self.main.addLayout(horizontalLayout, 0, 0)

    def set_wlan_client_section(self):
        utils.remove_widgets(self.main)
        self.set_selected_menu_button(self.b2)
        self.tab_changed()
        title = qtw.QLabel(text="Server selection:")
        title.setObjectName("lan-title")

        devices = net.get_devices()
        ip = []
        for d in devices:
            ip_addr = d["ip"]
            name = d["name"]
            entry = ip_addr + "\t" + name
            ip.append(entry)

        lst = qtw.QListWidget()
        lst.addItems(ip)
        lst.setCurrentRow(0)
        self.serverLst = lst

        connect_btn = qtw.QPushButton(text="connect")
        connect_btn.setObjectName("bacButton")
        connect_btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        connect_btn.clicked.connect(self.connect)

        btns = qtw.QHBoxLayout()
        btns.addWidget(connect_btn)

        lanLayout = qtw.QVBoxLayout()
        lanLayout.addWidget(title)
        lanLayout.addWidget(lst)
        lanLayout.addLayout(btns)

        self.main.addLayout(lanLayout, 0, 0)

    def connect(self):
        ip = self.serverLst.currentItem().text()
        ip = ip.split("\t")[0]
        print("trying to connect to " + ip)
        self.LAN_client.start_client_threaded(ip)
        self.set_LAN_loading_screen()

    def set_blue_server_section(self):
        self.tab_changed()
        utils.remove_widgets(self.main)
        self.srfBtn = None
        self.set_selected_menu_button(self.b2)

        on_macOS = self.BT_server.on_macOS()

        if not on_macOS:
            if not self.BT_server.is_running():
                self.BT_server.start_server_threaded()

            while not self.BT_server.is_running():
                pass

        s1 = "Your MAC-address is: "
        s2 = self.BT_server.get_mac_address()
        label = qtw.QLabel(s1 + s2)
        label.setObjectName("server-text")

        s2 = "MacOS bluetooth transfer is not supported."
        label2 = qtw.QLabel(s2)
        label2.setObjectName("server-text")

        BTLayout = qtw.QVBoxLayout()
        BTLayout.addStretch()
        if not on_macOS:
            BTLayout.addWidget(label)
        else:
            BTLayout.addWidget(label2)
        BTLayout.addStretch()

        horizontalLayout = qtw.QHBoxLayout()
        horizontalLayout.addStretch()
        horizontalLayout.addLayout(BTLayout)
        horizontalLayout.addStretch()

        self.main.addLayout(horizontalLayout, 0, 0)

    def set_blue_client_section(self):
        self.tab_changed()
        utils.remove_widgets(self.main)
        self.set_selected_menu_button(self.b2)

        label = qtw.QLabel("Enter partner's MAC-address:")
        label.setObjectName("client-text")

        input = qtw.QLineEdit()
        input.setAttribute(qtc.Qt.WA_MacShowFocusRect, 0)
        regex = qtc.QRegExp("^([0-9A-Fa-f]{2}[-:]){5}([0-9A-Fa-f]{2})$")
        input.setValidator(qtg.QRegExpValidator(regex))
        input.setAlignment(qtc.Qt.AlignCenter)

        btn = qtw.QPushButton("connect")
        btn.setObjectName("bt-client-btn")
        btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        #btn.clicked.connect(TODO)

        layout = qtw.QVBoxLayout()
        layout.addStretch()
        layout.addWidget(label)
        layout.addWidget(input)
        layout.addWidget(btn)
        layout.addStretch()

        horizontal = qtw.QHBoxLayout()
        horizontal.addStretch()
        horizontal.addLayout(layout)
        horizontal.addStretch()

        self.main.addLayout(horizontal, 0, 0)

    def close_connections(self):
        if self.server_socket != None:
            self.server_socket.stop_server()
            self.server_socket = None

    def switch_today(self):
        self.active_article_filter.setStyleSheet("color: black; height: 20%;")
        if not self.light:
            self.active_article_filter.setStyleSheet("color: #f7f7f7; height: 20%;")
        self.active_article_filter.setObjectName("filter-btn")
        self.active_article_filter = self.today_btn
        self.today_btn.setStyleSheet("color: grey; height: 20%;")
        self.today_btn.setObjectName("filter-btn-active")
        self.update_article_list()

        self.combo_selection_changed(None)
        self.selector.setCurrentRow(0)

    def switch_week(self):
        self.active_article_filter.setStyleSheet("color: black; height: 20%;")
        if not self.light:
            self.active_article_filter.setStyleSheet("color: #f7f7f7; height: 20%;")
        self.active_article_filter.setObjectName("filter-btn")
        self.active_article_filter = self.week_btn
        self.week_btn.setStyleSheet("color: grey; height: 20%;")
        self.week_btn.setObjectName("filter-btn-active")
        self.update_article_list()

        self.combo_selection_changed(None)
        self.selector.setCurrentRow(0)

    def switch_all(self):
        active_item = self.selector.currentItem()
        self.active_article_filter.setStyleSheet("color: black; height: 20%;")
        if not self.light:
            self.active_article_filter.setStyleSheet("color: #f7f7f7; height: 20%;")
        self.active_article_filter.setObjectName("filter-btn")
        self.active_article_filter = self.all_btn
        self.all_btn.setStyleSheet("color: grey; height: 20%;")
        self.all_btn.setObjectName("filter-btn-active")
        self.update_article_list()

        self.combo_selection_changed(None)
        self.selector.setCurrentRow(0)

    def update_style(self):
        if self.light:
            self.setStyleSheet(style.getLightStyleSheet())
        else:
            self.setStyleSheet(style.getDarkStyleSheet())

    def get_article_lst(self):
        if self.active_article_filter == self.today_btn:
            return self.logic.get_article_titles_today()
        if self.active_article_filter == self.week_btn:
            return self.logic.get_article_titles_week()
        else:
            return self.logic.get_article_titles()

    def get_bookmarked_article_lst(self):
        lst = self.logic.get_bookmarked_article_titles()
        return lst

    def update_article_list(self):
        entries = self.get_article_lst()
        self.selector.clear()
        self.selector.addItems(entries)

    def set_bookmark(self):
        if self.bookmark == None:
            return
        self.bookmark.setPixmap(qtg.QPixmap(os.getcwd() + "/data/images/bookmark-filled.png"))

    def remove_bookmark(self):
        if self.bookmark == None:
            return
        self.bookmark.setPixmap(qtg.QPixmap(os.getcwd() + "/data/images/bookmark-empty.png"))

    def update_bookmark(self):
        #if self.selector.currentItem() == None:
        #    return
        #title = self.selector.currentItem().text()
        title = utils.remove_dot(self.current_title)
        if title == None:
            return
        active = self.logic.is_article_bookmarked(title)
        if active:
            self.logic.remove_bookmark_article(title)
            self.draw_mdi_outline()
        else:
            self.logic.bookmark_article(title)
            self.fill_mdi()

        #if in archive update selector
        if self.selected == self.b3:
            entries = self.get_bookmarked_article_lst()
            self.selector.clear()
            self.selector.addItems(entries)

    def draw_bookmark(self):
        if self.selector.currentItem() == None:
            return
        title = self.selector.currentItem().text()
        active = self.logic.is_article_bookmarked(title)
        if active:
            self.fill_mdi()
        else:
            self.draw_mdi_outline()

    def draw_mdi_outline(self):
        if self.mdi_btn == None:
            return
        if self.light:
            icon = qta.icon("mdi.bookmark-outline", color="black")
        else:
            icon = qta.icon("mdi.bookmark-outline", color="#f7f7f7")
        self.mdi_btn.setIcon(icon)

    def fill_mdi(self):
        if self.mdi_btn == None:
            return
        if self.light:
            icon = qta.icon("mdi.bookmark", color="black")
        else:
            icon = qta.icon("mdi.bookmark", color="#f7f7f7")
        self.mdi_btn.setIcon(icon)

    def combo_selection_changed(self, category):
        if category == None:
            category = str(self.combo.currentText())

        titles = self.get_article_lst()

        if category == "All Categories":
            self.update_article_list()
            return
        elif category == "Switzerland":
            new_lst = self.logic.filter_by_category(titles, Category.SWITZERLAND)
        elif category == "International":
            new_lst = self.logic.filter_by_category(titles, Category.INTERNATIONAL)
        elif category == "Economics":
            new_lst = self.logic.filter_by_category(titles, Category.ECONOMICS)
        elif category == "Culture":
            new_lst = self.logic.filter_by_category(titles, Category.CULTURE)
        elif category == "Sports":
            new_lst = self.logic.filter_by_category(titles, Category.SPORTS)
        elif category == "Meteo":
            new_lst = self.logic.filter_by_category(titles, Category.METEO)
        elif category == "Panorama":
            new_lst = self.logic.filter_by_category(titles, Category.PANORAMA)

        self.selector.clear()
        self.selector.addItems(new_lst)

    def update_switches(self):
        if self.light:
            if self.active_article_filter == self.today_btn:
                self.today_btn.setStyleSheet("color: grey; height: 20%;")
                self.week_btn.setStyleSheet("color: black; height: 20%;")
                self.all_btn.setStyleSheet("color: black; height: 20%;")
            if self.active_article_filter == self.week_btn:
                self.today_btn.setStyleSheet("color: black; height: 20%;")
                self.week_btn.setStyleSheet("color: grey; height: 20%;")
                self.all_btn.setStyleSheet("color: black; height: 20%;")
            if self.active_article_filter == self.all_btn:
                self.today_btn.setStyleSheet("color: black; height: 20%;")
                self.week_btn.setStyleSheet("color: black; height: 20%;")
                self.all_btn.setStyleSheet("color: grey; height: 20%;")
        else:
            if self.active_article_filter == self.today_btn:
                self.today_btn.setStyleSheet("color: grey; height: 20%;")
                self.week_btn.setStyleSheet("color: #f7f7f7; height: 20%;")
                self.all_btn.setStyleSheet("color: #f7f7f7; height: 20%;")
            if self.active_article_filter == self.week_btn:
                self.today_btn.setStyleSheet("color: #f7f7f7; height: 20%;")
                self.week_btn.setStyleSheet("color: grey; height: 20%;")
                self.all_btn.setStyleSheet("color: #f7f7f7; height: 20%;")
            if self.active_article_filter == self.all_btn:
                self.today_btn.setStyleSheet("color: #f7f7f7; height: 20%;")
                self.week_btn.setStyleSheet("color: #f7f7f7; height: 20%;")
                self.all_btn.setStyleSheet("color: grey; height: 20%;")

    def tab_changed(self):
        self.LAN_server.stop_server()
        self.BT_server.stop_server()

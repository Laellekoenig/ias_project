import os
import socket
import threading

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import qtawesome as qta
from gui.interface import Interface
from logic.interface import LogicInterface as Logic
import gui.utils as utils
import gui.style as style
import transfer.local_network as net
import transfer.bluetooth as tooth
import transfer.LAN_server as net1

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

        # initiate window
        super().__init__(windowTitle="IAS Project")

        # for interacting with other parts of program
        self.interface = Interface(self)
        self.logic = Logic()

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
        self.close_connections()

        self.set_selected_menu_button(self.b1)

        # bookmark button before text to avoid errors when opening app
        bookmark = qtw.QPushButton()
        bookmark.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        bookmark.setObjectName("bookmark")
        bookmark.clicked.connect(self.play_bookmark)

        bookmark_gif = qtg.QMovie(os.getcwd() + "/data/images/bookmark-animated.gif")
        bookmark_gif.jumpToFrame(0)
        bookmark_gif.frameChanged.connect(self.update_bookmark)
        pixmap = bookmark_gif.currentPixmap()
        bookmark.setIcon(qtg.QIcon(pixmap))
        bookmark.setIconSize(qtc.QSize(40, 40))

        self.bookmark = bookmark
        self.bookmark_gif = bookmark_gif

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

        lhs_layout = qtw.QVBoxLayout()
        lhs_layout.addLayout(filter_layout)
        lhs_layout.addWidget(selector)

        rhs_layout = qtw.QVBoxLayout()
        rhs_layout.addWidget(bookmark)
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
        #blueB.clicked.connect(self.switch_blue)
        blueB.setObjectName("blueButton")

        bacB = qtw.QPushButton(text="BAC-Net")
        bacB.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        # bacB.clicked.connect()
        bacB.setObjectName("bacButton")

        localB = qtw.QPushButton(text="local network")
        localB.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        localB.clicked.connect(self.switch_wlan)
        localB.setObjectName("bacButton")

        # add to download layout
        downLayout.addLayout(toggleLayout)
        downLayout.addWidget(srfB)
        downLayout.addWidget(bacB)
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

        # new widgets
        title = qtw.QLabel(text="archive")

        # add to layout
        self.main.addWidget(title)

    def selected_article_changed(self):
        # change displayed article in UI on selection
        selectedArticle = self.selector.currentItem().text()
        html = self.logic.get_article_html_by_title1(selectedArticle)
        self.article.clear()
        self.article.insertHtml(html)
        is_bookmarked = self.logic.is_article_bookmarked(selectedArticle)
        print(is_bookmarked)
        if is_bookmarked:
            self.set_bookmark()
        else:
            self.remove_bookmark()
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

        if self.selected == self.b2 and self.logic.is_updating:
            self.set_loading_screen_section()

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

        self.downLayout.insertWidget(1, self.srfBtn)

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
        self.downLayout.removeWidget(self.srfBtn)

    def switch_to_loading(self):
        if self.selected == self.b2:
            self.set_loading_screen_section()

    def finished_downloading(self):
        print(self.selected)
        if self.selected == self.b2:
            self.set_downloading_section()

    def handle_download(self):
        self.logic.download_new_articles()
        self.set_loading_screen_section()

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
        utils.remove_widgets(self.main)
        self.srfBtn = None
        self.set_selected_menu_button(self.b2)

        self.server_socket = net1.LANServer()
        self.server_socket.start_server_threaded()

        while not self.server_socket.running:
            pass

        s1 = "Started server on"
        t1 = qtw.QLabel(s1)
        t1.setObjectName("server-text")

        s2 = self.server_socket.get_IP()
        t2 = qtw.QLabel(s1 + " " + s2)
        t2.setObjectName("server-text")

        s3 = "with port number"
        t3 = qtw.QLabel(s3)
        t3.setObjectName("server-text")

        s4 = self.server_socket.get_port() + "."
        t4 = qtw.QLabel(s3 + " " + s4)
        t4.setObjectName("server-text")

        lanLayout = qtw.QVBoxLayout()
        lanLayout.addStretch()
        #lanLayout.addWidget(t1)
        lanLayout.addWidget(t2)
        #lanLayout.addWidget(t3)
        lanLayout.addWidget(t4)
        lanLayout.addStretch()

        horizontalLayout = qtw.QHBoxLayout()
        horizontalLayout.addStretch()
        horizontalLayout.addLayout(lanLayout)
        horizontalLayout.addStretch()

        self.main.addLayout(horizontalLayout, 0, 0)

    def set_wlan_client_section(self):
        utils.remove_widgets(self.main)
        self.set_selected_menu_button(self.b2)

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
        net.start_client_threaded(ip)

    def set_blue_server_section(self):

        text = qtw.QLabel("server")

        layout = qtw.QVBoxLayout()
        layout.addWidget(text)

        self.main.addLayout(layout, 0, 0)

        tooth.start_server()

    def set_blue_client_section(self):

        text = qtw.QLabel("client")

        layout = qtw.QVBoxLayout()
        layout.addWidget(text)

        self.main.addLayout(layout, 0, 0)

        tooth.start_client()

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

    def update_article_list(self):
        entries = self.get_article_lst()
        self.selector.clear()
        self.selector.addItems(entries)

    def play_bookmark(self):
        current_title = self.selector.currentItem().text()
        if not self.bookmark_active:
            self.bookmark_active = True
            self.logic.bookmark_article(current_title)
            self.bookmark_gif.start()
            thread = threading.Thread(target=self.wait_end_animation)
            thread.start()
        else:
            self.bookmark_active = False
            self.logic.remove_bookmark_article(current_title)
            self.bookmark_gif.jumpToFrame(self.bookmark_gif.frameCount() / 2)
            self.bookmark_gif.start()
            thread = threading.Thread(target=self.wait_start_animation)
            thread.start()

    def wait_end_animation(self):
        end_frame = self.bookmark_gif.frameCount()
        end_frame /= 2
        while (self.bookmark_gif.currentFrameNumber() < end_frame - 1):
            pass
        self.bookmark_gif.stop()

    def wait_start_animation(self):
        while (self.bookmark_gif.currentFrameNumber() != 0):
            pass
        self.bookmark_gif.stop()

    def set_bookmark(self):
        self.bookmark_active = True
        #TODO set book mark icon

    def remove_bookmark(self):
        self.bookmark_active = False
        #TODO remove book mark icon

    def update_bookmark(self):
        pixmap = self.bookmark_gif.currentPixmap()
        icon = qtg.QIcon(pixmap)
        self.bookmark.setIcon(icon)

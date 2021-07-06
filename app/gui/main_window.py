# -- standard python --
import os
# -- PyQt --
import qtawesome as qta
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
# -- own classes --
import gui.utils as utils
import gui.style as style
import transfer.local_network as net
from logic.article import Category
from logic.interface import LogicInterface as Logic
from gui.interface import Interface
from transfer.LAN_server import LANServer
from transfer.LAN_client import LANClient
from transfer.bt_server import bt_server as BTServer
from transfer.bt_client import bt_client as BTClient

# own label class that can be clicked like a QPushButton
class imageLabel(qtw.QLabel):
    clicked = qtc.pyqtSignal()
    def mouseReleaseEvent(self, ev):
        if ev.button() == qtc.Qt.LeftButton:
            self.clicked.emit()

# QThread that downloads articles via logic.download_new_articles
class downloadingThread(qtc.QThread):
    def __init__(self, logic):
        super().__init__()
        self.logic = logic

    def run(self):
        self.logic.download_new_articles()

# QThread that downloads articles via LAN connection
class LANThread(qtc.QThread):
    def __init__(self, LAN_client, ip):
        super().__init__()
        self.LAN_client = LAN_client
        self.ip = ip

    def run(self):
        self.LAN_client.start_client(self.ip)

# QThread that downloads articles via Bluetooth connection
class BTThread(qtc.QThread):
    def __init__(self, BT_client, mac):
        super().__init__()
        self.BT_client = BT_client
        self.mac = mac

    def run(self):
        self.BT_client.start_client(self.mac)

# main GUI class
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
        self.lan_thread = None
        self.lan_is_downloading = False
        self.MAC_input = None
        self.BT_thread = None

        # initiate window
        super().__init__(windowTitle="IAS Project")

        # keyboard shortcuts
        self.shortcut_book = qtw.QShortcut(qtg.QKeySequence("Ctrl+B"), self)
        self.shortcut_book.activated.connect(self.update_bookmark)

        # for interacting with back-end
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

        # grid layout for placing items, 100 rows, 100 cols
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
        superLayout.addWidget(menu, 0, 0, 10, 100)
        superLayout.addLayout(self.main, 10, 0, 90, 100)

        # configure window and application details and show
        self.setLayout(superLayout)
        utils.starting_screen_size(self, app)
        self.setMinimumSize(700, 500)
        self.show()

    # if application is closed
    def closeEvent(self, event):
        # stop diverse servers
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
        # button 1 -- reading section
        self.b1 = qtw.QPushButton(text="read")
        self.b1.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.b1.clicked.connect(self.set_reading_section)
        menu.addWidget(self.b1)

        # used for setting style of currently selected section
        self.selected = self.b1

        # button 2 -- downloading section
        self.b2 = qtw.QPushButton(text="get new articles")
        self.b2.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.b2.clicked.connect(self.set_downloading_section)
        menu.addWidget(self.b2)

        # button3 -- archive section
        self.b3 = qtw.QPushButton(text="archive")
        self.b3.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.b3.clicked.connect(self.set_archiving_section)
        menu.addWidget(self.b3)

        # button 4 -- dark/light mode toggle
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
        self.tab_changed()
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

        # bookmark for moving articles to archive section
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
        # start with "today" article filter
        self.active_article_filter = self.today_btn

        self.week_btn = qtw.QPushButton(text="week")
        self.week_btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.week_btn.clicked.connect(self.switch_week)
        self.week_btn.setObjectName("filter-btn")

        self.all_btn = qtw.QPushButton(text="all")
        self.all_btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        self.all_btn.clicked.connect(self.switch_all)
        self.all_btn.setObjectName("filter-btn")

        filter_layout = qtw.QHBoxLayout()
        filter_layout.setObjectName("filter-layout")
        filter_layout.addWidget(self.today_btn)
        filter_layout.addWidget(self.week_btn)
        filter_layout.addWidget(self.all_btn)
        # -- end of filters --

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
        # if selection changed
        combo.activated[str].connect(self.filter_selection_changed)
        self.combo = combo

        # left of article reader
        lhs_layout = qtw.QVBoxLayout()
        lhs_layout.addLayout(filter_layout)
        lhs_layout.addWidget(combo)
        lhs_layout.addWidget(selector)

        # right of article reader
        rhs_layout = qtw.QVBoxLayout()
        rhs_layout.addWidget(mdi_book_btn)
        rhs_layout.addStretch()

        # article selector 20% of content
        self.main.addLayout(lhs_layout, 0, 0, 100, 20)
        # article 75% of content
        self.main.addWidget(text, 0, 20, 100, 75)
        # bookmarks etc. 5% of content
        self.main.addLayout(rhs_layout, 0, 95, 100, 5)

    # downloading and sharing section of app
    def set_downloading_section(self):
        if self.logic.is_updating or self.lan_is_downloading:
            # show loading screen if currently downloading
            self.set_loading_screen_section()
            return

        # clear main layout
        self.tab_changed()
        self.set_selected_menu_button(self.b2)

        # layouts
        downLayout = qtw.QVBoxLayout()
        downLayout.setContentsMargins(200, 30, 200, 0)
        toggleLayout = qtw.QHBoxLayout()

        # -- begin toggles for switching between sharing and downloading --
        toggle = qtw.QPushButton(text="download")
        toggle.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        toggle.setCheckable(True)
        # start in downloading mode
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
        # -- end of toggles --

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
        #TODO bacB.clicked.connect()
        bacB.setObjectName("bacButton")

        localB = qtw.QPushButton(text="local network")
        localB.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        localB.clicked.connect(self.switch_wlan)
        localB.setObjectName("bacButton")

        # add buttons to download layout
        downLayout.addLayout(toggleLayout)
        downLayout.addWidget(srfB)
        downLayout.addWidget(bacB)

        on_macOS = self.BT_server.on_macOS()

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

    # downloading animation
    def set_loading_screen_section(self):
        # reset layout
        self.tab_changed()
        self.set_selected_menu_button(self.b2)

        #new layouts
        layout = qtw.QVBoxLayout()
        centering_layout = qtw.QHBoxLayout()

        # get correct gif
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

    # LAN server UI
    def set_lan_server_section(self):
        self.tab_changed()
        self.set_selected_menu_button(self.b2)

        # don't kill open server
        self.LAN_server.keep_alive()

        # open a new server if no already running
        if not self.LAN_server.is_running():
            self.LAN_server.start_server_threaded()

        # wait for server to run
        while not self.LAN_server.is_running():
            pass

        # widgets
        text = "Your IP address is: "
        address = self.LAN_server.get_IP()
        label = qtw.QLabel(text + address)
        label.setObjectName("server-text")

        lanLayout = qtw.QVBoxLayout()
        lanLayout.addStretch()
        lanLayout.addWidget(label)
        lanLayout.addStretch()

        horizontalLayout = qtw.QHBoxLayout()
        horizontalLayout.addStretch()
        horizontalLayout.addLayout(lanLayout)
        horizontalLayout.addStretch()

        self.main.addLayout(horizontalLayout, 0, 0)

    # LAN client UI
    def set_lan_client_section(self):
        self.tab_changed()
        self.set_selected_menu_button(self.b2)

        # widgets
        title = qtw.QLabel(text="Server selection:")
        title.setObjectName("lan-title")

        # get list of devices
        devices = net.get_devices()
        ip = []
        for d in devices:
            ip_addr = d["ip"]
            name = d["name"]
            entry = ip_addr + "\t" + name
            ip.append(entry)

        # display devices in list widget
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

    # bluetooth server UI
    def set_blue_server_section(self):
        self.tab_changed()
        self.set_selected_menu_button(self.b2)

        # bluetooth sockets do not work on macOS
        on_macOS = self.BT_server.on_macOS()

        # keep server alive if open
        self.BT_server.keep_alive()

        if not on_macOS:
            if not self.BT_server.is_running():
                # not on mac -> open socket
                self.BT_server.start_server_threaded()

            # wait for server to run
            while not self.BT_server.is_running():
                pass

        # not displayed on macOS
        text = "Your MAC-address is: "
        address = self.BT_server.get_mac_address()
        label = qtw.QLabel(text + address)
        label.setObjectName("server-text")

        # only displayed on macOS
        text2 = "MacOS bluetooth transfer is not supported."
        label2 = qtw.QLabel(text2)
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

    # bluetooth client UI
    def set_blue_client_section(self):
        self.tab_changed()
        self.set_selected_menu_button(self.b2)

        label = qtw.QLabel("Enter partner's MAC-address:")
        label.setObjectName("client-text")

        input = qtw.QLineEdit()
        input.setAttribute(qtc.Qt.WA_MacShowFocusRect, 0)
        # only allow input of valid MAC addresses
        regex = qtc.QRegExp("^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$")
        input.setValidator(qtg.QRegExpValidator(regex))
        input.setAlignment(qtc.Qt.AlignCenter)
        self.MAC_input = input

        btn = qtw.QPushButton("connect")
        btn.setObjectName("bt-client-btn")
        btn.setCursor(qtg.QCursor(qtc.Qt.PointingHandCursor))
        btn.clicked.connect(self.handle_BT_client)

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

    # archive section of app
    def set_archiving_section(self):
        # clear main layout
        self.tab_changed()
        self.set_selected_menu_button(self.b3)

        # article reader
        text = qtw.QTextBrowser()
        style.setArticleStyle(text)
        text.setOpenExternalLinks(True)
        self.archive_reader = text

        # article selector
        selector = qtw.QListWidget()
        self.selector = selector
        selector.setWordWrap(True)
        # only bookmarked articles
        entries = self.get_bookmarked_article_lst()
        selector.addItems(entries)
        selector.itemSelectionChanged.connect(self.archive_article_changed)
        selector.setCurrentRow(0)
        text.moveCursor(qtg.QTextCursor.Start)

        # bookmark btn
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

    # if selected article in article selector changes
    # used in reading section
    def selected_article_changed(self):
        # change displayed article in UI on selection
        selectedArticle = self.selector.currentItem().text()

        # remove "new article" indication
        if selectedArticle.startswith("\u2022"):
            unmarked = selectedArticle[2:]
            self.selector.currentItem().setText(unmarked)

        # set article to reader
        html = self.logic.get_article_html_by_title1(selectedArticle)
        self.article.clear()
        self.article.insertHtml(html)

        # check article bookmark status
        is_bookmarked = self.logic.is_article_bookmarked(selectedArticle)
        if is_bookmarked:
            self.fill_mdi()
        else:
            self.draw_mdi_outline()

        #mark as read
        self.logic.mark_as_opened(selectedArticle)
        self.current_title = selectedArticle

    # if selected article in article selector changes
    # used in archive section
    def archive_article_changed(self):
        # get new article title
        selectedArticle = self.selector.currentItem().text()
        self.current_title = selectedArticle

        # get html of article and set it to reader
        html = self.logic.get_article_html_by_title1(selectedArticle)
        self.archive_reader.clear()
        self.archive_reader.insertHtml(html)

        # check bookmark status
        is_bookmarked = self.logic.is_article_bookmarked(selectedArticle)
        if is_bookmarked:
            self.fill_mdi()
        else:
            self.draw_mdi_outline()

    # used for switching between dark/light mode
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

        # if currently in downloading screen, get new gif
        if self.selected == self.b2 and self.logic.is_updating:
            self.set_loading_screen_section()

        if self.selected == self.b2 and self.lan_is_downloading:
            self.set_loading_screen_section()

        # update bookmark color
        self.draw_bookmark()
        # update filter color
        self.update_switches()

    # set the currently selected button and set correct color
    def set_selected_menu_button(self, button):
        self.selected = button
        buttons = [self.b1, self.b2, self.b3, self.b4]
        for b in buttons:
            if (self.light):
                b.setStyleSheet("color: black;")
            else:
                b.setStyleSheet("color: white")

        button.setStyleSheet("color: grey;")

    # switch between downloading/sharing mode in downloading section
    def toggle_download(self):
        # switch toggles
        if self.toggle.isChecked():
            self.toggle.setObjectName("toggleTrue")
            self.toggle2.setChecked(False)
            self.toggle2.setObjectName("toggleFalse")

            # set correct style
            if self.light:
                self.toggle.setStyleSheet("color: grey;")
                self.toggle2.setStyleSheet("color: black;")
            else:
                self.toggle.setStyleSheet("color: grey;")
                self.toggle2.setStyleSheet("color: #f7f7f7;")
        else:
            # if already activated toggle was selected, reactivate
            self.toggle.setChecked(True)

        # refresh section
        self.set_downloading_section()

    # switch between downloading/sharing mode in downloading section
    def toggle2_download(self):
        # switch toggles
        if self.toggle2.isChecked():
            self.toggle2.setObjectName("toggleTrue")
            self.toggle.setChecked(False)
            self.toggle.setObjectName("toggleFalse")

            # set correct style
            if self.light:
                self.toggle2.setStyleSheet("color: grey;")
                self.toggle.setStyleSheet("color: black;")
            else:
                self.toggle2.setStyleSheet("color: grey;")
                self.toggle.setStyleSheet("color: #f7f7f7;")
        else:
            # reactivate if already active toggle selected
            self.toggle2.setChecked(True)

        # remove srf button in sharing mode
        if not self.srfBtn == None:
            self.downLayout.removeWidget(self.srfBtn)
            self.srfBtn = None

    # activated if srf button is clicked
    # download new articles
    def handle_download(self):
        # set loading screen
        self.set_loading_screen_section()
        # create and start downloadingThread
        self.downloading_thread = downloadingThread(self.logic)
        self.downloading_thread.start()
        # switch to reading section when finished downloading
        self.downloading_thread.finished.connect(self.set_reading_section)

    def handle_BT_client(self):
        mac = self.MAC_input.text()
        if len(mac) == 17:
            self.set_loading_screen_section()
            self.BT_thread = BTThread(self.BT_client, mac)
            self.BT_thread.start()
            self.BT_thread.finished.connect(self.set_reading_section)
        else:
            info = qtw.QMessageBox()
            info.setText("Invalid MAC address.")
            info.setWindowTitle("Invalid")
            info.exec_()

    # check current mode downloading/sharing and select corresponding action
    def switch_wlan(self):
        if self.toggle.isChecked():
            self.set_lan_client_section()
        else:
            self.set_lan_server_section()

    # check current mode downloading/sharing and select corresponding action
    def switch_blue(self):
        if self.toggle.isChecked():
            self.set_blue_client_section()
        else:
            self.set_blue_server_section()

    # used in LAN client UI
    # connect to selected IP address
    def connect(self):
        ip = self.serverLst.currentItem().text()
        ip = ip.split("\t")[0]
        print("trying to connect to " + ip)
        self.set_loading_screen_section()
        self.lan_thread = LANThread(self.LAN_client, ip)
        self.lan_thread.start()
        self.lan_is_downloading = True
        self.lan_thread.finished.connect(self.finished_lan_download)

    # used after lan download finishes, turns off loading screen
    def finished_lan_download(self):
        self.lan_is_downloading = False
        self.set_reading_section()
        print("done")

    # switch active article filter to "today"
    def switch_today(self):
        # update style of items
        self.active_article_filter.setStyleSheet("color: black; height: 20%;")
        if not self.light:
            self.active_article_filter.setStyleSheet("color: #f7f7f7; height: 20%;")
        self.active_article_filter.setObjectName("filter-btn")
        self.active_article_filter = self.today_btn
        self.today_btn.setStyleSheet("color: grey; height: 20%;")
        self.today_btn.setObjectName("filter-btn-active")

        # update article selection according to filter
        self.filter_selection_changed(None)
        self.selector.setCurrentRow(0)

    # switch active article filter to "week"
    def switch_week(self):
        # update style of items
        self.active_article_filter.setStyleSheet("color: black; height: 20%;")
        if not self.light:
            self.active_article_filter.setStyleSheet("color: #f7f7f7; height: 20%;")
        self.active_article_filter.setObjectName("filter-btn")
        self.active_article_filter = self.week_btn
        self.week_btn.setStyleSheet("color: grey; height: 20%;")
        self.week_btn.setObjectName("filter-btn-active")

        # update article list
        self.filter_selection_changed(None)
        self.selector.setCurrentRow(0)

    # switch active article filter to "all"
    def switch_all(self):
        # update style of items
        self.active_article_filter.setStyleSheet("color: black; height: 20%;")
        if not self.light:
            self.active_article_filter.setStyleSheet("color: #f7f7f7; height: 20%;")
        self.active_article_filter.setObjectName("filter-btn")
        self.active_article_filter = self.all_btn
        self.all_btn.setStyleSheet("color: grey; height: 20%;")
        self.all_btn.setObjectName("filter-btn-active")

        # update entries in article selector
        self.filter_selection_changed(None)
        self.selector.setCurrentRow(0)

    # update stylesheet of main window according to mode
    def update_style(self):
        if self.light:
            self.setStyleSheet(style.getLightStyleSheet())
        else:
            self.setStyleSheet(style.getDarkStyleSheet())

    # get article list according to active filter
    def get_article_lst(self):
        if self.active_article_filter == self.today_btn:
            return self.logic.get_article_titles_today()
        if self.active_article_filter == self.week_btn:
            return self.logic.get_article_titles_week()
        else:
            return self.logic.get_article_titles()

    # get list of all bookmarked articles
    def get_bookmarked_article_lst(self):
        lst = self.logic.get_bookmarked_article_titles()
        return lst

    # get list of all articles and set it to selector
    # not paying attention to filter
    def update_article_list(self):
        entries = self.get_article_lst()
        self.selector.clear()
        self.selector.addItems(entries)

    # updates the bookmark icon after clicking on it
    # also communicates with back-end to update article bookmark in json files
    def update_bookmark(self):
        # get title without reading indication
        title = utils.remove_dot(self.current_title)
        if title == None:
            # nothing to bookmark
            return

        # check if article is bookmarked
        active = self.logic.is_article_bookmarked(title)
        # send bookmark info to back-end and update icon
        if active:
            self.logic.remove_bookmark_article(title)
            self.draw_mdi_outline()
        else:
            self.logic.bookmark_article(title)
            self.fill_mdi()

        # if in archive section: update selector
        if self.selected == self.b3:
            entries = self.get_bookmarked_article_lst()
            self.selector.clear()
            self.selector.addItems(entries)

    # draws the appropriate bookmark icon, considering bookmark status
    def draw_bookmark(self):
        if self.selector.currentItem() == None:
            # nothing to bookmark
            return

        # get current title and check if active
        title = self.selector.currentItem().text()
        active = self.logic.is_article_bookmarked(title)

        if active:
            self.fill_mdi()
        else:
            self.draw_mdi_outline()

    # draws empty bookmark -> not bookmarked, considers dark/light mode
    def draw_mdi_outline(self):
        if self.mdi_btn == None:
            # nothing to bookmark
            return

        if self.light:
            icon = qta.icon("mdi.bookmark-outline", color="black")
        else:
            icon = qta.icon("mdi.bookmark-outline", color="#f7f7f7")
        self.mdi_btn.setIcon(icon)

    # draws full bookmark -> bookmarked, considers dark/light mode
    def fill_mdi(self):
        if self.mdi_btn == None:
            # nothing to bookmark
            return

        if self.light:
            icon = qta.icon("mdi.bookmark", color="black")
        else:
            icon = qta.icon("mdi.bookmark", color="#f7f7f7")
        self.mdi_btn.setIcon(icon)

    # on category filter change
    # get correct articles and display them in selector
    def filter_selection_changed(self, category):
        if category == None:
            # if not given, get active filter from combo box
            category = str(self.combo.currentText())

        # get artcile list, considering time filter (today, week, all)
        titles = self.get_article_lst()

        # apply category filter to list
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

    # update style of time filter switches considering dark/light mode and active switch
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

    # reset window on section change
    def tab_changed(self):
        # clear window
        utils.remove_widgets(self.main)
        # stop active servers
        self.LAN_server.stop_server()
        self.BT_server.stop_server()

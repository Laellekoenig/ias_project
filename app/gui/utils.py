import os
import math
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

def load_fonts():
    # adds custom fonts to application
    db = qtg.QFontDatabase()
    walbaum = os.getcwd() + "/data/fonts/Walbaum.ttf"
    merri_light = os.getcwd() + "/data/fonts/Merriweather-Light.ttf"
    merri_regular = os.getcwd() + "/data/fonts/Merriweather-Regular.ttf"
    merri_bold = os.getcwd() + "/data/fonts/Merriweather-Bold.ttf"
    merri_black = os.getcwd() + "/data/fonts/Merriweather-BlackItalic.ttf"
    merri_italic = os.getcwd() + "/data/fonts/Merriweather-Italic.ttf"
    assistant = os.getcwd() + "/data/fonts/Assistant.ttf"

    db.addApplicationFont(walbaum)
    db.addApplicationFont(merri_light)
    db.addApplicationFont(merri_regular)
    db.addApplicationFont(merri_bold)
    db.addApplicationFont(merri_black)
    db.addApplicationFont(merri_italic)
    db.addApplicationFont(assistant)
    return

def get_screen_size(app):
    screen = app.primaryScreen()
    size = screen.size()
    w = size.width()
    h = size.height()
    return (w, h)

def starting_screen_size(window, app):
    w, h = get_screen_size(app)
    # application takes up 70% of screen size on start
    RATIO = 0.7
    w = math.floor(RATIO * w)
    h = math.floor(RATIO * h)
    window.resize(w, h)
    return

def get_article_list():
    # articles must be in data/articles folder
    # must be .html files
    # name will be formatted as follows:
    # generic_article_name.html     ->      generic article name

    files = os.listdir("data/articles")
    articles = []
    for item in files:
        if item.endswith(".html"):
            articleName = get_article_name(item)
            articles.append(articleName)
    return articles

def get_article_name(name):
    # cut away .html
    name = name[:-5]
    # format name:  article_name -> article name
    name = name.replace("_", " ")
    return name

def get_file_name(name):
    # article name  -> article_name ->  article_name.html
    name = name.replace(" ", "_")
    name += ".html"
    return name

def remove_widgets(layout):
    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)

        # not ideal but seems to work
        if str(type(item)) == "<class 'PyQt5.QtWidgets.QWidgetItem'>":
            item.widget().setParent(None)
        else:
            if str(type(item)) != "<class 'PyQt5.QtWidgets.QSpacerItem'>":
                remove_widgets(item)
                item.layout().setParent(None)
    return

def load_app_icons(app):
    app_icon = qtg.QIcon()
    path = os.getcwd() + "/data/images/"
    app_icon.addFile(path + "16x16.png", qtc.QSize(16, 16))
    app_icon.addFile(path + "24x24.png", qtc.QSize(24, 24))
    app_icon.addFile(path + "32x32.png", qtc.QSize(32, 32))
    app_icon.addFile(path + "48x48.png", qtc.QSize(48, 48))
    app_icon.addFile(path + "256x256.png", qtc.QSize(256, 256))
    app.setWindowIcon(app_icon)

def get_items_from_list_widget(widget):
    lst = []
    for i in range(widget.count() - 1):
        lst.append(widget.item(i).text())

    return lst

def remove_dot(title):
    if not title.endswith("\u2022"):
        return title
    else:
        return title[:-2]

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

def setArticleStyle(article):
    # style sheet for displayed article
    article.document().setDefaultStyleSheet(
        "body {font-family: Merriweather;} "
        "p {font-size: 18px; line-height: 1.5; font-weight: 300;} "
        "h1 {font-weight: bold; font-style: italic;} "
        "h3 {color: lightgrey;}"
        "h2 {color: grey;}"
    )
    return

def getLightStyleSheet():
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
        font-family: Assistant;
        font-weight: 400;
        font-size: 18px;
        line-height: 2;
        border-style: none;
        spacing: 10;
    }
    QListWidget::Item {
        padding-top: 5px;
        padding-bottom: 5px;  
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
        font-family: Assistant;
        font-weight: 500;
        font-size: 16px;
    }
    #main {
    }
    #container {
        border-bottom: 1px solid lightgrey;
    }
    #selected {
        color: red;
    }
    #srfButton {
        background-color: #AF011E;
        color: white;
        border-radius: 3px;
    }
    #srfButton:pressed {
        background-color: white;
        color: #AF011E;
        border-style: solid;
        border-width: 1px;
        border-color: #AF011E;
    }
    #blueButton {
        background-color: #0C3C91;
        color: white;
        border-radius: 3px;
    }
    #blueButton:pressed {
        background-color: white;
        color: #0C3C91;
        border-style: solid;
        border-width: 1px;
        border-color: #0C3C91;
    }
    #downloadTitle {
        font-size: 20px;
    }
    #toggleTrue {
        color: black;
    }
    #toggleFalse {
        color: grey;
    }
    #bacButton {
        color: white;
        background-color: black;
        border-radius: 3px;
        border-style: none;
    }
    #bacButton:pressed {
        color: black;
        background-color: white;
        border-style: solid;
        border-width: 1px;
        border-color: black;
    }"""
    return stylesheet

def getDarkStyleSheet():
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
        font-size: 16px;
    }
    QListWidget {
        font-family: Assistant;
        font-weight: 400;
        font-size: 18px;
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
        font-family: Assistant;
        font-weight: 500;
        font-size 18px;
    }
    #main {
    }
    #container {
        border-bottom: 1px solid lightgrey;
    }
    #srfButton {
        background-color: #f7f7f7;
        color: #AF011E;
        border-radius: 3px;
        border-style: none;
    }
    #srfButton:pressed {
        background-color: #AF011E;
        color: #f7f7f7;
        border-style: solid;
        border-width: 1px;
        border-color: #f7f7f7;
    }
    #blueButton {
        background-color: #f7f7f7;
        color: #0C3C91;
        border-radius: 3px;
    }
    #blueButton:pressed {
        background-color: #0C3C91;
        color: #f7f7f7;
        border-style: solid;
        border-width: 1px;
        border-color: #f7f7f7;
    }
    #downloadTitle {
        font-size: 20px;
    }
    #toggleTrue {
        color: #f7f7f7;
    }
    #toggleFalse {
        color: grey;
    }
    #bacButton {
        color: #282828;
        background-color: #f7f7f7;
        border-radius: 3px;
        border-style: none;
    }
    #bacButton:pressed {
        color: #f7f7f7;
        background-color: #282828;
        border-style: solid;
        border-width: 1px;
        border-color: #f7f7f7;
    }"""
    return stylesheet

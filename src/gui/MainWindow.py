import sys
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

class MainWindow(qtw.QWidget):

    def __init__(self):
        # initiate window
        super().__init__(windowTitle="IAS Project")
        
        # grid layout for playing items
        layout = qtw.QGridLayout()
        self.setLayout(layout)

        self.show()

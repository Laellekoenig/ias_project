import sys
from gui.MainWindow import MainWindow
from PyQt5 import QtWidgets as qtw

app = qtw.QApplication(sys.argv)
mainWindow = MainWindow()
app.exec()
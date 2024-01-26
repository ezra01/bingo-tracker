import sys
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QDialog,
    QFileDialog,
    QGridLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QMainWindow
)
from PyQt5.uic import loadUi
from PyQt5.QtGui import (
    QPixmap,
    QActionEvent
)
from pathlib import Path
class MainWindow(QDialog):
    def __init__ (self):
        super(MainWindow,self).__init__()
        loadUi("gui.ui",self)
        self.browse_button.clicked.connect(self.browse_files)


    def browse_files(self):
        file_names= QFileDialog.getOpenFileName(self, 'Open file', 'C:\\Users', 'Images (*.png *.jpg *.jpeg)' )
        self.filename.setText(file_names[0])
        #display
        pixmap = QPixmap(file_names[0])
        self.pic_label.resize(pixmap.width(),pixmap.height())
        self.pic_label.setPixmap(pixmap)
        self.adjustSize()


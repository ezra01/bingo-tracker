import sys
from PyQt5.QtCore import QThread, QRect, QObject,pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QDialog,
    QFileDialog,
    QGridLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QMainWindow,
    QStackedWidget
)
from PyQt5.uic import loadUi
from PyQt5.QtGui import (
    QPixmap,QActionEvent
)
import main

class MainWindow(QDialog):
    def __init__ (self):
        super(MainWindow,self).__init__()
        loadUi("gui.ui",self)
        self.browse_button.clicked.connect(self.gui_browse_files)
        self.analyze_button.clicked.connect(self.gui_analyze)

        # Swap Buttons for testing
        #self.browse_button.clicked.connect(self.test_btn)


    def gui_browse_files(self):
        file_names = QFileDialog.getOpenFileName(self, 'Open file', 'C:\\Users', 'Images (*.png *.jpg *.jpeg)')
        self.filename_line.setText(str(file_names[0]))
        #self.filename.isReadOnly(True)
        # display
        pixmap = QPixmap(file_names[0])
        self.pic_label.resize(pixmap.width(), pixmap.height())
        self.pic_label.setPixmap(pixmap)
        self.adjustSize()
        self.analyze_button.setEnabled(True)

    def gui_analyze(self):
        self.thread = QThread()
        self.worker = Worker(self.filename_line.text(),bool(self.isDebug_btn.isChecked() ))
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        self.analyze_button.setEnabled(False)
        self.thread.finished.connect(lambda: self.analyze_button.setEnabled(True))
    def test_btn(self):
        print(self.isDebug_btn.isChecked())


class Worker(QObject):
    finished = pyqtSignal()
    def __init__(self, filename_line ="helloworld", isDebug = False ):
        QObject.__init__(self)
        self.filename = filename_line
        self.isDebug = isDebug
    def run(self):
        "Task"
        lin = ['62', '47', '34', '29', '13', '67', '58', '45', '16', '3', '63', '57', '22', '15', '73', '53', '38',
               '20', '10', '68', '60', '35', '23', '2']
        number_calls = ['62', '13', '67', '58', '22', '15', '20', '10', '2']
        #main.getWinningNumbers(lin)

        main.read_text(self.filename,self.isDebug)
        self.finished.emit()



if __name__ == '__main__':
    app = QApplication([])
    WINDOW = MainWindow()
    widget = QStackedWidget()
    widget.addWidget(WINDOW)
    widget.setMinimumSize(500,500)
    widget.show()
    app.exec()
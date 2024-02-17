
from PyQt5.QtCore import QThread, QThreadPool, QRect, QObject,pyqtSignal,Qt
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QDialog,
    QFileDialog,
    QGridLayout,
    QPushButton,
    QLabel,
    QListWidget, QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QTableView,
    QTableWidget, QTableWidgetItem
)
from PyQt5.uic import loadUi
from PyQt5.QtGui import (
    QPixmap,QActionEvent,QColor
)
import sys, traceback, main, config
import numpy as np
from gameCard import GameCard


class MainWindow(QDialog):
    def __init__ (self):
        super(MainWindow,self).__init__()
        loadUi("gui.ui",self)
        self.browse_button.clicked.connect(self.gui_browse_files)
        self.analyze_button.clicked.connect(self.gui_analyze)
        self.isDebug_btn.stateChanged.connect(lambda: config.flipDebug() )
        self.myCards = []
        self.currentVisualCard = self.dial
        self.itemCallsList= set()
        self.tabWidget.tabBarClicked.connect(self.refresh_my_cards)
        self.card_list_widget.itemClicked.connect(self.make_visual_card)
        self.line_edit_calls.returnPressed.connect(self.add_line_call)
        self.rand_call_btn.clicked.connect(self.add_random_call)
        self.rand_card_btn.clicked.connect(self.add_random_card)
        # Swap Buttons for testing
        #self.browse_button.clicked.connect(self.test_btn)


    def add_random_card(self):
        randomCard= GameCard("Card "+ str(len(self.myCards)+1) )
        randomCard.randomize()
        self.add_bingo_card(randomCard)
        self.refresh_my_cards(1)


    def add_random_call(self):
        if len(self.itemCallsList)!= 75:
            unusedCallsList = [x for x in range(1,76)]
            unusedCallsList = list(set(unusedCallsList) - set(self.itemCallsList))
            tempNum =config.RAND.choice(unusedCallsList)
            while tempNum in self.itemCallsList:
                tempNum = config.choice(unusedCallsList)

            self.insert_calls(str(tempNum))
        else:
            #Error no more calls availble
            #print("Tried to add random call")
            pass

    def add_line_call(self):
        s=(self.line_edit_calls.text()).strip()
        self.insert_calls(s)
    def insert_calls(self,s):
            # updates list of calls
        if s.isnumeric():
            s=int(s)
            self.line_edit_calls.clear()
            self.calls_list_widget.addItem(str(s))
            self.itemCallsList.add(int(s))

            # check current card, Refresh visual representation
            if self.currentVisualCard.verticalHeaderItem(1) is  None:
                counter = 0
                for q in range(self.currentVisualCard.columnCount() ):
                    for p in range(self.currentVisualCard.columnCount() ):
                        #print("p={0} , q={1}, box={2} ".format(q,p,(self.currentVisualCard.item(p,q).text()) ))
                        if self.currentVisualCard.item(q, p).text() == "Free" or self.currentVisualCard.item(q, p).text()==-1:
                            self.currentVisualCard.item(q, p).setBackground(QColor(0, 200, 0, 127))
                        else:
                            if int(self.currentVisualCard.item(q, p).text()) in self.itemCallsList:
                                self.currentVisualCard.item(q, p).setBackground(QColor(0, 200, 0, 127))
                        counter += 1
            # check for winner bingo cards
            if len(self.itemCallsList)>=4: #arrsize
                self.check_all_cards()



            else:
                pass
        else:
             pass



    def make_visual_card(self, item):
            # creates visual representation for selected bingoCard
        myGameCard=item.data(config.CustomObjectRole)
        lin=myGameCard.getNumbers()
        mTable = QTableWidget()
        myHeader = ["B","I","N","G","O"]
        l = len(lin) + 1
        lin.insert(l // 2, -1)
        arrSize = int(np.sqrt(l + 1))
        mTable.setRowCount(arrSize)
        mTable.setColumnCount(arrSize)
        while len(myHeader) < arrSize:
            myHeader.append("O")
        mTable.setHorizontalHeaderLabels(myHeader)

        counter=0
        for q in range(arrSize):
            for p in range(arrSize):
                #print("p={0} , q={1}, box={2} ".format(q,p,lin[counter]))
                if lin[counter] ==-1:
                    mTable.setItem(q, p, QTableWidgetItem(str("Free") ))
                    mTable.item(q, p).setBackground(QColor(0,200,0,127))
                else:
                    mTable.setItem(q,p,QTableWidgetItem (str(lin[counter]) ))
                    if int(lin[counter]) in self.itemCallsList:
                        mTable.item(q, p).setBackground(QColor(0,200,0,127))
                counter+=1
        
        #mTable.setItem(1, 1, QTableWidgetItem("t"))
        #containingLayout = self.tableView.parent().layout()
        self.gridLayout.replaceWidget(self.currentVisualCard,mTable)
        self.currentVisualCard=mTable


    def refresh_my_cards(self,tabIndex):
            #  updates list of bingo cards.
            # Will update on change of tab
        if tabIndex ==1:
            self.card_list_widget.clear()
            for k, v in enumerate (self.myCards):
                tempItem = QListWidgetItem()
                tempItem.setText(str(k+1)+" . "+v.getImgPath())
                tempItem.setData(config.CustomObjectRole,v)
                #check all cards for winners
                if v.isWinner(self.itemCallsList):
                    tempItem.setBackground(QColor(0, 200, 0, 127))
                self.card_list_widget.addItem(tempItem )



    def gui_browse_files(self):
        file_names = QFileDialog.getOpenFileName(self, 'Open file', 'C:\\Users', 'Images (*.png *.jpg *.jpeg)')
        self.filename_line.setText(str(file_names[0]))
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
        # Receiving Results Slot
        self.worker.result.connect(self.add_bingo_card)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()
        self.analyze_button.setEnabled(False)
        self.thread.finished.connect(lambda: self.analyze_button.setEnabled(True))


    def check_this_card(self,myCard):
        if isinstance(myCard,GameCard):
            if myCard.isWinner(self.itemCallsList):
                self.this_card_won(myCard)
        else:
            #error not a game card
            pass


    def check_all_cards(self):
        for x in self.myCards:
            self.check_this_card(x)



    def this_card_won(self, winningCard):
        winnerList = self.card_list_widget.findItems(winningCard.getImgPath(),Qt.MatchEndsWith)
        for x in winnerList:
            x.setBackground(QColor(0, 200, 0, 127))




    def add_bingo_card(self,bingoCard):
        if  isinstance(bingoCard,GameCard):
            self.myCards.append(bingoCard)
        else:
            pass


    def test_btn(self):
        #print(self.isDebug_btn.isChecked())
        print("Debug Mode: ",config.DEBUG_MODE)


class Worker(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    # progress signal
    result = pyqtSignal(GameCard)
    def __init__(self, filename_line ="", isDebug = False ):
        QObject.__init__(self)
        self.filename = filename_line
        self.isDebug = isDebug

    def run(self):
        "Task"
        try:
            myBingoCard = main.read_text(self.filename,self.isDebug)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.result.emit(myBingoCard)
        finally:
            self.finished.emit()




# Run this file to use application.
if __name__ == '__main__':
    app = QApplication([])
    WINDOW = MainWindow()
    widget = QStackedWidget()
    widget.addWidget(WINDOW)
    widget.setMinimumSize(500,500)
    widget.show()
    app.exec()

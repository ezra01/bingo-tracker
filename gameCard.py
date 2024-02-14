import config
import numpy as np

class GameCard:
    def __init__(self, imgPath="", numbers=[], winningNumbers =[]):
        self.imgPath = imgPath
        self.numbers = numbers
        self.winningNumbers = winningNumbers


    def getImgPath(self):
        return str(self.imgPath)


    def setImgPath(self, imgPath):
        self.imgPath=imgPath


    def getNumbers(self):
        return list(self.numbers)


    def setNumbers(self, numbers):
        self.numbers = numbers
        self.setWinningNumbers()


    def getWinningNumbers(self):
        if self.winningNumbers != []:
            return self.winningNumbers
        self.setWinningNumbers()
        return list(self.winningNumbers)



    def setWinningNumbers(self):
        lin = list(self.getNumbers())
        l = len(lin) + 1
        lin.insert(l // 2, -1)
        rowCounter = -1

        arrSize = int(np.sqrt(l + 1))
        shape = (arrSize * 2 + 2, arrSize)
        arr = np.zeros(shape)

        shape = (arrSize, arrSize)
        rows = np.zeros(shape)
        cols = np.zeros(shape)

        dia_tl = []
        dia_tr = []

        # Bingo List
        for i in range(0, l):
            if i != l // 2:
                if i % arrSize == 0:
                    rowCounter += 1
                rows[rowCounter][i % arrSize] = lin[i]
                cols[i % arrSize][rowCounter] = lin[i]
                if i % (arrSize + 1) == 0:
                    dia_tl.append(lin[i])
                if i % (arrSize - 1) == 0 and i != 0 and i < l - 1:
                    dia_tr.append(lin[i])
        if config.DEBUG_MODE:
            print("Here are the Separated rows \n{0}".format(rows))
            print("Here are the Separated cols \n{0}".format(cols))
            print("Here are the Separated diagonals \n{0}\n{1}".format(dia_tr, dia_tl))

        """
            Account for skipped middle value
            rows: every 5
            cols: every 5th
            diagonal tl: 0Val + every 5+1
            diagonal tr: every 5-1 excluding 0Val and lastval
        """
        bingoSets = []
        for bingoList in [rows, cols, [dia_tl, dia_tl]]:
            for line in bingoList:
                bingoSets.append(set(line))
        if config.DEBUG_MODE:
            print("Here are the sets of all bingo Lines \n{0}".format(bingoSets))
        self.winningNumbers = bingoSets



    def isWinner(self,calls):
        allWinners = self.getWinningNumbers()
        calls= set(calls)
        for x in allWinners:
            if x.issubset(calls):
                return True
        return False

if __name__ == '__main__':
    test_file =(
        #"jpg"
        "example_bingo.jpg"
    )
    lin = ['62', '47', '34', '29', '13', '67', '58', '45', '16', '3', '63', '57', '22', '15', '73', '53', '38', '20', '10', '68', '60', '35', '23', '2']
    myCard = GameCard("Card 1",lin)
    for x in myCard.getWinningNumbers():
        print(x)
    number_calls = ['62', '13', '67', '58', '22', '15', '20', '10', '2']
    print(myCard.isWinner(number_calls))
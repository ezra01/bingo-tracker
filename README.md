# Bingo Tracker 
***
#### Objective
Reads a picture of a bingo card and converts it to a digital representation. With input from user for game 
announcements the app will process winning 'Bingos'. 

 With many bingo cards this can reduce lag time and user errors in the game, while the major advantage comes with scalability. Digitizing bingo cards allows for a drastic increase in # of Bingo cards played by one person.

##### This project is currently in progress.

## Tech
***
- OpenCv with Google Tesseract for Optical Character Recognition
- PyQt5 for Graphical User Interface

## How to use
***

### Requirements:
- Python 3.6+ for Python-tesseract  
- c++ build tools v14
- Ensure pip is updated
- requirements.txt libraries

To download the most updated version of tesseract for windows go to I downloaded the additional language: equation and math in case it has better number recognition.
> [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) (Windows)

Make sure to record the download location for changing 
> pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
> 
### Project In use:
![alt text](https://github.com/ezra01/bingo-tracker/blob/master/Images/Analyze.JPG "Sample Bingo card")
![alt text](https://github.com/ezra01/bingo-tracker/blob/master/Images/Result.JPG "Digitized representation of sample bingo card")
![alt text](https://github.com/ezra01/bingo-tracker/blob/master/Images/Winner.JPG "Winning bingo card")

## ToDos
***
### Major TODOs:
- ~~Bingo card OCR~~ Stabalize image preprocessing for larger variety of images
- ~~Use isWinner method to determine winning bingo cards.~~
- ~~input for game IRL announcements~~
- checkCount of OCR Hits to determine if image preprocessing is correct (<24)
- checkCount of bounding boxes to determine if bingo tiles count is correct ((>24))
- ~~implement class for multiple bingo cards~~

### Minor TODOs:
- Determine if the additional language equation and math are critical
- ~~Create random bingo cards~~
- ~~Create random bingo calls~~
- Clear game
- Remove accidental bingo call
- Remove bingo card

### Future Features:
- image viewer for image preprocessing tweaks
- Overlay image ~~image representation of current cards in gui~~
- convolutional neural network for recognizing bingo cards and image preprocessing
- binary executable and installer



## Licenses:
***
PyQt5 is not licensed for commercial use.

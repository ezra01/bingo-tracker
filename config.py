import pytesseract
import random as rng
from PyQt5.QtCore import Qt
from datetime import datetime

import config

CustomObjectRole = Qt.UserRole + 1
rng.seed(datetime.now().timestamp())
RAND = rng
# Location of Tesseract download
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
DEBUG_MODE= False
def flipDebug():
    config.DEBUG_MODE= not bool(config.DEBUG_MODE)
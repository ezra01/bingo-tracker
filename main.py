# install numpy, pytesseract and opencv

from os import system as sys, name, path
from PyQt5.QtWidgets import QApplication,QStackedWidget
import numpy as np
import cv2 as cv
from scipy import stats as st
import numpy
from PIL import Image
import json
import pytesseract
from pytesseract import Output

import config
from gameCard import GameCard

def get_path(fin):
    exists = path.isfile(fin)

    full_path = path.realpath(fin)
    print(full_path)
    dirname, file = path.split(full_path)
    return dirname


windowNames = []
def add_to_list(window_name,image, scale = 60):
    image= cv.resize(image,(int(image.shape[0]*scale/100), int(image.shape[1]*scale/100)), interpolation= cv.INTER_AREA)
    cv.imshow(window_name, image)
    windowNames.append(window_name)

def move_windows():
    """
    np_img_concant = windowNames[0]
    for window_name,val in enumerate(windowNames):
        if val==0:
           pass
        else:
            np_img_concant = cv.hconcat( [window_name, np_img_concant])
    #cv.destroyAllWindows()
    cv.imshow("np_img_concant", np_img_concant)
    """
    cv.waitKey(0)



def gamma_correction(gamma, img_original):
    lookUpTable = np.empty((1, 256), np.uint8)
    for i in range(256):
        lookUpTable[0, i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
    return cv.LUT(img_original, lookUpTable)

def myround(x, base = 10):
    return base * round(x/base)

def read_text(fin, isDebug):
    DEBUG_MODE = isDebug
    window_name = fin
            # Get Image
    img1 = cv.imread(fin)
            # get dimensions of image
    imgHeight, imgWidth, colorSpace = img1.shape


            # Preprocess Image
    alpha = 1.2
    beta = 40
    img_corrected =cv.convertScaleAbs(img1, alpha=alpha, beta=beta)
    add_to_list("Color Corrected", img_corrected)
            # Gamma Correction
    img_corrected=gamma_correction(1.0, img_corrected)
    if DEBUG_MODE:
        add_to_list("Gamma Corrected", img_corrected)
            # To Grayscale
    img_grey = cv.cvtColor(img_corrected, cv.COLOR_BGR2GRAY)
            # Media filter
    img_grey = cv.medianBlur(img_grey, 3)
    if DEBUG_MODE:
        add_to_list("Median Filter", img_grey)
            # Blur, while retaining edges
    img_grey = cv.bilateralFilter(img_grey, 20, 20, 20)
    if DEBUG_MODE:
        add_to_list("BF2", img_grey)
            # otsu thresh
    ret, img_grey = cv.threshold(img_grey, 120, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    if DEBUG_MODE:
        add_to_list("ThreshedImage", img_grey)
    rect_kernel = cv.getStructuringElement(cv.MORPH_RECT, (1, 3))
    elipse_kernal = cv.getStructuringElement(cv.MORPH_ELLIPSE, (3,3))
            # must use odd kernal size or results in shift/translation

            # Morphology
            # erosion / dilation ( remove white noise/ removes black noise )
    img_grey = cv.dilate(img_grey, elipse_kernal, iterations=2)
    img_grey = cv.erode(img_grey, elipse_kernal, iterations=2)
    if DEBUG_MODE:
        add_to_list("Elipse morphology", img_grey)

    img_grey = cv.dilate(img_grey, rect_kernel, iterations=2)
    img_grey = cv.erode(img_grey, rect_kernel, iterations=1)
    if DEBUG_MODE:
        add_to_list("Rectangle morphology", img_grey)

    rect_kernel = cv.getStructuringElement(cv.MORPH_RECT, (1, 3))
    img_grey = cv.morphologyEx(img_grey, cv.MORPH_OPEN, rect_kernel)
    if DEBUG_MODE:
        add_to_list("Rectangle morphology2", img_grey)

            # Edge detection, outputs outline version of the image
    #img_contours = cv.Canny(img_grey, 30, 150)
    #add_to_list("edges", img_contours)

            #Creation of Bounding Boxes for masking and validation of preprocessing
                # using Contour Approximation, findContours returns contours and hierarchy
    cnts,hierarchy = cv.findContours(img_grey.copy(), cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
    img_copy = img1.copy()
    contours_poly =[]
    boundRect = []
    for i, c in enumerate(cnts):
        (x, y, w, h) = cv.boundingRect(c)
        if (imgWidth/8) > w > (imgWidth/25) and (imgHeight/8) > w > (imgHeight/25):
            contours_poly.append(cv.approxPolyDP(c, 3, True))
            boundRect.append(cv.boundingRect(contours_poly[-1]))

            # Clean up Bounding boxes
            # First, find Mode of Text Height
    modeRectHeight=st.mode(boundRect)[0][0][3]
    if DEBUG_MODE:
        print("modeRectHeight is {0}".format(modeRectHeight))
    boundRect2= []
    garbage=[]
    for a in range(0, len(boundRect)):
        # arbitrary value 10 used for range of heights between font lettering
        if abs(boundRect[a][3]-modeRectHeight) > 10:
            garbage.append(a)
    for a in range(len(garbage)-1, -1, -1):
        boundRect.pop(garbage[a])
            # sort by primary x values to closest modeRectHeight secondary y values
    boundRectSorted = sorted(boundRect, key=lambda x: (-myround(x[1], modeRectHeight), -x[0]))
    boundRect = boundRectSorted

            # Unionize Bounding boxes
    skip = True
    l = len(boundRect)
    if DEBUG_MODE:
        print("---BOUNDING BOX---\n")
    for i in range(0, l):
        if DEBUG_MODE:
            print("Ax={0} Cx+Cw={1} Dif={2}".format(int(boundRect[i - 1][0]), int(boundRect[i][0] + boundRect[i][2]), int(boundRect[i - 1][0]) - int(boundRect[i][0] + boundRect[i][2])))
        if skip==False:
            #arbitrary value 12 used for pixel distance (width) between bounding boxes
            # todo keep taller bounding box height and y value in union
            if abs(int(boundRect[i-1][0]) - int(boundRect[i][0]+boundRect[i][2])) < 16:
                #print("APPEND")
                boundRect2.append((boundRect[i][0],
                                   boundRect[i][1],
                                   int(boundRect[i-1][0]+boundRect[i-1][2]-boundRect[i][0]),
                                   int(boundRect[i-1][3])))
                # Bounding boxes are added to images determined by sorted array
                # currently sorted: starting in bottom-right corner right-to-left, bottom-to-top
                # imaged are drawn with the origin in the top left, adding pixels to move outward -> or V
                # from notation given by cv.boundingRect in TupleNotation: (x,y,w,h)
                # to 2ptNotation necessary for cv.rectangle (top-left pt, bottom-right pt) aka ((x,y), (x+w,y+h))
                # union of 2 separate bounding boxes can be done with
                # Box1:TL pt 'A', BR pt 'B' and Box2:TL pt 'C', BR pt 'D'. Again, added right-to-left
                # Box1. TupleNotation:(Ax,Ay,Aw,Ah). 2ptNotation: (Ax,Ay), (Bx,By) aka (Ax,Ay),(Ax+Aw,Ay+Ah)
                # Box2. TupleNotation:(Cx,Cy,Cw,Ch). 2ptNotation: (Cx,Cy), (Dx,Dy) aka (Cx,Cy),(Cx+Cw,Cy+Ch)
                #  Union.   TupleNotation: (Cx,Cy,Bx-Cx,By) aka (Cx, Cy, Ax+Aw-Cx+Cw,Ah)
                #           2ptNotation: (Cx,Cy), (Bx,By) aka (Cx,Cy),(Ax+Aw,Ay+Ah)
                skip = True
            else:
                boundRect2.append(boundRect[i-1])
                skip = False
        else:
            skip = False
        if i == l-1:
            boundRect2.append(boundRect[i])

            # Drawing Bounding Boxes
    if DEBUG_MODE:
        print("---BOUNDING BOX Locations---\n")
        for i in range(len(boundRect2)):
            color = (config.RAND.randint(0, 256), config.RAND.randint(0, 256), config.RAND.randint(0, 256))
            cv.rectangle(img_copy,  (int(boundRect2[i][0]), int(boundRect2[i][1])), (int(boundRect2[i][0]+boundRect2[i][2]), int(boundRect2[i][1]+boundRect2[i][3])), color, 2)
            if DEBUG_MODE:
                try:
                    print("{0}AND {1}".format((int(boundRect2[i][0]), int(boundRect2[i][1])), (int(boundRect2[i][0]+boundRect2[i][2]), int(boundRect2[i][1]+boundRect2[i][3]))))
                except Exception or TypeError as e:
                    print("Error: {0}".format(e))
        add_to_list("Unioned BoundBoxes", img_copy)

            # Mask everything outside of bounding boxes
    mask = np.zeros(img_copy.shape[:2], dtype="uint8")
    reverse_mask = 255* np.ones(img_copy.shape[:2], dtype="uint8")

    for i in range(len(boundRect2)):
        cv.rectangle(mask, (int(boundRect2[i][0]), int(boundRect2[i][1])), (int(boundRect2[i][0] + boundRect2[i][2]), int(boundRect2[i][1] + boundRect2[i][3])), 255,-1)
        cv.rectangle(reverse_mask, (int(boundRect2[i][0]), int(boundRect2[i][1])), (int(boundRect2[i][0] + boundRect2[i][2]), int(boundRect2[i][1] + boundRect2[i][3])), 0,-1)
    img_union_mask = cv.bitwise_and(img_grey, img_grey, mask=mask)
    img_union_reverse_mask = cv.bitwise_or(img_union_mask, reverse_mask)

    if DEBUG_MODE:
        print("count= {0}".format(len(boundRect2)))
        print("Count info= {0}".format(boundRect2))
        add_to_list("Mask", mask)
        add_to_list("reverse mask", reverse_mask)
        add_to_list("img_union_mask", img_union_mask)
        add_to_list("img_union_reverse_mask", img_union_reverse_mask)


                # Tesseract OCR
    padding=0
    final_results=[]
    for i in range(len(boundRect2)):
        temp_crop_image = img_union_reverse_mask[
                          int(boundRect2[i][1])-padding: int(boundRect2[i][1] + boundRect2[i][3])+padding,
                          int(boundRect2[i][0])-padding: int(boundRect2[i][0] + boundRect2[i][2])+padding
                          ]
        """
        if DEBUG_MODE:
            add_to_list("temp_crop_img {0}".format(i),temp_crop_image)
        """
        result = pytesseract.image_to_string(temp_crop_image, output_type=Output.DICT,
                                            config=""
                                                   "--psm 6"
                                                   " -c tessedit_char_whitelist=0123456789")
        final_results.append(result['text'].strip())

    if DEBUG_MODE:
        results = pytesseract.image_to_data(img_union_reverse_mask, output_type=Output.DICT,
                                            config=""
                                                   "--psm 11"
                                                   " -c tessedit_char_whitelist=0123456789")
        print(results['text'])

                # Read (Save Data as points)
        for i in range(0, len(results["text"])):
            x = results["left"][i]
            y = results["top"][i]
            w = results["width"][i]
            h = results["height"][i]
            text = results["text"][i]
            conf = int(results["conf"][i])

                # label data points on img1
            if conf > 0:
                text = "".join([c if ord(c) < 128 else "" for c in text]).strip()
                cv.rectangle(img_grey, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv.putText(img_grey, text, (x, y - 10),
        cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 200), 2)
    move_windows()
    # todo debug window view (for all windows)
    """ 
           # Display final Image
    add_to_list("Final Result", img_grey)
    
            # Simple VIEW Move windows side by side in 2 rows
    for i in range(0, len(windowNames)):
        if i <=len(windowNames)//2:
            cv.moveWindow(windowNames[i], (5+imgWidth)*i, 0)
        else:
            cv.moveWindow(windowNames[i], (5+imgWidth)*(i-len(windowNames)//2-1), (40+imgHeight))
    cv.waitKey(0)
    cv.destroyAllWindows()
    """
    if DEBUG_MODE:
        print(final_results)
    myBingoCard = GameCard(fin,final_results[::-1])
    return myBingoCard



    #return myBingoCard


if __name__ == '__main__':
    test_file =(
        #"jpg"
        "example_bingo.jpg"
    )
    read_text(test_file,config.DEBUG_MODE)
    lin = ['62', '47', '34', '29', '13', '67', '58', '45', '16', '3', '63', '57', '22', '15', '73', '53', '38', '20', '10', '68', '60', '35', '23', '2']
    number_calls = ['62', '13', '67', '58', '22', '15', '20', '10', '2']


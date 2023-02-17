# Extract texts from a document
import asyncio
import pandas as pd
import numpy as np
import PIL
import pytesseract
import spacy
import cv2
import os
from pdf2image import convert_from_path
from glob import glob
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.debug("test")

pdfPath = r"../data/Binder3.pdf"

# this will put all the content of the data frame into a csv
def writecsv(df: pd.DataFrame, path: str):
    os.makedirs('csvs', exist_ok=True)
    df.to_csv(path)


def generateBoundedImage(image, index:int, df:pd.DataFrame):
    ## Draw lines on the text in the document
    level = 'word'
    for l, x, y, w, h, c, t in df[['level', 'left', 'top', 'width', 'height', 'conf', 'text']].values:
        if level == 'page':
            if l == 1:
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 0), 2)
            else:
                continue

        elif level == 'block':
            if l == 2:
                cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            else:
                continue
        elif level == 'para':
            if l == 3:
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
            else:
                continue
        elif level == 'line':
            if l == 4:
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2)
            else:
                continue
        elif level == 'word':
            if l == 5:
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(image, t, (x, y), cv2.FONT_HERSHEY_PLAIN,
                            1, (255, 0, 0), 2)
            else:
                continue
    
    boundedImagePath = "../data/bounded/boundingbox_"+ str(index)+".jpeg"
    cv2.imwrite(boundedImagePath, image)

# Generate metadata of a PDF file
def getFileData(filename: str):
    pages = convert_from_path(filename, 350)
    i = 1
    for page in pages:
        image_name = "../data/temp/Page_" + str(i) + ".jpg"
        page.save(image_name, "JPEG")
        i = i+1

    imagePathList = glob("../data/temp/*.jpg")

    #logging.info("total number of pages "+ str(len(imagePathList)))
    imagePathList.sort()

    finalDF = pd.DataFrame()

    col_int = ['level', 'page_num', 'block_num', 'par_num',
                'line_num', 'word_num', 'left', 'top', 'width', 'height']

    for index, path in enumerate   (imagePathList):
        if index == 1:
            break

        img = cv2.imread(path)
        data = pytesseract.image_to_data(img, lang='mar+eng')
        dataList = list(map(lambda x: x.split('\t'), data.split('\n')))
        df = pd.DataFrame(dataList[1:], columns=dataList[0])
        df.to_csv(index=False)

        ## Data cleaning
        df.dropna(inplace=True)  # drop the missing in rows
        df[col_int] = df[col_int].astype(int)
        df['conf'] = df['conf'].astype(float).astype(int)

        ## Draw lines on the text in the document
        #image = img.copy()
        #generateBoundedImage(image, index, df)
    
        finalDF = pd.concat([finalDF, df], ignore_index = True)

    # write df to csv
    writecsv(finalDF, "csvs/extracted.csv")
    
    dfWords=finalDF[finalDF['level'] == 5]

    writecsv(dfWords, "csvs/extractedText.csv")

    ## Filter dataframe to just words
    finalDF80 = dfWords[dfWords['conf'] > 80]
    finalDF80 = finalDF80[["text"]]

    finalDF80.dropna(inplace=True)

    return finalDF80


async def main():
    df80 = getFileData(pdfPath)
    writecsv(df80, "csvs/output_80.csv")



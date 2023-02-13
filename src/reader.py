import pandas as pd
import numpy as np
import PIL
import pytesseract
import spacy
import cv2
import os
from pdf2image import convert_from_path

filenumber = "4"

pdfs = r"../data/4.pdf"
pages = convert_from_path(pdfs, 350)

i = 1
for page in pages:
    image_name = "../data/temp/Page"+filenumber+"_" + str(i) + ".jpg"
    page.save(image_name, "JPEG")
    i = i+1


# PIL.Image.open('./data/temp/Page_1.jpg')
img = cv2.imread('../data/temp/Page4_1.jpg')

data = pytesseract.image_to_data(img, lang='mar+eng')
print(data)
dataList = list(map(lambda x: x.split('\t'), data.split('\n')))
print(dataList, '\n\n')
df = pd.DataFrame(dataList[1:], columns=dataList[0])
print(df)
df.to_csv(index=False)


os.makedirs('csvs', exist_ok=True)
df.to_csv('csvs/out1.csv')


df.dropna(inplace=True)  # drop the missing in rows
col_int = ['level', 'page_num', 'block_num', 'par_num',
           'line_num', 'word_num', 'left', 'top', 'width', 'height']
df[col_int] = df[col_int].astype(int)
df['conf'] = df['conf'].astype(float).astype(int)
df.dtypes

image = img.copy()
level = 'word'
for l, x, y, w, h, c, t in df[['level', 'left', 'top', 'width', 'height', 'conf', 'text']].values:
    # print(l,x,y,w,h,c)
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

cv2.imwrite('boundingbox.jpeg', image)
df = df[df['conf'] > 80]

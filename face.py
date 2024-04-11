import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import sys
import mysql.connector
import argparse
parser = argparse.ArgumentParser(description='Easy Facial Recognition ')
parser.add_argument('-i', '--input', type=str, required=True, help='show the face of his account')
args = parser.parse_args()
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="tnmazes"
)
mycursor = mydb.cursor()

mycursor.execute("SELECT email FROM user ORDER BY id ASC")

email = mycursor.fetchall()

mycursor.execute("SELECT image_name FROM user ORDER BY id ASC")

imagename = mycursor.fetchall()
# from PIL import ImageGrab
 
path = 'Images'
images = []
classNames = []
realname= []
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
    print(classNames)
for i in range(len(classNames)):
    for j in range(len(imagename)):
        if classNames[i] == imagename[j][0]:
            realname[i] = email[j][0]

print(realname)
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList
 
def markAttendance(name):
    with open('Attendance.csv','w+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{dtString}')
 
#### FOR CAPTURING SCREEN RATHER THAN WEBCAM
# def captureScreen(bbox=(300,300,690+300,530+300)):
#     capScr = np.array(ImageGrab.grab(bbox))
#     capScr = cv2.cvtColor(capScr, cv2.COLOR_RGB2BGR)
#     return capScr
 
encodeListKnown = findEncodings(images)
print('Encoding Complete')
 
cap = cv2.VideoCapture(0)
i=0
while True:
    success, img = cap.read()
    #img = captureScreen()
    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
 
    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)
   
    for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
        #print(faceDis)
        matchIndex = np.argmin(faceDis)
       
        if matches[matchIndex]:
           



            name =email[matchIndex][0]
            
            print(name)
            
            #print(name)
            y1,x2,y2,x1 = faceLoc
            y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
            cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
            markAttendance(name)
            if name==args.input :
             i+=1
            
            if i==4:
                
              
                 cv2.destroyAllWindows()
                 sys.exit() 
    cv2.imshow('Webcam',img)
    cv2.waitKey(1)
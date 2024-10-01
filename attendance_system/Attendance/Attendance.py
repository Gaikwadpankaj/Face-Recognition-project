import cv2
import numpy as np
import face_recognition
import os
import csv
from datetime import datetime

path = 'Images'
images = []
classNames = []
myList = os.listdir(path)

for cl in myList:
    currentImg = cv2.imread(f'{path}/{cl}')
    images.append(currentImg)
    classNames.append(os.path.splitext(cl)[0])

def Encoding(images):
    encodeList = []
    for img in images:
        try:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        except Exception as e:
            print(f"Error encoding image: {e}")
    return encodeList

def markAtt(name, date):
    directory = 'Attendance'
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file_path = f"{directory}/Attendance_{date}.csv"
    COL_NAMES = ["Name", "Time"]
    attendance = [name, datetime.now().strftime('%H:%M:%S')]

    if name == "UNKNOWN":
        print("Face not recognized. Skipping attendance marking.")
    else:
        try:
            with open(file_path, "a") as csvfile:
                writer = csv.writer(csvfile)
                if os.path.getsize(file_path) == 0:
                    writer.writerow(COL_NAMES)
                writer.writerow(attendance)
        except Exception as e:
            print(f"Error writing to file: {e}")

encodeListKnown = Encoding(images)


cap = cv2.VideoCapture(0)

first_attendance_taken = False
last_attendance_time = datetime.now()

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    
    current_date = datetime.now().strftime('%Y-%m-%d')
    if current_date != last_attendance_time.strftime('%Y-%m-%d'):
        first_attendance_taken = False  
        last_attendance_time = datetime.now()

    facesCurrentFrame = face_recognition.face_locations(imgS)
    encodesCurrentFrame = face_recognition.face_encodings(imgS, facesCurrentFrame)

    for encodeFace, faceLoc in zip(encodesCurrentFrame, facesCurrentFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 1)
            cv2.rectangle(img, (x1, y1), (x2, y2), (50, 50, 255), 2)
            cv2.rectangle(img, (x1, y1 - 40), (x2, y1), (0, 0, 255), -1)
            cv2.putText(img, name, (x1 + 6, y1 - 16), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

            current_time = datetime.now()
            elapsed_time = (current_time - last_attendance_time).total_seconds()
            if not first_attendance_taken or elapsed_time >= 60:
                markAtt(name, current_time.strftime('%Y-%m-%d'))
                last_attendance_time = current_time
                if not first_attendance_taken:
                    first_attendance_taken = True
        else:
            cv2.putText(img, "Face not recognized", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

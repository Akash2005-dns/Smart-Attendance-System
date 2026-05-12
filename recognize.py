import cv2
import numpy as np
import pickle
from mtcnn import MTCNN
from keras_facenet import FaceNet
from sklearn.metrics.pairwise import cosine_similarity
import csv
from datetime import datetime 
import os
import time
from google_sheets import mark_attendance_google, update_class_sheet

def mark_attendance(name):
    os.makedirs("logs", exist_ok=True)
    file_path = "logs/attendance.csv"

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time_now = now.strftime("%H:%M:%S")

    file_exists = os.path.isfile(file_path)

    if name in marked_names:
        return

    already_marked = False
    if file_exists:
        with open(file_path, "r") as fr:
            reader = csv.reader(fr)
            for row in reader:
                if len(row) > 0 and row[0] == name and row[1] == date:
                    already_marked = True
                    break

    if not already_marked:
        with open(file_path, "a", newline="") as f:
            writer = csv.writer(f)

            if not file_exists:
                writer.writerow(["Name", "Date", "Time"])

            writer.writerow([name, date, time_now])

        # 🔥 Google Sheets update
        mark_attendance_google(name)

        print(f"✅ Attendance marked for {name}")

        marked_names.add(name)

# Load models
detector = MTCNN()
embedder = FaceNet()

# Load encodings
with open("encodings/faces.pkl", "rb") as f:
    data = pickle.load(f)

known_embeddings = data["embeddings"]
known_names = data["names"]

cap = cv2.VideoCapture(0)

print("📷 Starting recognition... Press 'q' to quit")

marked_names = set()
frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_count += 1
    if frame_count % 4 != 0:
        continue
    frame = cv2.resize(frame, (480,360))#reduce size for speed
    if not ret:
        break

    faces = detector.detect_faces(frame)

    for face in faces:
        x, y, w, h = face['box']
        x, y = abs(x), abs(y)

        face_img = frame[y:y+h, x:x+w]

        if face_img.size == 0:
            continue

        face_img = cv2.resize(face_img, (160, 160))
        face_img = np.expand_dims(face_img, axis=0)

        embedding = embedder.embeddings(face_img)[0]

        similarities = cosine_similarity([embedding], known_embeddings)[0]

        max_index = np.argmax(similarities)
        max_score = similarities[max_index]

        if max_score > 0.6:
            name = known_names[max_index]
            print(f"Recognized: {name}")
            #save to csv
            mark_attendance(name)
            #save to google sheets
            mark_attendance_google(name) #remove this line if you want to avoid duplicate entries in google sheets
            # update class sheet present/absent
            update_class_sheet(name)
        else:
            name = "Unknown"

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
        cv2.putText(frame, name, (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

    cv2.imshow("Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
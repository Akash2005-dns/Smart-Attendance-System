import cv2
import os
from mtcnn import MTCNN

detector = MTCNN()

name = input("Enter student name: ")
path = f"dataset/{name}"
os.makedirs(path, exist_ok=True)

cap = cv2.VideoCapture(0)

count = 0

print("📸 Capturing images... Look at camera")

while count < 20:
    ret, frame = cap.read()
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

        file_name = f"{path}/{count}.jpg"
        cv2.imwrite(file_name, face_img)

        count += 1

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)

    cv2.imshow("Capture Faces", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print(f"✅ {count} images saved for {name}")
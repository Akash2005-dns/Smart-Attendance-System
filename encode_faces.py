import os
import numpy as np
import pickle
from keras_facenet import FaceNet
import cv2

embedder = FaceNet()

dataset_path = "dataset"

embeddings = []
names = []

for person_name in os.listdir(dataset_path):
    person_folder = os.path.join(dataset_path, person_name)

    for image_name in os.listdir(person_folder):
        image_path = os.path.join(person_folder, image_name)

        img = cv2.imread(image_path)

        if img is None:
            continue

        img = cv2.resize(img, (160, 160))
        img = np.expand_dims(img, axis=0)

        embedding = embedder.embeddings(img)[0]

        embeddings.append(embedding)
        names.append(person_name)

print(f"✅ Total encodings: {len(embeddings)}")

data = {"embeddings": embeddings, "names": names}

os.makedirs("encodings", exist_ok=True)

with open("encodings/faces.pkl", "wb") as f:
    pickle.dump(data, f)

print("✅ Encoding completed!")
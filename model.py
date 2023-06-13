import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from PIL import Image
from sklearn.model_selection import train_test_split
import pickle

good_images_folder = 'good_images'
good_images_files = os.listdir(good_images_folder)
bad_images_folder = 'bad_images'
bad_images_files = os.listdir(bad_images_folder)

X = []
y = []

for image_file in good_images_files:
    image_path = os.path.join(good_images_folder, image_file)
    img = Image.open(image_path)  # Загрузка картинки
    img = img.resize((400, 400))
    features = np.asarray(img).reshape(-1)  # Преобразование картинки в вектор признаков
    X.append(features)
    y.append(1)

for image_file in bad_images_files:
    image_path = os.path.join(bad_images_folder, image_file)
    img = Image.open(image_path).resize((400, 400))  # Загрузка картинки
    features = np.asarray(img).reshape(-1)  # Преобразование картинки в вектор признаков
    X.append(features)
    y.append(0)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier()
model.fit(X_train, y_train)

# Сохранение модели в файл
with open('model.pickle', 'wb') as f:
    pickle.dump(model, f)

# -*- coding: utf-8 -*-
"""Crop_and_Weed_Detection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XrgAvxBzSmNi4i0LqsIZSzALTkpO_S-b
"""

! mkdir ~/.kaggle

!cp kaggle.json ~/.kaggle/

! chmod 600 ~/.kaggle/kaggle.json

#downloading dataset
!kaggle datasets download -d ravirajsinh45/crop-and-weed-detection-data-with-bounding-boxes

#extracting
import zipfile
zip_ref = zipfile.ZipFile('/content/crop-and-weed-detection-data-with-bounding-boxes.zip', 'r')
zip_ref.extractall("/content/")
zip_ref.close()

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

info = pd.DataFrame(columns = ["Name","Class","X", "Y", "Width", "Height"])

info

name = []
clas = []
x = []
y = []
w = []
h = []
path = "/content/agri_data/data/"
for file in os.listdir(path):
  if file.split(".")[-1] == "txt":
    with open(path + file, "r") as f :
      for line in f.readlines():
        data = line.split(" ")
        name.append(file.split(".")[0])
        clas.append(data[0])
        x.append(data[1])
        y.append(data[2])
        w.append(data[3])
        h.append(data[4])

len(name), len(clas), len(x), len(y),len(w), len(h)

info["Name"] = pd.Series(name)
info["Class"] = pd.Series(clas)
info["X"] = pd.to_numeric(pd.Series(x))
info["Y"] = pd.to_numeric(pd.Series(y))
info["Width"] = pd.to_numeric(pd.Series(w))
info["Height"] = pd.to_numeric(pd.Series(h))

info.info()

!mkdir Cropped_data
!mkdir Cropped_data/Crop
!mkdir Cropped_data/Weed

from PIL import Image

def crop_pic(image_name, x, y, w, h):
  source_path = "/content/agri_data/data/"
  image = plt.imread(f"{source_path}{image_name}.jpeg")
  #taking the shape
  W,H = image.shape[1],image.shape[0]
  #normalizing
  X = x*W
  Y = y*H
  width = w*W
  height = h*H

  x1 = int( X - (int(width) // 2))
  y1 = int( Y - (int(height) // 2))
  x2 = int( X + (int(width) // 2))
  y2 = int( Y + (int(height) // 2))
  # print(x1,x2, y1, y2)

  # Crop the image using the calculated coordinates
  cropped_image = image[y1:y2,  x1:x2]
  # print(W,H,x,y)
  return cropped_image
  #-------------------------------------------------------------------------
#Cropping the image and adding to its corresponding folder.
for index in range(info.shape[0]):
  cropped_pic = crop_pic( info.iloc[index,0], info.iloc[index,2], info.iloc[index,3], info.iloc[index,4],info.iloc[index,5] )
  reduced_img = Image.fromarray(cropped_pic)
  reduced_img = reduced_img.resize((256,256))
  # print(info.iloc[index,1],info.iloc[index,0])
  if info.iloc[index,1] == '0':
    reduced_img.save(f"/content/Cropped_data/Crop/{index}.jpeg")
  else:
    reduced_img.save(f"/content/Cropped_data/Weed/{index}.jpeg")

len(os.listdir("/content/Cropped_data/Crop"))+len(os.listdir("/content/Cropped_data/Weed"))

info.shape

from tensorflow.keras.utils import image_dataset_from_directory
import tensorflow as tf

from tensorflow.keras.layers import Dense, Conv2D, BatchNormalization, MaxPooling2D, Flatten, Dropout
from tensorflow.keras.models import Sequential

dataset = image_dataset_from_directory("/content/Cropped_data/",image_size = (256,256))

dataset.class_names

# Normalization
def process(image,label):
    image = tf.cast (image/255.0 ,tf.float32)
    return image,label

dataset = dataset.map(process)

# del model

# create CNN model

model = Sequential()

model.add(Conv2D(32,kernel_size=(3,3),padding='valid',activation='relu',input_shape=(256,256,3)))
model.add(Conv2D(32,kernel_size=(3,3),padding='valid',activation='relu',input_shape=(256,256,3)))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2,2),strides=2,padding='valid'))

model.add(Conv2D(64,kernel_size=(3,3),padding='valid',activation='relu'))
model.add(Conv2D(64,kernel_size=(3,3),padding='valid',activation='relu'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2,2),strides=2,padding='valid'))

model.add(Conv2D(128,kernel_size=(3,3),padding='valid',activation='relu'))
model.add(Conv2D(128,kernel_size=(3,3),padding='valid',activation='relu'))
model.add(Conv2D(128,kernel_size=(3,3),padding='valid',activation='relu'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2,2),strides=2,padding='valid'))

model.add(Conv2D(128,kernel_size=(3,3),padding='valid',activation='relu'))
model.add(Conv2D(128,kernel_size=(3,3),padding='valid',activation='relu'))
model.add(Conv2D(128,kernel_size=(3,3),padding='valid',activation='relu'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2,2),strides=2,padding='valid'))

model.add(Conv2D(128,kernel_size=(3,3),padding='valid',activation='relu'))
model.add(Conv2D(128,kernel_size=(3,3),padding='valid',activation='relu'))
model.add(Conv2D(128,kernel_size=(3,3),padding='valid',activation='relu'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2,2),strides=2,padding='valid'))

model.add(Flatten())

model.add(Dense(128,activation='relu'))
model.add(Dropout(0.1))
model.add(Dense(64,activation='relu'))
model.add(Dropout(0.1))
model.add(Dense(1,activation='sigmoid'))

model.summary()

model.compile(optimizer='adam',loss='binary_crossentropy',metrics=['accuracy'])

history = model.fit(dataset, epochs=10, batch_size=32)

plt.plot(history.history['accuracy'],color='red',label='train')
plt.legend()
plt.show()



test_image = plt.imread("/content/Cropped_data/Weed/1011.jpeg")
plt.imshow(test_image)
plt.show()
test_image = process(test_image,0)[0]
test_image = np.array(test_image).reshape((1,256,256,3))
# test_image = test_image.reshape((1,256,256,3))
if model.predict([test_image])[0]:
  print("Weed")
else:
  print("Crop")

test_image = plt.imread("/content/Cropped_data/Crop/1033.jpeg")
plt.imshow(test_image)
plt.show()
test_image = process(test_image,0)[0]
test_image = np.array(test_image).reshape((1,256,256,3))
# model.predict([test_image])

if model.predict([test_image])[0]>0.50:
  print("Weed")
else:
  print("Crop")
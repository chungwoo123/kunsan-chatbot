# data_preprocessing.py
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

def preprocess_data(directories, target_size=(150, 150), batch_size=32):
    datagens = [ImageDataGenerator(rescale=1./255, validation_split=0.2) for _ in directories]
    
    train_generators = []
    validation_generators = []

    for dir, datagen in zip(directories, datagens):
        train_generator = datagen.flow_from_directory(
            dir,
            target_size=target_size,
            batch_size=batch_size,
            class_mode='categorical',
            subset='training'
        )

        validation_generator = datagen.flow_from_directory(
            dir,
            target_size=target_size,
            batch_size=batch_size,
            class_mode='categorical',
            subset='validation'
        )

        train_generators.append(train_generator)
        validation_generators.append(validation_generator)

    return train_generators, validation_generators
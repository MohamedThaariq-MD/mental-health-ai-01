import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Dropout, Flatten, BatchNormalization
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
import matplotlib.pyplot as plt

# =====================================================
# CONFIGURATION
# =====================================================
IMG_SIZE = 48
BATCH_SIZE = 64
EPOCHS = 50
NUM_CLASSES = 7 # angry, disgust, fear, happy, sad, surprise, neutral

# Map indices to labels
EMOTION_LABELS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

def build_model():
    """
    Builds a Convolutional Neural Network (CNN) for emotion classification.
    """
    model = Sequential([
        # Block 1
        Conv2D(64, (3, 3), padding='same', activation='relu', input_shape=(IMG_SIZE, IMG_SIZE, 1)),
        BatchNormalization(),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),

        # Block 2
        Conv2D(128, (5, 5), padding='same', activation='relu'),
        BatchNormalization(),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),

        # Block 3
        Conv2D(512, (3, 3), padding='same', activation='relu'),
        BatchNormalization(),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),

        # Block 4
        Conv2D(512, (3, 3), padding='same', activation='relu'),
        BatchNormalization(),
        MaxPooling2D(pool_size=(2, 2)),
        Dropout(0.25),

        Flatten(),

        # Fully Connected layers
        Dense(256, activation='relu'),
        BatchNormalization(),
        Dropout(0.5),

        Dense(512, activation='relu'),
        BatchNormalization(),
        Dropout(0.5),

        Dense(NUM_CLASSES, activation='softmax')
    ])

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def train_model(train_dir, val_dir):
    """
    Trains the model using directories of images.
    Expects structure: train/happy/*.jpg, train/sad/*.jpg, etc.
    """
    
    # Data Augmentation to increase accuracy and prevent overfitting
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=30,
        shear_range=0.3,
        zoom_range=0.3,
        width_shift_range=0.4,
        height_shift_range=0.4,
        horizontal_flip=True,
        fill_mode='nearest'
    )

    val_datagen = ImageDataGenerator(rescale=1./255)

    train_generator = train_datagen.flow_from_directory(
        train_dir,
        color_mode='grayscale',
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=True
    )

    val_generator = val_datagen.flow_from_directory(
        val_dir,
        color_mode='grayscale',
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )

    model = build_model()
    print(model.summary())

    # Callbacks
    checkpoint = ModelCheckpoint(
        'models/emotion_model.h5', 
        monitor='val_accuracy', 
        save_best_only=True, 
        mode='max', 
        verbose=1
    )
    
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss', 
        factor=0.2, 
        patience=3, 
        verbose=1, 
        min_delta=0.0001
    )

    # Train
    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // BATCH_SIZE,
        epochs=EPOCHS,
        validation_data=val_generator,
        validation_steps=val_generator.samples // BATCH_SIZE,
        callbacks=[checkpoint, reduce_lr]
    )

    return history

if __name__ == "__main__":
    # Note: To train, you need the FER-2013 dataset (or similar) extracted into folders
    # Example structure:
    # dataset/
    #   train/
    #     happy/
    #     sad/
    #     ...
    #   test/
    #     happy/
    #     sad/
    #     ...
    
    TRAIN_DIR = 'data/train'
    TEST_DIR = 'data/test'

    print("Checking for dataset directories...")
    if not os.path.exists(TRAIN_DIR) or not os.path.exists(TEST_DIR):
        print(f"\n[!] Dataset not found at {TRAIN_DIR} or {TEST_DIR}.")
        print("[!] Please download the FER-2013 dataset and place it in the 'data' folder.")
        print("[!] You can get it from Kaggle: https://www.kaggle.com/c/challenges-in-representation-learning-facial-expression-recognition-challenge/data")
        print("\nSkipping training for now. However, the `emotion_face.py` script will use a robust pre-trained model by default.")
    else:
        print("Starting training pipeline...")
        history = train_model(TRAIN_DIR, TEST_DIR)
        print("Training complete. Best model saved to 'models/emotion_model.h5'")

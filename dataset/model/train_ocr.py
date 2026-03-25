import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np

IMG_WIDTH = 128
IMG_HEIGHT = 32
NUM_CLASSES = 80  # charset size

def build_crnn():
    input_img = layers.Input(shape=(IMG_HEIGHT, IMG_WIDTH, 1))

    # CNN
    x = layers.Conv2D(64, (3,3), activation='relu', padding='same')(input_img)
    x = layers.MaxPooling2D((2,2))(x)

    x = layers.Conv2D(128, (3,3), activation='relu', padding='same')(x)
    x = layers.MaxPooling2D((2,2))(x)

    # Reshape for RNN
    x = layers.Reshape((IMG_WIDTH // 4, (IMG_HEIGHT // 4) * 128))(x)

    # RNN
    x = layers.Bidirectional(layers.LSTM(128, return_sequences=True))(x)
    x = layers.Bidirectional(layers.LSTM(128, return_sequences=True))(x)

    output = layers.Dense(NUM_CLASSES, activation='softmax')(x)

    model = models.Model(input_img, output)
    model.compile(optimizer='adam', loss='categorical_crossentropy')
    return model

model = build_crnn()
model.save("model/crnn_model.h5")
print("Model saved.")

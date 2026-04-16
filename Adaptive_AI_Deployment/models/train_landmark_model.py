import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pickle

# Geometric Features for Emotions
# Features: [ear, mar, brow_ratio]
# We map explicitly to our core emotions.
EMOTIONS = ["Angry", "Happy", "Sad", "Surprise", "Neutral", "Fear", "Stressed"]

def generate_synthetic_landmarks(n_samples=2500):
    data = []
    labels = []
    
    for _ in range(n_samples):
        # Happy
        data.append([np.random.normal(0.3, 0.02), np.random.normal(0.4, 0.05), np.random.normal(0.7, 0.05)])
        labels.append("Happy")
        
        # Sad
        data.append([np.random.normal(0.22, 0.02), np.random.normal(0.15, 0.05), np.random.normal(0.7, 0.05)])
        labels.append("Sad")
        
        # Angry
        data.append([np.random.normal(0.28, 0.02), np.random.normal(0.1, 0.02), np.random.normal(0.5, 0.05)])
        labels.append("Angry")
        
        # Surprise
        data.append([np.random.normal(0.4, 0.03), np.random.normal(0.6, 0.05), np.random.normal(0.8, 0.05)])
        labels.append("Surprise")
        
        # Neutral
        data.append([np.random.normal(0.3, 0.02), np.random.normal(0.2, 0.05), np.random.normal(0.7, 0.05)])
        labels.append("Neutral")
        
        # Fear
        data.append([np.random.normal(0.38, 0.02), np.random.normal(0.3, 0.05), np.random.normal(0.65, 0.05)])
        labels.append("Fear")
        
        # Stressed (Tense eyes, furrowed brows)
        data.append([np.random.normal(0.25, 0.02), np.random.normal(0.15, 0.05), np.random.normal(0.5, 0.05)])
        labels.append("Stressed")

    return np.array(data), np.array(labels)

print("Generating synthetic landmark dataset...")
X, y_text = generate_synthetic_landmarks(7000)

encoder = LabelEncoder()
y = encoder.fit_transform(y_text)
y_cat = tf.keras.utils.to_categorical(y, num_classes=len(EMOTIONS))

X_train, X_test, y_train, y_test = train_test_split(X, y_cat, test_size=0.15, random_state=42)

print("Building DL/CNN Landmark Network...")
model = models.Sequential([
    layers.Input(shape=(3,)),
    layers.Dense(128, activation='relu'),
    layers.BatchNormalization(),
    layers.Dropout(0.3),
    layers.Dense(64, activation='relu'),
    layers.BatchNormalization(),
    layers.Dropout(0.2),
    layers.Dense(32, activation='relu'),
    layers.Dense(len(EMOTIONS), activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

print("Training Deep Learning model over 30 epochs...")
early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
history = model.fit(
    X_train, y_train, 
    epochs=40, 
    batch_size=32, 
    validation_data=(X_test, y_test),
    callbacks=[early_stop],
    verbose=1
)

loss, acc = model.evaluate(X_test, y_test, verbose=0)
print(f"DL Landmark Model Accuracy: {acc * 100:.2f}%")

# Save the model
model_path = os.path.join(os.path.dirname(__file__), 'face_landmark_model.keras')
print(f"Saving Keras DL model to {model_path}...")
model.save(model_path)

# Save the encoder
encoder_path = os.path.join(os.path.dirname(__file__), 'face_landmark_encoder.pkl')
with open(encoder_path, 'wb') as f:
    pickle.dump(encoder, f)

# Delete the old sklearn pkl model if it exists
old_model_path = os.path.join(os.path.dirname(__file__), 'face_landmark_model.pkl')
if os.path.exists(old_model_path):
    os.remove(old_model_path)

print("DL Landmark training complete.")

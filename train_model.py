import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ---------- Settings ----------
IMG_SIZE = 224
BATCH_SIZE = 8
EPOCHS = 10
DATASET_DIR = "dataset"

# ---------- Data Augmentation ----------
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    horizontal_flip=True,
    zoom_range=0.2,
    validation_split=0.2
)

train_generator = train_datagen.flow_from_directory(
    DATASET_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

val_generator = train_datagen.flow_from_directory(
    DATASET_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

# ---------- Save class labels ----------
class_names = list(train_generator.class_indices.keys())
print("Classes found:", class_names)

with open("class_names.txt", "w") as f:
    for name in class_names:
        f.write(name + "\n")

# ---------- Transfer Learning: MobileNetV2 base ----------
base_model = MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)

base_model.trainable = False

# ---------- Custom classification head ----------
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation='relu')(x)
output = Dense(len(class_names), activation='softmax')(x)

model = Model(inputs=base_model.input, outputs=output)

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# ---------- Training ----------
print("Training start ho rahi hai...")
history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS
)

# ---------- Model save karo ----------
model.save("civic_classifier.h5")
print("Model saved as civic_classifier.h5")

# ---------- Final accuracy print karo ----------
final_acc = history.history['val_accuracy'][-1]
print(f"Final validation accuracy: {final_acc:.2%}")
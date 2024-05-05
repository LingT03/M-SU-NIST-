import os
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from keras.models import Sequential
from keras.layers import Dense, Flatten, Conv2D, MaxPooling2D, Dropout, BatchNormalization

class Dataset:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.classes = []
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None

    def load_data(self):
        files = os.listdir(self.data_dir)
        self.classes = [f for f in files if os.path.isdir(os.path.join(self.data_dir, f))]

        X = []
        y = []

        for i, c in enumerate(self.classes):
            files = os.listdir(os.path.join(self.data_dir, c))
            files = [f for f in files if f.endswith('.png')]
            for f in files:
                img = Image.open(os.path.join(self.data_dir, c, f))
                img = img.resize((28, 28))
                img = np.array(img)
                img = img / 255
                img = img.astype(np.float32)
                X.append(img)
                y.append(i)

        X = np.array(X)
        y = np.array(y)

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.y_train = to_categorical(self.y_train)
        self.y_test = to_categorical(self.y_test)

class Model:
    def __init__(self):
        self.model = self.build_model()

    def build_model(self):
        model = Sequential()
        model.add(Conv2D(32, kernel_size=3, activation='relu', input_shape=(28, 28, 4)))
        model.add(BatchNormalization())
        model.add(Conv2D(32, kernel_size=3, activation='relu'))
        model.add(BatchNormalization())
        model.add(Conv2D(32, kernel_size = 5, strides=2, padding='same', activation='relu'))
        model.add(BatchNormalization())
        model.add(Dropout(0.5))
        model.add(Conv2D(64, kernel_size = 3, activation='relu'))
        model.add(BatchNormalization())
        model.add(Conv2D(64, kernel_size = 3, activation='relu'))
        model.add(BatchNormalization())
        model.add(Conv2D(64, kernel_size = 5, strides=2, padding='same', activation='relu'))
        model.add(BatchNormalization())
        model.add(Dropout(0.4))

        model.add(Conv2D(128, kernel_size = 4, activation='relu'))
        model.add(BatchNormalization())
        model.add(Flatten())
        model.add(Dropout(0.4))
        model.add(Dense(10, activation='softmax'))

        return model


    def train(self, X_train, y_train, X_test, y_test, epochs, batch_size):
        adam_optimizer = Adam(learning_rate=0.001)
        self.model.compile(loss="categorical_crossentropy", optimizer=adam_optimizer, metrics=["accuracy"])
        self.model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=epochs, batch_size=batch_size)

    def evaluate(self, X_test, y_test):
        predictions = self.model.predict(X_test)
        # Add post-processing evaluation here
        pass

class DataAugmentation:
    def __init__(self):
        self.datagen = ImageDataGenerator(
            rotation_range=10,
            zoom_range=0.10,
            width_shift_range=0.1,
            height_shift_range=0.1
        )

    def augment_data(self, X_train, y_train, num_augmented_samples=5):
        augmented_X = []
        augmented_y = []

        for i in range(len(X_train)):
            X_train_example = X_train[i].reshape((1, 28, 28, 4))
            y_train_example = y_train[i].reshape((1, 10))
            for _ in range(num_augmented_samples):
                X_train_augmented, y_train_augmented = self.datagen.flow(X_train_example, y_train_example).__next__()
                X_train_augmented = X_train_augmented.squeeze(axis=0)
                y_train_augmented = y_train_augmented.squeeze(axis=0)
                augmented_X.append(X_train_augmented)
                augmented_y.append(y_train_augmented)

        augmented_X = np.array(augmented_X)
        augmented_y = np.array(augmented_y)

        return augmented_X, augmented_y

# Usage
data_dir = 'Data'
dataset = Dataset(data_dir)
dataset.load_data()

data_augmentor = DataAugmentation()
augmented_X, augmented_y = data_augmentor.augment_data(dataset.X_train, dataset.y_train)

model = Model()
model.train(augmented_X, augmented_y, dataset.X_test, dataset.y_test, epochs=8, batch_size=50)
model.evaluate(dataset.X_test, dataset.y_test)

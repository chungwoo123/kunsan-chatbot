from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, Flatten
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import numpy as np
import os

# 데이터 경로 설정
train_data_dir = 'D:/lee/머신러닝_2024/식물 병해 인식/학습 이미지'

# ImageDataGenerator 설정
train_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)  # 데이터의 20%를 검증 데이터로 사용
validation_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

# 데이터 생성기
train_generator = train_datagen.flow_from_directory(
    train_data_dir,
    target_size=(150, 150),
    batch_size=32,
    class_mode='sparse',
    subset='training'
)

validation_generator = validation_datagen.flow_from_directory(
    train_data_dir,
    target_size=(150, 150),
    batch_size=32,
    class_mode='sparse',
    subset='validation'
)

# 모델 정의
model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(150, 150, 3)),
    MaxPooling2D((2, 2)),
    Flatten(),
    Dense(64, activation='relu'),
    Dense(len(train_generator.class_indices), activation='softmax')
])

# 모델 컴파일
model.compile(optimizer=Adam(), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# 모델 훈련
history = model.fit(
    train_generator,
    epochs=30,
    validation_data=validation_generator
)

# 그래프로 출력
plt.plot(history.history['accuracy'], label='training_accuracy')
plt.plot(history.history['val_accuracy'], label='val_accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')
plt.show()

# 모델 저장
model.save('plant_disease_model.h5')

# 테스트 이미지 예측 함수 정의
def predict_disease(image_path, model, class_names):
    img = load_img(image_path, target_size=(150, 150))
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # 배치 차원 추가
    img_array /= 255.0  # 정규화

    predictions = model.predict(img_array)[0]  # 배치 차원 제거
    predicted_class_index = np.argmax(predictions)
    predicted_class_name = class_names[predicted_class_index]
    predicted_probabilities = {class_names[i]: predictions[i] for i in range(len(predictions))}

    return predicted_class_name, predicted_probabilities

# 클래스 인덱스와 클래스 이름 매핑
class_indices = train_generator.class_indices
class_names = {v: k for k, v in class_indices.items()}

# 테스트 이미지 경로 설정
test_data_dir = 'D:/lee/머신러닝_2024/식물 병해 인식/테스트 이미지'  # 경로에 맞게 변경 필요

# 테스트 이미지 폴더 탐색 및 예측 결과 출력
for root, dirs, files in os.walk(test_data_dir):
    for file in files:
        if file.lower().endswith(('png', 'jpg', 'jpeg')):
            image_path = os.path.join(root, file)
            predicted_class_name, predicted_probabilities = predict_disease(image_path, model, class_names)
            print(f"이미지: {file}")
            print(f"예측된 질병: {predicted_class_name}")
            print("예측 확률:")
            for class_name, probability in predicted_probabilities.items():
                print(f"  {class_name}: {probability:.4f}")
            print("\n")

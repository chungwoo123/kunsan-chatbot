# app.py
from data_preprocessing import preprocess_data
from model_training import create_model, train_model
from model_evaluation import plot_history

import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import os

# 여러 데이터셋 디렉터리 경로
directories = ['D:/lee/머신러닝_2024/식물 병해 인식/학습 이미지/흰가루병',
               'D:/lee/머신러닝_2024/식물 병해 인식/학습 이미지/적성병', 
               'D:/lee/머신러닝_2024/식물 병해 인식/학습 이미지/잿빛곰팡이병',
               'D:/lee/머신러닝_2024/식물 병해 인식/학습 이미지/역병',
               'D:/lee/머신러닝_2024/식물 병해 인식/학습 이미지/시들음병']
target_size = (150, 150)
batch_size = 32
epochs = 30

# 데이터 전처리
train_generators, validation_generators = preprocess_data(directories, target_size, batch_size)

# 각 제너레이터의 클래스 인덱스 확인 (모든 제너레이터의 클래스 인덱스가 동일해야 합니다)
class_indices = train_generators[0].class_indices

# 모델 생성
num_classes = len(class_indices)
model = create_model(num_classes=num_classes, input_shape=(150, 150, 3))

# 모델 컴파일
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# 제너레이터를 합쳐서 훈련 데이터와 검증 데이터 생성
train_data = np.concatenate([next(gen)[0] for gen in train_generators])
train_labels = np.concatenate([next(gen)[1] for gen in train_generators])

validation_data = np.concatenate([next(gen)[0] for gen in validation_generators])
validation_labels = np.concatenate([next(gen)[1] for gen in validation_generators])

# 모델 훈련
history = model.fit(
    train_data, train_labels,
    epochs=epochs,
    validation_data=(validation_data, validation_labels)
)

# 모델 평가
plot_history(history)

# 모델 저장
model.save('plant_disease_model.h5')

# 모델 불러오기
model = load_model('plant_disease_model.h5')

# 클래스 인덱스와 클래스 이름 매핑 (한글로)
class_names = list(class_indices.keys())
class_names.sort(key=lambda x: class_indices[x])
class_names_korean = ['흰가루병', '적성병', '잿빛곰팡이병', '역병', '시들음병']

def preprocess_input_image(img_path):
    img = image.load_img(img_path, target_size=(150, 150))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0
    return img_array

def predict_image(model, img_path):
    img_array = preprocess_input_image(img_path)
    predictions = model.predict(img_array)
    class_idx = np.argmax(predictions, axis=1)[0]
    class_name = class_names_korean[class_idx]
    return class_name

if __name__ == '__main__':
    while True:
        img_path = input("식물 이미지를 입력하세요 (종료하려면 'exit' 입력): ")
        if img_path.lower() == 'exit':
            break
        if not os.path.exists(img_path):
            print("잘못된 파일 경로입니다. 다시 시도해주세요.")
            continue
        class_name = predict_image(model, img_path)
        print(f"식물의 병해 유형은: {class_name}")
import json
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout, TimeDistributed

# 대화 데이터를 로드하는 함수
def load_conversation_data(directory):
    conversations = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data['info']:
                    text = item['annotations']['text']
                    lines = text.split('\n')
                    for i in range(0, len(lines) - 1, 2):
                        user_text = lines[i].split(': ')[1] if ': ' in lines[i] else ''
                        bot_text = lines[i + 1].split(': ')[1] if ': ' in lines[i + 1] else ''
                        if user_text and bot_text:
                            conversations.append((user_text, bot_text))
    return conversations

# 대화 데이터 폴더 경로
conversation_directory = r'C:\Users\skykm\바탕 화면\대화데이터'

# 대화 데이터 로드
conversation_pairs = load_conversation_data(conversation_directory)

# 대화 데이터를 DataFrame으로 변환
conversation_df = pd.DataFrame(conversation_pairs, columns=['user_text', 'bot_text'])


# 직업 데이터 로드 (이전 작업에서 동일)
job_data = pd.read_csv(r'C:\Users\skykm\바탕 화면\직업_분류표.csv')
job_data = job_data.dropna()

# 입력 (X)와 출력 (y) 데이터 정의 (대화 데이터)
X = conversation_df['user_text']
y = conversation_df['bot_text']

# 토크나이저 설정 및 텍스트 시퀀스 변환
tokenizer = Tokenizer(num_words=5000, oov_token='<OOV>')
tokenizer.fit_on_texts(X)

X_sequences = tokenizer.texts_to_sequences(X)
y_sequences = tokenizer.texts_to_sequences(y)

max_length = 100
X_padded = pad_sequences(X_sequences, maxlen=max_length, padding='post')
y_padded = pad_sequences(y_sequences, maxlen=max_length, padding='post')

# y 값을 3차원에서 2차원으로 변환
y_padded = np.expand_dims(y_padded, -1)

# 훈련 데이터와 테스트 데이터로 분할
X_train, X_test, y_train, y_test = train_test_split(X_padded, y_padded, test_size=0.2, random_state=42)

# 4. 딥러닝 모델 구성 및 학습
model = Sequential([
    Embedding(input_dim=5000, output_dim=64),
    LSTM(64, return_sequences=True),
    Dropout(0.2),
    LSTM(64, return_sequences=True),
    Dropout(0.2),
    TimeDistributed(Dense(32, activation='relu')),
    TimeDistributed(Dense(5000, activation='softmax'))
])

model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

model.fit(X_train, y_train, epochs=20, validation_data=(X_test, y_test))

loss, accuracy = model.evaluate(X_test, y_test)
print(f'테스트 정확도: {accuracy:.4f}')

# 5. 사용자 입력을 처리하고 예측하는 함수 작성
def preprocess_input(user_input, tokenizer, max_length):
    sequences = tokenizer.texts_to_sequences([user_input])
    padded_sequences = pad_sequences(sequences, maxlen=max_length, padding='post')
    return padded_sequences

def generate_response(user_input, model, tokenizer, max_length):
    processed_input = preprocess_input(user_input, tokenizer, max_length)
    prediction = model.predict(processed_input)
    predicted_sequence = prediction.argmax(axis=2)[0]
    response = tokenizer.sequences_to_texts([predicted_sequence])[0]
    return response

# 6. 챗봇과의 대화 함수 작성
def chat_with_bot(model, tokenizer, max_length):
    print("안녕하세요! 진로 상담 챗봇입니다. '종료'라고 입력하면 대화를 종료합니다.")
    while True:
        user_input = input("사용자: ")
        if user_input.lower() == '종료':
            print("챗봇: 대화를 종료합니다. 안녕히 가세요!")
            break
        response = generate_response(user_input, model, tokenizer, max_length)
        print(f"챗봇: {response}")

# 7. 챗봇 실행
chat_with_bot(model, tokenizer, max_length)

import json
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Embedding

# 대화 데이터를 로드하는 함수
def load_conversation_data(directory):
    conversations = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.getsize(file_path) > 0:  # 파일이 비어있지 않은 경우에만 읽기
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
            except json.JSONDecodeError:
                print(f"파일을 읽는 도중 오류가 발생했습니다: {file_path}")
                continue
    return conversations

# 대화 데이터 폴더 경로
conversation_directory = r'C:\Users\skykm\바탕 화면\대화데이터'

# 대화 데이터 로드
conversation_pairs = load_conversation_data(conversation_directory)

# 대화 데이터를 DataFrame으로 변환
conversation_df = pd.DataFrame(conversation_pairs, columns=['user_text', 'bot_text'])

# 데이터의 첫 몇 행 확인
print(conversation_df.head())

# 직업 데이터 로드
job_data = pd.read_csv(r'C:\Users\skykm\바탕 화면\직업_분류표.csv')
job_data = job_data.dropna()

# 직업 데이터의 첫 몇 행 확인
print(job_data.head())

# 입력 (X)와 출력 (y) 데이터 정의 (대화 데이터)
X = conversation_df['user_text']
y = conversation_df['bot_text']

# 토크나이저 설정 및 텍스트 시퀀스 변환
num_words = 30000  # num_words를 10000에서 30000으로 증가
tokenizer = Tokenizer(num_words=num_words, oov_token='<OOV>')
tokenizer.fit_on_texts(pd.concat([X, y]))

# 시작 및 종료 토큰 추가
start_token = '<start>'
end_token = '<end>'

# 토크나이저에 시작 및 종료 토큰 추가
tokenizer.word_index[start_token] = len(tokenizer.word_index) + 1
tokenizer.word_index[end_token] = len(tokenizer.word_index) + 1

X_sequences = tokenizer.texts_to_sequences(X)
y_sequences = tokenizer.texts_to_sequences(y)

# y 시퀀스에 시작 및 종료 토큰 추가
y_sequences = [[tokenizer.word_index[start_token]] + seq + [tokenizer.word_index[end_token]] for seq in y_sequences]

# 레이블 값이 유효한지 확인하고 변환
max_word_index = num_words - 1
y_sequences = [[token if token <= max_word_index else tokenizer.word_index['<OOV>'] for token in seq] for seq in y_sequences]

max_length = 50  # 패딩 길이를 100에서 50으로 감소
X_padded = pad_sequences(X_sequences, maxlen=max_length, padding='post')
y_padded = pad_sequences(y_sequences, maxlen=max_length, padding='post')

# 훈련 데이터와 테스트 데이터로 분할
X_train, X_test, y_train, y_test = train_test_split(X_padded, y_padded, test_size=0.2, random_state=42)

# seq2seq 모델 구성 및 학습
# 인코더
encoder_inputs = Input(shape=(max_length,))
enc_emb = Embedding(input_dim=num_words, output_dim=64)(encoder_inputs)
encoder_lstm = LSTM(64, return_sequences=True, return_state=True)
encoder_outputs, state_h, state_c = encoder_lstm(enc_emb)
encoder_states = [state_h, state_c]

# 디코더
decoder_inputs = Input(shape=(max_length,))
dec_emb_layer = Embedding(input_dim=num_words, output_dim=64)
dec_emb = dec_emb_layer(decoder_inputs)
decoder_lstm = LSTM(64, return_sequences=True, return_state=True)
decoder_outputs, _, _ = decoder_lstm(dec_emb, initial_state=encoder_states)
decoder_dense = Dense(num_words, activation='softmax')
decoder_outputs = decoder_dense(decoder_outputs)

# 모델 정의
model = Model([encoder_inputs, decoder_inputs], decoder_outputs)

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# y_padded에 차원을 추가
y_padded = np.expand_dims(y_padded, -1)

model.fit([X_train, X_train], y_train, epochs=20, validation_data=([X_test, X_test], y_test))

# 예측 모델 구성
encoder_model = Model(encoder_inputs, encoder_states)

decoder_state_input_h = Input(shape=(64,))
decoder_state_input_c = Input(shape=(64,))
decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]
dec_emb2 = dec_emb_layer(decoder_inputs)
decoder_outputs2, state_h2, state_c2 = decoder_lstm(dec_emb2, initial_state=decoder_states_inputs)
decoder_states2 = [state_h2, state_c2]
decoder_outputs2 = decoder_dense(decoder_outputs2)
decoder_model = Model(
    [decoder_inputs] + decoder_states_inputs,
    [decoder_outputs2] + decoder_states2)

# 디코더를 이용한 응답 생성 함수
def decode_sequence(input_seq):
    states_value = encoder_model.predict(input_seq)
    target_seq = np.zeros((1, 1))
    target_seq[0, 0] = tokenizer.word_index[start_token]

    stop_condition = False
    decoded_sentence = ''
    while not stop_condition:
        output_tokens, h, c = decoder_model.predict(
            [target_seq] + states_value)
        
        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_word = tokenizer.index_word.get(sampled_token_index, '<OOV>')
        
        if sampled_word != '<OOV>':
            decoded_sentence += ' ' + sampled_word

        if sampled_word == end_token or len(decoded_sentence) > max_length:
            stop_condition = True

        target_seq = np.zeros((1, 1))
        target_seq[0, 0] = sampled_token_index

        states_value = [h, c]

    return decoded_sentence.strip()

# 사용자 입력을 처리하고 예측하는 함수 작성
def preprocess_input(user_input, tokenizer, max_length):
    sequences = tokenizer.texts_to_sequences([user_input])
    padded_sequences = pad_sequences(sequences, maxlen=max_length, padding='post')
    return padded_sequences

# 직업 데이터에서 관련 직업 찾기
def find_related_jobs(user_input, job_data):
    related_jobs = job_data[job_data['하는 일'].str.contains(user_input, case=False, na=False)]
    return related_jobs['직업 이름'].tolist()

# 챗봇과의 대화 함수 작성
def chat_with_bot():
    print("안녕하세요! 진로 상담 챗봇입니다. '종료'라고 입력하면 대화를 종료합니다.")
    while True:
        user_input = input("사용자: ")
        if user_input.lower() == '종료':
            print("챗봇: 대화를 종료합니다. 안녕히 가세요!")
            break
        input_seq = preprocess_input(user_input, tokenizer, max_length)
        response = decode_sequence(input_seq)
        related_jobs = find_related_jobs(user_input, job_data)
        if related_jobs:
            response += f"\n관련 직업: {', '.join(related_jobs)}"
        print(f"챗봇: {response}")

# 챗봇 실행
chat_with_bot()

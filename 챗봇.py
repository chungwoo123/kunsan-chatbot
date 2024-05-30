import csv
import json
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

nltk.download('punkt')

def load_jobs(file_path):
    jobs = {}
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            jobs[row['직업 이름']] = row['하는 일']
    return jobs

def load_conversation(file_path):
    with open(file_path, 'r', encoding='utf-8') as jsonfile:
        conversation_data = json.load(jsonfile)
    return conversation_data

def tokenize_and_vectorize(conversation_data):
    corpus = []
    responses = {}
    for convo in conversation_data:
        for key, value in convo['talk']['content'].items():
            if key.startswith('HS') and value:
                corpus.append(value)
                response_key = 'S' + key[1:]
                responses[value] = convo['talk']['content'].get(response_key, "죄송합니다, 잘 이해하지 못했습니다. 다른 질문을 해 주세요.")
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus)
    return vectorizer, X, responses

def get_response(user_input, vectorizer, X, responses):
    user_vec = vectorizer.transform([user_input])
    similarities = cosine_similarity(user_vec, X).flatten()
    closest_idx = np.argmax(similarities)
    closest_match = list(responses.keys())[closest_idx]
    return responses[closest_match]

def chat(jobs, conversation_data):
    vectorizer, X, responses = tokenize_and_vectorize(conversation_data)
    print("안녕하세요. IT-chat입니다. '종료'를 입력하면 대화가 종료됩니다.")
    while True:
        user_input = input("사용자 : ")
        if user_input.lower() == '종료':
            print("챗봇 : 대화를 종료합니다.")
            break
        elif user_input in jobs:
            print("챗봇 : " + jobs[user_input])
        else:
            response = get_response(user_input, vectorizer, X, responses)
            print("챗봇 : " + response)

# 파일 경로 설정
jobs_file_path = r'C:\Users\skykm\바탕 화면\직업_분류표.csv'
conversation_file_path = r'C:\Users\skykm\바탕 화면\감성대화말뭉치(최종데이터)_Training.json'

# 파일 로드
jobs = load_jobs(jobs_file_path)
conversation_data = load_conversation(conversation_file_path)

# 채팅 함수 실행
chat(jobs, conversation_data)

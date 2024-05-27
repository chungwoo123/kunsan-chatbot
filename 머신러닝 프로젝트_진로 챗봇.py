import pandas as pd
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from konlpy.tag import Okt

# 형태소 분석을 위한 객체 생성
okt = Okt()

# CSV 파일에서 데이터 로드
def load_career_data(file_path):
    data = pd.read_csv(file_path)
    career_data = {row['직업 이름']: row['하는 일'] for _, row in data.iterrows()}
    return career_data

# 바탕화면 경로 설정
file_path = 'C:/Users/USER/Desktop/직업_분류표.csv'
career_data = load_career_data(file_path)

# ChatterBot 생성 및 훈련
chatbot = ChatBot('CareerBot')
trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train("chatterbot.corpus.korean")

def analyze_question(question):
    """질문을 형태소 분석 후 주요 명사 추출"""
    nouns = okt.nouns(question)
    return nouns

def find_career(nouns, career_data):
    """추출된 명사와 매칭되는 직업 찾기"""
    for noun in nouns:
        if noun in career_data:
            return noun
    return None

def get_career_advice(career):
    """직업에 대한 정보 반환"""
    return career_data.get(career, "해당 직업에 대한 정보가 없습니다.")

def chat():
    print("안녕하세요! 저는 진로 상담 챗봇입니다. 무엇을 도와드릴까요?")
    while True:
        user_input = input("질문을 입력해주세요: ")
        if user_input.lower() in ["종료", "끝", "그만"]:
            print("안녕히 가세요!")
            break
        
        nouns = analyze_question(user_input)
        career = find_career(nouns, career_data)
        
        if career:
            advice = get_career_advice(career)
            print(advice)
        else:
            response = chatbot.get_response(user_input)
            print(response)

# 챗봇 실행
chat()
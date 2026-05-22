import re 
from konlpy.tag import Okt 

class TextCleaner: 
    def __init__(self):  
        # 형태소 분석기(Okt) 초기화 
        self.okt = Okt()
        
        # STT에서 자주 나오는 불필요한 추임새(불용어) 리스트
        self.stop_words = ['음', '어', '그', '저', '아', '막']
        
    def clean(self, text):
        # 1차 정제: 특수문자 제거 (기존 로직)
        text = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', text)
        
        # 2차 정제: Okt 정규화 기능 (예: "안녕하세욬ㅋㅋ" -> "안녕하세요ㅋㅋ" 로 교정)
        text = self.okt.normalize(text)
        
        # 3차 정제: 형태소 분석을 통해 불필요한 추임새(음, 어 등) 제거
        pos_data = self.okt.pos(text)
        cleaned_words = []
        for word, pos in pos_data:
            # 불용어 리스트에 없는 단어만 통과
            if word not in self.stop_words:
                cleaned_words.append(word)
                
        # 리스트로 쪼개진 단어들을 다시 하나의 문장으로 띄어쓰기로 합치기
        final_text = ' '.join(cleaned_words)
        
        return final_text.strip()

# --- 자가 테스트용 코드 ---
if __name__ == "__main__":  
    cleaner = TextCleaner()
    print("TextCleaner 초기화 완료")
    
    # 테스트 해보기
    test_text = "음... 아 안녕하세욬 제 이름은 이중원입니다."
    print("원본:", test_text)
    print("정제:", cleaner.clean(test_text))
import logging 
import requests 
import time
from flask import Flask, request, jsonify, render_template 
from flask_cors import CORS 
from cleaner import TextCleaner  # 🛠️ 정제 모듈을 PC 서버단에서 가져옴

app = Flask(__name__)  
CORS(app)

log = logging.getLogger('werkzeug') 
log.setLevel(logging.ERROR) 

# PC 서버단에서 텍스트 정제기 초기화 (무거운 JVM 연산을 성능 좋은 PC가 부담)
cleaner = TextCleaner()
print("✅ GPU/메인 PC 서버단에서 KoNLPy 정제 엔진 초기화 완료!")

latest_data = {
    "raw": "대기 중...", 
    "refined": "대기 중...", 
    "ai_response": "AI가 번역 중입니다...",
    "timestamp": "-" 
}

# LM Studio 호출 함수 (수신된 언어 상태에 따라 프롬프트 가변 분기)
def ask_lm_studio(text, source_lang): 
    url = "http://25.18.230.25:5000/v1/chat/completions"
    headers = {"Content-Type": "application/json"} 
    
    if source_lang == "ja":
        system_prompt = """당신은 일본어를 한국어로 번역하는 전문 번역기입니다.
다음 규칙을 엄격히 지켜서 대답하세요.
1. 문맥을 파악해 가장 자연스럽고 매끄러운 한국어로 번역하세요.
2. 부연 설명이나 인사말("번역 결과입니다" 등)은 절대 하지 마세요.
3. 오직 번역된 한국어 문장만 출력하세요."""
        user_content = f"다음 일본어 문장을 한국어로 번역해: {text}"
    else:
        system_prompt = """당신은 한국어를 일본어로 번역하는 전문 번역기입니다.
다음 규칙을 엄격히 지켜서 대답하세요.
1. 문맥을 파악해 가장 자연스러운 일본어로 번역하세요.
2. 부연 설명이나 아는 척하는 대답은 절대 하지 마세요.
3. 오직 번역된 일본어 문장만 출력하세요."""
        user_content = f"다음 문장을 일본어로 번역해: {text}"

    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.2
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        return "AI 응답 오류"
    except Exception as e:
        return f"연결 실패: {e}"

@app.route('/') 
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST']) 
def process(): 
    global latest_data 
    data = request.json 
    
    # 라즈베리파이가 보낸 가공되지 않은 날것의 데이터 접수
    raw_text = data.get("raw", "")
    source_lang = data.get("lang", "ko")
    print(f"📥 [API 호출 접수] 라즈베리파이로부터 문자 도착: '{raw_text}'")
    
    # 🛠️ 변경됨: 받아온 날것의 문자를 성능 좋은 PC에서 직접 형태소 정제 가동!
    refined_text = cleaner.clean(raw_text, lang=source_lang)
    print(f"✨ [서버 자체 정제 완료] 결과: '{refined_text}'")
    
    # 정제된 안전한 데이터로 로컬 AI에게 번역 요청
    ai_res = ask_lm_studio(refined_text, source_lang)
    print(f"🤖 [AI 번역 완료] 결과: '{ai_res}'")
    
    # 웹 UI 전송용 데이터 업데이트
    latest_data["raw"] = raw_text
    latest_data["refined"] = refined_text
    latest_data["ai_response"] = ai_res
    latest_data["timestamp"] = time.strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify({"status": "success", "ai_response": ai_res})

@app.route('/get_latest', methods=['GET']) 
def get_latest(): 
    return jsonify(latest_data) 

if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5001)
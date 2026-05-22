import logging 
import requests 
import time
from flask import Flask, request, jsonify, render_template 
from flask_cors import CORS 

# 1. 앱 초기화 (오타 수정: __name__)
app = Flask(__name__)  
CORS(app)

# 접속 로그 숨기기
log = logging.getLogger('werkzeug') 
log.setLevel(logging.ERROR) 

latest_data = {
    "raw": "대기 중...", 
    "refined": "대기 중...", 
    "ai_response": "AI가 번역 중입니다...",
    "timestamp": "-" 
}

# 2. LM Studio 호출 함수 (수정 완료)
def ask_lm_studio(text): 
    # 실제 LM Studio 주소로 수정
    url = "http://25.18.230.25:5000/v1/chat/completions"
    headers = {"Content-Type": "application/json"} 
    
    system_prompt = """당신은 한국어를 일본어로 번역하는 전문 번역기입니다.
다음 규칙을 엄격히 지켜서 대답하세요.
1. 사용자의 입력은 음성 인식을 통해 작성된 것이므로, 오타나 문법에 맞지 않는 구어체가 있더라도 문맥을 파악해 가장 자연스러운 일본어로 번역하세요.
2. "번역 결과입니다", "알겠습니다" 같은 불필요한 대답이나 부연 설명은 절대 하지 마세요.
3. 오직 번역된 일본어 문장만 출력하세요."""

    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"다음 문장을 일본어로 번역해: {text}"}
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

# 3. 라우터 설정
@app.route('/') 
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST']) 
def process(): 
    global latest_data 
    data = request.json 
    
    raw_text = data.get("raw", "")
    refined_text = data.get("refined", "") 
    
    ai_res = ask_lm_studio(refined_text)
    
    latest_data["raw"] = raw_text
    latest_data["refined"] = refined_text
    latest_data["ai_response"] = ai_res
    latest_data["timestamp"] = time.strftime('%Y-%m-%d %H:%M:%S')
    
    return jsonify({"status": "success", "ai_response": ai_res})

@app.route('/get_latest', methods=['GET']) 
def get_latest(): 
    return jsonify(latest_data) 

# 4. 실행 (오타 수정: __name__, __main__, 포트 5001)
if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=5001)
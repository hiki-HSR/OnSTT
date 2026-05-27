import time 
import requests 
import speech_recognition as sr  
from faster_whisper import WhisperModel 

# 🛠️ 백엔드 실제 고정 API 주소
API_URL = "http://210.110.250.32:8000"
HEALTH_CHECK_URL = f"{API_URL}/health"
SESSION_API_URL = f"{API_URL}/sessions"
UTTERANCE_API_URL = f"{API_URL}/utterances"

def check_server_health():
    print(f"📡 서버 연결 상태 확인 중... ({HEALTH_CHECK_URL})")
    try:
        response = requests.get(HEALTH_CHECK_URL, timeout=3)
        if response.status_code == 200:
            print("✅ 서버 연결 성공!")
            return True
        return False
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return False

def get_model_settings():
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda", "float16"
    except ImportError:
        pass
    return "cpu", "int8"

def run_pi_node(): 
    if not check_server_health():
        print("🚨 서버가 통신 불가능 상태이므로 종료합니다.")
        return

    DEVICE, COMPUTE_TYPE = get_model_settings()
    MODEL_SIZE = "tiny" 

    print("모델 로딩 중...")
    stt_model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE) 
    print("✅ 라즈베리파이 STT 엔진 준비 완료!")

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    print("✅ 마이크 준비 완료!")

    # 🛠️ [DB 모델 매칭 Step 1] 유저 ID 설정
    # SQLAlchemy 모델에 맞춰 user_id는 정수형(Integer)이어야 합니다.
    # 기본적으로 테스트용 1번 유저를 타겟팅합니다.
    target_user_id = 1 
    
    # 🛠️ [DB 모델 매칭 Step 2] 세션 생성 (필수 값인 topic 포함)
    print(f"⏳ 백엔드 서버에 회화 세션 생성 요청 중... ({SESSION_API_URL})")
    session_payload = {
        "user_id": target_user_id,
        "topic": "라즈베리파이 실시간 번역 세션",  # ⭕ 필수값(nullable=False) 반영
        "description": "STT 스트리밍 테스트"
    }
    
    # 서버 응답 실패를 대비한 임시 정수형 세션 ID 기본값
    current_session_id = 1 
    
    try:
        session_res = requests.post(SESSION_API_URL, json=session_payload, timeout=5)
        if session_res.status_code in [200, 201]:
            print("✅ DB 세션 생성 성공!")
            try:
                # 서버가 생성 후 리턴해 준 실제 DB의 세션 고유 id(Integer)를 추출합니다.
                current_session_id = int(session_res.json().get("id", current_session_id))
                print(f"🔗 연동된 고유 세션 번호(ID): {current_session_id}")
            except Exception as e:
                print(f"⚠️ 세션 ID 파싱 실패, 기본값 {current_session_id}번으로 매핑합니다.")
        else:
            print(f"⚠️ 세션 생성 실패 (Code: {session_res.status_code}). 기본 1번 세션에 강제 연결합니다.")
    except Exception as e:
        print(f"⚠️ 세션 통신 에러: {e}. 기본 1번 세션으로 진행합니다.")

    # 3. 실시간 음성 인식 및 발화 전송 루프
    while True:
        try:
            with microphone as source:
                print("\n👂 듣는 중... (한/일 음성 입력 가능)")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("⏳ 음성 감지됨! 텍스트 변환 중...")
            temp_audio_path = "temp_speech.wav"
            with open(temp_audio_path, "wb") as f:
                f.write(audio.get_wav_data())
            
            segments, info = stt_model.transcribe(temp_audio_path, beam_size=1, vad_filter=True)
            detected_lang = info.language
            
            if detected_lang not in ['ko', 'ja']:
                detected_lang = 'ko'
            
            recognized_text = ""
            for segment in segments:
                recognized_text += segment.text + " "
            
            raw_text = recognized_text.strip()
            
            if raw_text:
                print("-" * 50)
                print(f"🗣️ [라즈베리파이 내부 검증 완료]")
                print(f"   - 변환된 문자: {raw_text}")
                print(f"   - 감지된 언어: {detected_lang}")
                print("-" * 50)
                
                print("📡 DB Utterance 테이블 규칙에 맞춰 API 호출 중...")
                
                # 🛠️ [DB 모델 매칭 Step 3] 데이터 양식 전면 수정
                utterance_payload = {
                    "session_id": int(current_session_id), # ⭕ 문자열이 아닌 정수(Integer) 데이터 타입 맞춤
                    "stt_text": raw_text,                  # ⭕ raw_text를 stt_text로 키 명칭 변경 (nullable=False 반영)
                    "language": detected_lang,             # ⭕ "ko" 또는 "ja" 문자열 데이터
                    "stt_model": "faster-whisper-tiny"     # 선택 필드 채우기
                }
                
                # POST /utterances 주소로 최종 데이터 전송
                response = requests.post(UTTERANCE_API_URL, json=utterance_payload, timeout=5)
                
                if response.status_code in [200, 201]:
                    print("📡 [성공] 데이터가 백엔드 DB 테이블에 정상 저장되었습니다!")
                else:
                    print(f"❌ [실패] 데이터 전송 실패 (응답 코드: {response.status_code})")
                    print(f"   - 서버 반환 메시지: {response.text}")
                    
        except sr.WaitTimeoutError:
            pass
        except Exception as e:
            print(f"오류 발생: {e}")
            
        time.sleep(0.5)

if __name__ == "__main__": 
    run_pi_node()
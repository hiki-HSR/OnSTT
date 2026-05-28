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

    # [DB 모델 매칭] 테스트용 1번 유저 타겟팅
    target_user_id = 1 
    
    print(f"⏳ 백엔드 서버에 회화 세션 생성 요청 중... ({SESSION_API_URL})")
    session_payload = {
        "user_id": target_user_id,
        "topic": "라즈베리파이 일본어 고정 세션",  
        "description": "STT 스트리밍 테스트"
    }
    
    current_session_id = 1 
    
    try:
        session_res = requests.post(SESSION_API_URL, json=session_payload, timeout=5)
        if session_res.status_code in [200, 201]:
            print("✅ DB 세션 생성 성공!")
            try:
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
                print("\n👂 듣는 중... (일본어 발음 복원 모드 구동 중)")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("⏳ 음성 감지됨! 고정밀 텍스트 변환 중...")
            temp_audio_path = "temp_speech.wav"
            with open(temp_audio_path, "wb") as f:
                f.write(audio.get_wav_data())
            
            # 🛠️ 민성 님 피드백 반영: 소리 그대로 정확하게 받아적기 위한 파라미터 튜닝
            segments, info = stt_model.transcribe(
                temp_audio_path, 
                language="ja",          # 일본어 고정
                beam_size=5,            # 정확도 탐색 경로 확장 (정확성 극대화)
                temperature=0.0,        # 환각 방지 및 입력 밀착도 강화
                vad_filter=True,        # 노이즈 제거
                suppress_tokens=[]      # 특정 토큰 생략 금지 (말한 그대로 수집)
            )
            
            recognized_text = ""
            for segment in segments:
                recognized_text += segment.text + " "
            
            raw_text = recognized_text.strip()
            
            if raw_text:
                print("-" * 50)
                print(f"🗣️ [라즈베리파이 내부 검증 완료]")
                print(f"   - 변환된 문자(날것): {raw_text}")
                print("-" * 50)
                
                print("📡 DB Utterance 테이블 규칙에 맞춰 API 호출 중...")
                
                utterance_payload = {
                    "session_id": int(current_session_id), 
                    "stt_text": raw_text,                  
                    "language": "ja",                      
                    "stt_model": "faster-whisper-tiny-tuned"     
                }
                
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
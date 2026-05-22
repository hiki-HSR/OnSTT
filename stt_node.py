import time 
import requests 
import socket
import speech_recognition as sr  
from faster_whisper import WhisperModel 
from cleaner import TextCleaner

# 1. IP 주소 자동 설정 함수
def get_target_ip():
    hostname = socket.gethostname().lower()
    if "raspberry" in hostname or "pi" in hostname:
        return "192.168.50.117"  
    else:
        return "127.0.0.1"       

# 2. 하드웨어 환경 감지 및 모델 설정 함수
def get_model_settings():
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda", "float16"
    except ImportError:
        pass
    return "cpu", "int8"

def run_pi_node(): 
    LAPTOP_IP = get_target_ip()
    DEVICE, COMPUTE_TYPE = get_model_settings()
    
    MODEL_SIZE = "tiny" 
    SERVER_URL = f"http://{LAPTOP_IP}:5001/process"  # 포트 5001 확인
    print(f"📡 데이터를 보낼 서버 주소: {SERVER_URL}")	

    # 3. 모델 및 전처리 엔진 초기화 
    print(f"-> 설정 반영 - Device: {DEVICE}, Compute Type: {COMPUTE_TYPE}")
    print("모델 로딩 중... (최초 1회 약 5~10초 소요)")
    stt_model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE) 
    cleaner = TextCleaner()
    print("✅ 모델 초기화 완료!")

    # 🛠️ 추가됨: 마이크 인식기 초기화
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    print("🎙️ 주변 소음 환경을 분석 중입니다... 잠시만 조용히 해주세요.")
    with microphone as source:
        # 주변 소음(선풍기 소리 등)을 1초간 듣고 기준점 설정
        recognizer.adjust_for_ambient_noise(source, duration=1)
    print("✅ 마이크 준비 완료! 이제 시스템이 듣고 있습니다.")

    # 4. 실제 STT를 수행하는 무한 반복 루프
    while True:
        try:
            with microphone as source:
                print("\n👂 듣는 중... (말씀해주세요)")
                # timeout=5: 5초 동안 아무 말 없으면 다시 루프
                # phrase_time_limit=10: 최대 10초 길이까지만 한 번에 녹음
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("⏳ 음성 감지됨! 텍스트로 변환 중...")
            
            # 음성 데이터를 임시 오디오 파일로 저장
            temp_audio_path = "temp_speech.wav"
            with open(temp_audio_path, "wb") as f:
                f.write(audio.get_wav_data())
            
            # 음성을 텍스트로 변환
            segments, info = stt_model.transcribe(temp_audio_path, beam_size=1, language="ko")
            
            recognized_text = ""
            for segment in segments:
                recognized_text += segment.text + " "
            
            if recognized_text.strip():
                print(f"🗣️ 인식된 원본: {recognized_text.strip()}")
                
                # 텍스트 정제
                cleaned_text = cleaner.clean(recognized_text)
                print(f"✨ 정제된 결과: {cleaned_text}")
                
                # 서버로 결과 전송
                data = {
                    "raw": recognized_text.strip(),
                    "refined": cleaned_text
                }
                response = requests.post(SERVER_URL, json=data)
                
                if response.status_code == 200:
                    print("📡 웹 서버(5001)로 전송 성공!")
                else:
                    print("⚠️ 서버 전송 실패")
                    
        except sr.WaitTimeoutError:
            # 5초 동안 아무 말도 하지 않았을 때 조용히 다시 듣기 상태로 돌아감
            pass
        except Exception as e:
            print(f"오류 발생: {e}")
            
        time.sleep(0.5)


if __name__ == "__main__": 
    run_pi_node()
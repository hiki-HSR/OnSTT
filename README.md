# 🎙️ Voice AI Control Center

실시간 음성 인식(STT)과 로컬 AI(LM Studio)를 연동하여, 한국어 음성을 일본어로 번역하고 결과를 시각화하는 AI 비서 파이프라인입니다.

## 🏗️ 시스템 아키텍처
[Image of simple software architecture diagram]

- **`stt_node.py`**: 마이크 음성 인식(faster-whisper) 및 서버 전송
- **`cleaner.py`**: KoNLPy(Okt) 기반 텍스트 전처리
- **`server.py`**: Flask 백엔드, LM Studio API 통신 및 웹 대시보드 서빙

---

## 🚀 환경 구축 (Installation)

### 1. 필수 프로그램
* **Java (OpenJDK 17+)**: `KoNLPy` 구동을 위해 필요합니다.
* **LM Studio**: 모델 구동 및 Local Server(v1/chat/completions)를 위해 필요합니다.

### 2. 프로젝트 세팅
```bash
# 1. 가상환경 생성
python -m venv venv

# 2. 가상환경 활성화 (Windows)
venv\Scripts\activate

# 3. 패키지 설치
pip install -r requirements.txt

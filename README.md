🎙️ Voice AI Control Center
이 프로젝트는 음성 인식(STT)을 통해 입력된 한국어를 실시간으로 정제하고, 로컬 AI 모델을 통해 일본어로 번역 및 응답을 생성하는 음성 기반 AI 비서 파이프라인입니다.

1. 시스템 구조
stt_node.py: 실시간 마이크 입력 감지, STT 변환(faster-whisper), 텍스트 정제 후 서버 전송.

cleaner.py: KoNLPy(Okt) 기반 텍스트 정제 모듈.

server.py: 데이터 수신, AI 연동(LM Studio API), 웹 대시보드 서빙.

2. 환경 구축 (Installation)
이 프로젝트는 파이썬 가상환경 사용을 권장합니다.

2-1. 필수 사전 프로그램
Java (OpenJDK): KoNLPy 구동을 위해 필요합니다. 설치 후 JAVA_HOME 환경 변수를 설정하세요.

LM Studio: 로컬 LLM 구동을 위한 프로그램입니다. (Local Server 탭에서 서버를 가동하세요.)

2-2. 환경 세팅 및 패키지 설치
requirements.txt를 사용하여 의존성을 관리합니다.

Bash
# 1. 가상환경 생성
python -m venv venv

# 2. 가상환경 활성화
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. 필수 패키지 설치
pip install -r requirements.txt
Git 사용자를 위한 팁: venv/ 폴더는 용량 문제로 Git에 올리지 않으며, .gitignore 파일에 추가하여 관리합니다. 다른 환경에서 배포 시 pip install -r requirements.txt만 실행하면 즉시 환경이 구축됩니다.

3. 실행 방법 (Usage)
각 프로세스는 별도의 터미널 창에서 실행해야 합니다.

AI 서버 가동 (LM Studio):
LM Studio를 켜고 모델을 로드한 뒤 Local Server 탭에서 Start 버튼을 누릅니다.

백엔드 서버 실행 (터미널 1):

Bash
python server.py
(브라우저에서 http://localhost:5001 접속 가능)

STT 노드 실행 (터미널 2):

Bash
python stt_node.py
4. 트러블슈팅
포트 충돌(Error 10013): 5001번 포트가 사용 중인 경우, server.py와 stt_node.py의 포트 설정을 다른 번호로 변경하세요.

Java Version 에러: Java 17 이상을 설치하고 환경 변수를 재설정(터미널 재시작 필수)했는지 확인하세요.

마이크 인식 불가: speech_recognition 라이브러리가 마이크 권한을 가지고 있는지 OS 설정을 확인하세요.

💡 프로젝트 구성 파일 관리
.gitignore 파일에 아래 내용을 포함하여 가상환경 및 불필요한 파일을 관리하세요:

Plaintext
venv/
__pycache__/
*.pyc
temp_speech.wav
새 기기에서 환경을 구축할 때는 pip freeze > requirements.txt로 생성된 파일을 Git에 올리고, 다른 PC에서 이를 pip install -r requirements.txt로 설치하여 동일한 환경을 유지하세요.

# 가이드

---

## 1. 사전 준비물

### 하드웨어

- 마이크가 연결된 컴퓨터
- 라즈베리 파이

### 소프트웨어

- **Python 3.10 ~ 3.11**
  - 최신 패키지와의 호환성이 좋습니다.
- **Java JDK 17 이상**
  - KoNLPy 기반 한국어 형태소 분석기 실행에 필요합니다.
- **LM Studio**
  - 로컬 LLM을 실행하고 API 서버(Local Server)를 열기 위해 사용합니다.

---

## 2. 전체 설치 가이드

### 2.1 가상환경 생성 및 의존성 설치

Git으로 프로젝트 코드를 클론한 뒤, 프로젝트 폴더에서 아래 명령어를 실행합니다.

```bash
# 1. 가상환경 생성
python -m venv venv

# 2. 가상환경 활성화

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# 3. 필수 패키지 설치
pip install -r requirements.txt
```

---

### 2.2 Java 환경 변수 설정

KoNLPy를 사용하기 위해 Java가 설치되어 있어야 합니다.

1. Adoptium Temurin 17 등에서 **JDK 17 이상**을 설치합니다.
2. 시스템 환경 변수에서 `JAVA_HOME`을 생성합니다.
3. `JAVA_HOME` 값에 JDK 설치 경로를 지정합니다.
4. `Path` 변수에 아래 경로를 추가합니다.

```text
%JAVA_HOME%\bin
```

5. 환경 변수 적용을 위해 열려 있는 터미널을 모두 종료한 뒤 다시 실행합니다.

---

## 3. 실행 순서

시스템 실행을 위해 총 3개의 프로그램 또는 터미널 창을 사용합니다.

실행 순서는 반드시 아래 순서를 따릅니다.

---

### Step 1. AI 엔진 실행

LM Studio에서 로컬 LLM 서버를 실행합니다.

1. LM Studio 프로그램을 실행합니다.
2. 우측 하단의 `Local Server` 아이콘을 클릭합니다.
3. 사용할 모델을 선택합니다.
4. `Start Server` 버튼을 눌러 서버를 실행합니다.
5. 서버 주소가 아래 형식인지 확인합니다.

```text
http://본인IP:5000/v1/chat/completions
```

예시:

```text
http://localhost:5000/v1/chat/completions
```

---

### Step 2. 백엔드 서버 실행

터미널 1에서 Flask 백엔드 서버를 실행합니다.  
이 서버는 STT 노드로부터 데이터를 받아 AI 모델로 전달하는 중계 역할을 합니다.

```bash
# 터미널 1

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

python server.py
```

정상적으로 실행되면 아래와 같은 메시지가 표시됩니다.

```text
* Running on http://0.0.0.0:5001/
```

---

### Step 3. STT 노드 실행

터미널 2에서 STT 노드를 실행합니다.  
STT 노드는 마이크 입력을 받아 음성을 텍스트로 변환하고, 변환된 데이터를 백엔드 서버로 전송합니다.

```bash
# 터미널 2

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

python stt_node.py
```

---

## 4. 대시보드 확인

웹 브라우저에서 아래 주소로 접속합니다.

```text
http://localhost:5001
```

대시보드에서는 다음 결과를 실시간으로 확인할 수 있습니다.

- 원본 음성 인식 결과
- 정제된 문장
- AI가 번역한 일본어 결과

---

## 5. 트러블슈팅

### 5.1 포트 충돌 오류

`Error 10013` 또는 포트 사용 중 오류가 발생하는 경우, `5001`번 포트가 이미 사용 중일 수 있습니다.

해결 방법:

1. `server.py`에서 포트 번호를 변경합니다.

```python
port=5001
```

예시:

```python
port=5002
```

2. `stt_node.py`의 `SERVER_URL`도 동일한 포트 번호로 수정합니다.

```python
SERVER_URL = "http://localhost:5002"
```

---

### 5.2 마이크 인식 불가

마이크 입력이 인식되지 않는 경우 아래 항목을 확인합니다.

1. 필요한 패키지가 설치되어 있는지 확인합니다.

```bash
pip install SpeechRecognition pyaudio
```

2. Windows 설정에서 앱의 마이크 접근 권한이 켜져 있는지 확인합니다.
3. 마이크가 정상적으로 연결되어 있는지 확인합니다.

---

### 5.3 번역 결과가 표시되지 않음

데이터가 번역되지 않는 경우, `server.py`에 설정된 LM Studio API 주소가 현재 실행 중인 LM Studio 서버 주소와 일치하는지 확인합니다.

예시:

```python
LM_STUDIO_URL = "http://localhost:5000/v1/chat/completions"
```

또는 네트워크 환경에 따라 아래와 같이 실제 IP 주소를 사용할 수 있습니다.

```python
LM_STUDIO_URL = "http://25.18.230.25:5000/v1/chat/completions"
```

---

## 6. 파일 구성

```text
project-root/
├── server.py
├── stt_node.py
├── cleaner.py
├── templates/
│   └── index.html
├── requirements.txt
└── README.md
```

### 주요 파일 설명

| 파일 | 설명 |
|---|---|
| `server.py` | Flask 백엔드 서버 및 LM Studio 번역 요청 처리 |
| `stt_node.py` | 음성 인식 및 서버 통신 처리 |
| `cleaner.py` | KoNLPy를 활용한 문장 정제 |
| `templates/index.html` | 실시간 대시보드 UI |
| `requirements.txt` | 프로젝트 실행에 필요한 Python 패키지 목록 |

---

## 7. Git 관리 시 주의사항

가상환경, 캐시 파일, 임시 음성 파일은 Git에 포함하지 않는 것이 좋습니다.

`.gitignore` 파일에 아래 내용을 추가합니다.

```gitignore
venv/
__pycache__/
*.pyc
temp_speech.wav
```

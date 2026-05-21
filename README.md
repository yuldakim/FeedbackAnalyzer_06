# Feedback Analyzer
![feedback_analyzer](./feedback_analyzer.png)

고객 피드백 분석 시스템은 자연어 기반 고객 피드백 데이터를 수집, 분류, 시각화하는 기능을 제공하는 Python(Flask) 기반 웹 애플리케이션입니다.

## 주요 기능

- 텍스트 피드백 입력 (수동/CSV 업로드)
- 키워드 기반 피드백 분류
- 감정 분석 (긍정/부정/중립)
- 피드백 필터링 및 검색
- 분석 결과 시각화
- 결과 CSV 다운로드

## 요구사항

- Python 3.9 이상
- pip

## 설치 및 실행 방법 (가상환경)

### 1. 저장소 클론
```bash
git clone [repository-url]
cd feedback_analyzer_python
```

### 2. 가상환경 생성

#### Windows
```bash
cd src/python
python -m venv .venv
```

#### macOS / Linux
```bash
cd src/python
python3 -m venv .venv
```

### 3. 가상환경 활성화

#### Windows (PowerShell)
```powershell
.venv\Scripts\Activate.ps1
```

#### Windows (CMD)
```cmd
.venv\Scripts\activate.bat
```

#### macOS / Linux
```bash
source .venv/bin/activate
```

> 활성화되면 터미널 프롬프트 앞에 `(.venv)`가 표시됩니다.

### 4. 의존성 설치
```bash
pip install -r requirements.txt
```

### 5. 서버 실행
```bash
python app.py
```

서버가 시작되면 브라우저에서 `http://localhost:8080` 으로 접속합니다.

### 6. 가상환경 비활성화
작업이 끝나면 아래 명령으로 가상환경을 종료합니다.
```bash
deactivate
```

## 프로젝트 구조

```
feedback_analyzer/
├── src/python/
│   ├── app.py              # Flask 웹 서버 및 라우팅, HTML 렌더링
│   ├── feedback.py         # 피드백 데이터 모델
│   ├── text_analyzer.py    # 텍스트 분석 로직
│   ├── filters.py          # 필터링
│   ├── session.py          # 상태 관리
│   ├── logger.py           # 로깅
│   ├── constants.py        # 상수 정의 (감정 키워드, 카테고리 키워드)
│   ├── file_handler.py     # 파일 처리 (미사용)
│   └── requirements.txt    # Python 의존성
├── project_purpose.md      # 프로젝트 목적 문서
└── README.md               # 프로젝트 설명
```

## 사용 방법

1. 웹 브라우저에서 `http://localhost:8080` 접속
2. 피드백 텍스트 입력 또는 CSV 파일 업로드
3. 감정/키워드 필터로 결과 필터링
4. 필요시 결과 다운로드

## CSV 파일 형식

입력 CSV 파일은 다음과 같은 형식이어야 합니다:
- 필수 컬럼: `text`
- 텍스트 컬럼에 피드백 내용 포함

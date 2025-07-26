# MCP 서버 (Confluence 연동)

Confluence 자동화 및 통합을 위한 미들웨어(MCP) 서버입니다.

## ✨ 주요 기능

- REST API를 통한 Confluence 페이지 생성
- CI/CD, 모니터링 등 외부 시스템과의 연동 허브
- 맞춤형 문서 자동화 워크플로우 지원

## 🚀 시작하기

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성하고, Confluence 접속 정보를 입력합니다.

```bash
cp .env.example .env
# .env 파일 내용 수정
```

### 3. 서버 실행

```bash
uvicorn app.main:app --reload
```

서버가 실행되면 `http://127.0.0.1:8000/docs` 에서 자동 생성된 API 문서를 확인할 수 있습니다.


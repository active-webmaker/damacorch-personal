# 페이지에 필요한 UI 요소 목록
## 마이페이지
새 성향분석 시작
성향 분석 히스토리(게시판 목록) 버튼(링크)

---

## DB 설계

### 1. 기본 개념
- 마이페이지에서 하는 일
  - 현재 로그인한 유저 기준으로
    - "새 성향분석 시작" 액션 진입
    - 과거 성향 분석 결과 히스토리 페이지로 이동
- 필요한 데이터
  - 유저 기본 정보 (필요 시)
  - 유저의 성향 분석 결과 목록 (최근 N개 등)

### 2. 주요 테이블

#### 2-1. users (요약)
- **테이블명**: `users`
- 서비스 전반에서 공통으로 사용하는 유저 테이블 (이미 다른 문서에서 정의되어 있음)
- 여기서는 `id`, `name`, `email` 정도만 사용 가능하면 충분

#### 2-2. analysis_results (성향 분석 결과)
- **테이블명**: `analysis_results`
- 마이페이지에서 필요한 컬럼 (요약)
  - `id` (bigint, PK)
  - `user_id` (bigint, FK → users.id)
  - `character_name` (varchar(100))
  - `summary` (text)
  - `created_at` (datetime)
- 히스토리 목록에서는 `character_name`, `summary`, `created_at` 정도만 노출하고, 상세는 결과 페이지(`/analysis-result?resultId=...`)에서 보여줌.

---

## API 설계

### 1. 마이페이지 초기 데이터 조회 (선택)

#### 1) GET /api/mypage
- **설명**
  - 마이페이지 진입 시, 현재 로그인 유저의 기본 정보와 최근 성향 분석 결과 몇 개를 같이 내려줄 때 사용
- **응답 예시**
  ```json
  {
    "user": {
      "id": 45,
      "name": "홍길동"
    },
    "recentAnalysisResults": [
      {
        "id": 123,
        "characterName": "도시형 탐험가",
        "summary": "당신은 사람들과 함께할 때 에너지를 얻지만...",
        "createdAt": "2026-02-05T12:34:56Z"
      },
      {
        "id": 122,
        "characterName": "사색하는 마법사",
        "summary": "깊이 있는 관계를 선호하며...",
        "createdAt": "2026-01-31T09:10:11Z"
      }
    ]
  }
  ```

### 2. 성향 분석 히스토리 페이지용 목록 API

#### 2) GET /api/users/{userId}/analysis-results
- **설명**
  - 특정 유저의 전체(또는 페이징된) 성향 분석 결과 목록을 조회
  - "성향 분석 히스토리(게시판 목록)" 페이지에서 사용 (마이페이지에서는 버튼/링크만 제공)
- **Path 파라미터**
  - `userId`: 현재 로그인 유저 ID
- **Query 파라미터(선택)**
  - `page`, `pageSize` 또는 `limit`, `offset`
- **응답 예시**
  ```json
  {
    "items": [
      {
        "id": 123,
        "characterName": "도시형 탐험가",
        "summary": "당신은 사람들과 함께할 때 에너지를 얻지만...",
        "createdAt": "2026-02-05T12:34:56Z"
      }
    ],
    "totalCount": 10
  }
  ```

### 3. 새 성향분석 시작 진입

#### 3) POST /api/analysis/start (또는 프론트 라우팅만 사용)
- **설명**
  - 마이페이지에서 "새 성향분석 시작" 버튼 클릭 시 사용할 엔드포인트에 대한 메모
  - 실제 구현은 다음 두 가지 중 하나로 선택 가능
    - 프론트 라우팅만: 버튼 클릭 시 바로 성격 검사/셀프체크 페이지(`/psy_test`, `/self_check`)로 이동
    - 혹은 서버에서 "새 분석 세션"을 발급한 뒤 해당 세션 ID와 함께 페이지 이동
- **요청/응답 예시 (세션 발급 방식 가정)**
  ```json
  // 요청 Body (필요 없을 수도 있음)
  {}
  ```
  ```json
  // 응답
  {
    "analysisSessionId": 999,
    "redirectPath": "/psy_test?sessionId=999"
  }
  ```

---

## 화면 요소 ↔ DB/API 매핑 메모
- 새 성향분석 시작
  - 기본: 프론트 라우팅으로 성향 분석 시작 페이지(`/psy_test`, `/self_check` 등)로 이동
  - 필요 시: `POST /api/analysis/start`로 세션 발급 후, 응답의 `redirectPath`로 이동
- 성향 분석 히스토리(게시판 목록) 버튼(링크)
  - 프론트 라우팅: `/quest_history` 또는 `/analysis-history` 등 히스토리 페이지로 이동
  - 히스토리 페이지에서 사용할 API: `GET /api/users/{userId}/analysis-results`
  - DB: `analysis_results`
# 퀘스트 페이지
## 페이지에 필요한 UI 요소 목록
퀘스트 종류 탭(일일, 주간)
삭제, 완료 버튼(체크박스와 연동)
퀘스트 섹션(퀘스트 3개, 체크박스)
히스토리 버튼(히스토리 페이지로 이동)

---

## DB 설계

### 1. 기본 개념
- 이 페이지에서 하는 일
  - 현재 유저의 **오늘 일일 퀘스트 최대 3개**, **이번 주 주간 퀘스트**를 탭으로 전환하며 보여줌
  - 각 퀘스트에 체크박스로 완료/삭제 상태를 변경
- 필요한 데이터
  - 퀘스트 마스터 정보(제목, 설명, 타입 등)
  - 유저별 퀘스트 인스턴스(상태, 날짜 정보 등)

### 2. 주요 테이블

> `home.md`, `quest_history.md`에서 정의한 퀘스트 테이블 재사용

#### 2-1. quest_templates (퀘스트 마스터)
- **테이블명**: `quest_templates`
- (요약)
  - `id` (bigint, PK)
  - `title` (varchar(200))
  - `description` (text)
  - `type` (varchar(20)) — `"daily"`, `"weekly"` 등
  - `is_active` (boolean)
  - `created_at`, `updated_at`

#### 2-2. user_quests (유저별 퀘스트 인스턴스)
- **테이블명**: `user_quests`
- (요약)
  - `id` (bigint, PK)
  - `user_id` (bigint, FK → users.id)
  - `quest_template_id` (bigint, FK → quest_templates.id)
  - `status` (varchar(20))
    - 예: `"pending"`, `"completed"`, `"deleted"`
  - `period_date` (date, nullable)
    - 일간 퀘스트 기준일 (오늘 일일 퀘스트 필터용)
  - `week_start_date` (date, nullable)
    - 주간 퀘스트 주 시작일
  - `created_at` (datetime)
  - `completed_at` (datetime, nullable)

퀘스트 페이지에서는 현재 날짜/주 기준으로 `user_quests`를 조회하여 탭별 리스트를 구성.

---

## API 설계

### 1. 오늘/이번 주 퀘스트 목록 조회

#### 1) GET /api/quests
- **설명**
  - 현재 로그인 유저 기준으로, 오늘의 일일 퀘스트와 이번 주의 주간 퀘스트 목록을 조회
  - 탭(일일/주간)을 나누어 한 번에 내려주거나, 쿼리 파라미터로 타입을 분리해도 됨 (여기서는 한 번에 내려오는 형태 예시)
- **쿼리 파라미터 (선택)**
  - `date`: 기준 날짜 (지정 없으면 오늘)
- **응답 예시**
  ```json
  {
    "daily": [
      {
        "userQuestId": 1001,
        "title": "오늘 30분 이상 걷기",
        "description": "가벼운 산책으로 몸을 풀어보세요.",
        "status": "pending"
      },
      {
        "userQuestId": 1002,
        "title": "감사 일기 3줄 쓰기",
        "description": "오늘 있었던 좋은 일 3가지를 적어보세요.",
        "status": "completed"
      }
    ],
    "weekly": [
      {
        "userQuestId": 2001,
        "title": "이번 주에 친구 1명에게 연락하기",
        "description": "오래 연락하지 못한 친구에게 근황을 전해보세요.",
        "status": "pending"
      }
    ]
  }
  ```

### 2. 퀘스트 상태 변경 (완료/삭제)

#### 2) PATCH /api/quests/{userQuestId}
- **설명**
  - 체크박스와 연동되어, 개별 퀘스트의 상태를 `pending` ↔ `completed` 또는 `deleted`로 변경
- **Path 파라미터**
  - `userQuestId`: `user_quests.id`
- **요청 Body 예시**
  ```json
  {
    "status": "completed"
  }
  ```
- **응답 예시**
  ```json
  {
    "userQuestId": 1001,
    "status": "completed"
  }
  ```

#### 3) PATCH /api/quests/bulk-status (선택)
- **설명**
  - 여러 퀘스트를 한 번에 완료/삭제 처리하고 싶을 때 사용 (체크박스로 다중 선택 후 버튼 클릭)
- **요청 Body 예시**
  ```json
  {
    "userQuestIds": [1001, 1002],
    "status": "deleted"
  }
  ```
- **응답 예시**
  ```json
  {
    "updatedCount": 2
  }
  ```

---

## 화면 요소 ↔ DB/API 매핑 메모
- 퀘스트 종류 탭(일일, 주간)
  - API: `GET /api/quests` 응답의 `daily`, `weekly`를 탭으로 나누어 표시
  - DB: `user_quests`, `quest_templates`
- 삭제, 완료 버튼(체크박스와 연동)
  - 단일 처리: `PATCH /api/quests/{userQuestId}`
  - 다중 처리(선택): `PATCH /api/quests/bulk-status`
  - DB: `user_quests.status`, `user_quests.completed_at`
- 퀘스트 섹션(퀘스트 3개, 체크박스)
  - API: `GET /api/quests`에서 받은 리스트를 최대 3개까지 표시 (UI 정책)
  - 각 아이템: 제목/설명/현재 상태 + 선택용 체크박스
- 히스토리 버튼(히스토리 페이지로 이동)
  - 프론트 라우팅: `/quest_history` 페이지로 이동
  - 히스토리 페이지에서는 `GET /api/quest-history`, `GET /api/quest-history/summary` 사용 (별도 문서 참조)


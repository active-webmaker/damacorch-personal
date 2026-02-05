# 퀘스트 히스토리(게시판 목록이 아니라 캘린더 형태)
## 페이지에 필요한 UI 요소 목록
뒤로가기 버튼
캘린더(연/월/일 포맷, 비동기 통신으로 특정 날짜의 히스토리 조회)

---

## DB 설계

### 1. 기본 개념
- 이 페이지에서 하는 일
  - 캘린더에서 날짜(연/월/일)를 선택하면, 해당 날짜에 수행한 **일간/주간 퀘스트 히스토리**를 보여줌
- 필요한 데이터
  - 유저별 퀘스트 인스턴스(언제 어떤 퀘스트를 했는지, 완료 여부 등)

### 2. 주요 테이블

> 홈 화면에서 정의한 퀘스트 관련 테이블(`quest_templates`, `user_quests`)을 재사용

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
  - `status` (varchar(20)) — `"pending"`, `"completed"`, `"deleted"` 등
  - `period_date` (date, nullable)
    - 일간 퀘스트 기준일 (해당 날짜의 히스토리 필터 기준)
  - `week_start_date` (date, nullable)
    - 주간 퀘스트 주 시작일
  - `created_at` (datetime)
  - `completed_at` (datetime, nullable)

이 페이지에서는 `period_date`(일간), `week_start_date`(주간)와 캘린더에서 선택된 날짜를 기준으로 히스토리를 필터링.

---

## API 설계

### 1. 특정 날짜의 퀘스트 히스토리 조회

#### 1) GET /api/quest-history
- **설명**
  - 쿼리 파라미터의 날짜(연/월/일)를 기준으로, 해당 날짜에 해당하는 퀘스트 수행 기록을 가져옴
  - 캘린더에서 날짜를 클릭할 때마다 비동기 호출
- **Query 파라미터**
  - `date` (필수): ISO 포맷 문자열 예: `"2026-02-05"`
- **인증**
  - 로그인 유저 기준 (`userId`는 토큰/세션에서 추출)
- **응답 예시**
  ```json
  {
    "date": "2026-02-05",
    "dailyQuests": [
      {
        "userQuestId": 1001,
        "title": "오늘 30분 이상 걷기",
        "description": "가벼운 산책으로 몸을 풀어보세요.",
        "status": "completed",
        "completedAt": "2026-02-05T20:10:00Z"
      }
    ],
    "weeklyQuests": [
      {
        "userQuestId": 2001,
        "title": "이번 주에 친구 1명에게 연락하기",
        "description": "오래 연락하지 못한 친구에게 근황을 전해보세요.",
        "status": "pending",
        "weekStartDate": "2026-02-03"
      }
    ]
  }
  ```

### 2. 월 단위 히스토리 요약 (선택)

#### 2) GET /api/quest-history/summary
- **설명**
  - 캘린더에 "어떤 날짜에 퀘스트가 있는지"를 표시하기 위한 요약 데이터 (점/마커 표시용)
- **Query 파라미터**
  - `year` (필수): 예: `2026`
  - `month` (필수): 예: `2` (또는 `02`)
- **응답 예시**
  ```json
  {
    "year": 2026,
    "month": 2,
    "days": [
      {
        "date": "2026-02-01",
        "hasQuest": true,
        "completedCount": 2,
        "totalCount": 3
      },
      {
        "date": "2026-02-05",
        "hasQuest": true,
        "completedCount": 1,
        "totalCount": 1
      }
    ]
  }
  ```

---

## 화면 요소 ↔ DB/API 매핑 메모
- 뒤로가기 버튼
  - 프론트 라우팅(`/mypage` 또는 `/home`) 처리, DB 직접 연관 없음
- 캘린더(연/월/일 포맷, 비동기 통신으로 특정 날짜의 히스토리 조회)
  - 월 전환/로드 시
    - API: `GET /api/quest-history/summary?year=YYYY&month=MM`
    - DB: `user_quests`, `quest_templates`
  - 날짜 클릭 시
    - API: `GET /api/quest-history?date=YYYY-MM-DD`
    - DB: `user_quests`, `quest_templates`


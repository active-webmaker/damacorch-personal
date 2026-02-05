# 홈 화면
## 페이지에 필요한 UI 요소 목록
로그아웃 버튼
캐릭터 이미지 섹션
캐릭터 이름 섹션
캐릭터 상태 섹션
일간 퀘스트 3개 섹션
주간 퀘스트 1개 섹션

---

## DB 설계

### 1. 기본 개념
- 홈 화면에는 아래 데이터가 필요함
  - 현재 로그인 유저 정보 (로그아웃 버튼은 프론트/세션 처리)
  - 유저의 "현재 캐릭터" 정보 (이미지, 이름, 상태)
  - 오늘의 일간 퀘스트 최대 3개
  - 이번 주의 주간 퀘스트 최대 1개

### 2. 주요 테이블

#### 2-1. users (요약)
- 이미 존재한다고 가정 (또는 별도 정의)
- **컬럼 예시**
  - `id` (PK, bigint)
  - `email` (unique)
  - `name`
  - `created_at`
  - `updated_at`

#### 2-2. analysis_results (캐릭터 정보 출처, 참고)
- 홈 화면의 "캐릭터 이미지/이름/상태"는 최근 분석 결과를 기반으로 가져올 수 있음
- (상세 구조는 `analysis_result.md` 참고)
- 이 페이지에서 사용하는 컬럼
  - `user_id`
  - `character_name`
  - `character_image_url`
  - `summary` 또는 별도의 상태 컬럼이 있다면 그 값으로 "캐릭터 상태" 표현

#### 2-3. quest_templates (퀘스트 마스터)
- **테이블명**: `quest_templates`
- 퀘스트의 정적 정보(제목, 설명, 유형 등)를 관리
- **컬럼**
  - `id` (bigint, PK)
  - `title` (varchar(200))
  - `description` (text)
  - `type` (varchar(20))
    - 예: `"daily"`, `"weekly"`
  - `is_active` (boolean)
  - `created_at` (datetime)
  - `updated_at` (datetime)

#### 2-4. user_quests (유저별 퀘스트 인스턴스)
- **테이블명**: `user_quests`
- 유저에게 실제로 할당된 퀘스트와 그 상태를 관리
- **컬럼**
  - `id` (bigint, PK)
  - `user_id` (bigint, FK → users.id)
  - `quest_template_id` (bigint, FK → quest_templates.id)
  - `status` (varchar(20))
    - 예: `"pending"`, `"completed"`, `"deleted"`
  - `period_date` (date, nullable)
    - 일간 퀘스트 기준일(예: 2026-02-05)
  - `week_start_date` (date, nullable)
    - 주간 퀘스트 주 시작일(예: 2026-02-03)
  - `created_at` (datetime)
  - `completed_at` (datetime, nullable)

홈 화면에서는 위 테이블에서 **오늘 날짜 기준 일간 퀘스트 3개**, **이번 주 기준 주간 퀘스트 1개**를 조회해서 사용.

---

## API 설계

### 1. 홈 화면 요약 데이터 조회

#### 1) GET /api/home
- **설명**
  - 현재 로그인한 유저 기준으로 홈 화면에 필요한 모든 데이터를 한 번에 조회
- **인증**
  - 로그인 세션/토큰에서 `userId`를 식별한다고 가정
- **응답 예시**
  ```json
  {
    "user": {
      "id": 45,
      "name": "홍길동"
    },
    "character": {
      "name": "도시형 탐험가",
      "imageUrl": "https://.../characters/explorer.png",
      "status": "오늘은 에너지가 높고, 새로운 도전을 즐기기 좋은 상태입니다."
    },
    "dailyQuests": [
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
    "weeklyQuest": {
      "userQuestId": 2001,
      "title": "이번 주에 친구 1명에게 연락하기",
      "description": "오래 연락하지 못한 친구에게 근황을 전해보세요.",
      "status": "pending"
    }
  }
  ```

### 2. 내부 쿼리 로직 메모 (백엔드 구현 참고)
- 캐릭터 정보
  - `analysis_results`에서 `user_id = 현재유저` 인 레코드 중, 가장 최근(`created_at` DESC) 1건 조회
- 일간 퀘스트 3개
  - `user_quests`에서
    - `user_id = 현재유저`
    - `status != "deleted"`
    - `period_date = 오늘날짜`
    - `JOIN quest_templates ON quest_template_id = quest_templates.id AND quest_templates.type = "daily"`
    - 최대 3건
- 주간 퀘스트 1개
  - `user_quests`에서
    - `user_id = 현재유저`
    - `status != "deleted"`
    - `week_start_date = 이번 주 시작일`
    - `JOIN quest_templates ON quest_template_id = quest_templates.id AND quest_templates.type = "weekly"`
    - 최대 1건

---

## 화면 요소 ↔ DB/API 매핑 메모
- 로그아웃 버튼
  - 프론트에서 세션/토큰 삭제 + 로그인 페이지로 이동 (DB 컬럼 없음)
- 캐릭터 이미지 섹션
  - DB: `analysis_results.character_image_url`
  - API: `character.imageUrl`
- 캐릭터 이름 섹션
  - DB: `analysis_results.character_name`
  - API: `character.name`
- 캐릭터 상태 섹션
  - DB: `analysis_results.summary` 혹은 별도 상태 컬럼
  - API: `character.status`
- 일간 퀘스트 3개 섹션
  - DB: `user_quests`, `quest_templates`
  - API: `dailyQuests[]`
- 주간 퀘스트 1개 섹션
  - DB: `user_quests`, `quest_templates`
  - API: `weeklyQuest`
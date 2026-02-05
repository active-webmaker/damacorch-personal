# 페이지에 필요한 UI 요소 목록
## 성격 검사
뒤로가기
심리 검사 문항 섹션(문항 50개)
제출 버튼

---

## DB 설계

### 1. 기본 개념
- 이 페이지에서 하는 일
  - 유저가 **심리 검사 문항 50개**에 답변 → 서버에서 점수/타입을 계산 → 분석 결과(`analysis_results`)를 생성하는 입력 단계
- 필요한 데이터
  - 심리 검사 **문항 마스터** (질문 내용, 문항 순서, 점수 방향 등)
  - 유저가 각 문항에 어떻게 응답했는지(응답 저장)
  - (선택) 검사 세션 정보

### 2. 주요 테이블

#### 2-1. psy_questions (심리 검사 문항 마스터)
- **테이블명**: `psy_questions`
- 심리 검사에 사용되는 문항 정의(50개)
- **컬럼 예시**
  - `id` (bigint, PK)
  - `code` (varchar(50), nullable)
    - 필요 시 문항 코드를 부여 (예: `"Q1"` ~ `"Q50"`)
  - `text` (text)
    - 질문 내용
  - `order_index` (int)
    - 문항 순서 (1~50)
  - `scale_min` (int)
    - 응답 최소값 (예: 1)
  - `scale_max` (int)
    - 응답 최대값 (예: 5)
  - `reverse_scored` (boolean)
    - 역채점 여부(점수 계산 시 방향 반전 필요할 때)
  - `created_at` (datetime)
  - `updated_at` (datetime)

#### 2-2. psy_test_sessions (선택: 검사 세션)
- **테이블명**: `psy_test_sessions`
- 한 번의 검사 진행을 하나의 세션으로 관리하고 싶을 때 사용 (마이페이지의 `analysis_start`와 연결 가능)
- **컬럼 예시**
  - `id` (bigint, PK)
  - `user_id` (bigint, FK → users.id)
  - `status` (varchar(20))
    - 예: `"in_progress"`, `"completed"`
  - `created_at` (datetime)
  - `completed_at` (datetime, nullable)

#### 2-3. psy_answers (유저 응답)
- **테이블명**: `psy_answers`
- 유저가 각 문항에 대해 제출한 응답을 저장
- **컬럼 예시**
  - `id` (bigint, PK)
  - `user_id` (bigint, FK → users.id)
  - `session_id` (bigint, FK → psy_test_sessions.id, nullable)
    - 세션을 사용하지 않는다면 nullable 또는 미사용 가능
  - `question_id` (bigint, FK → psy_questions.id)
  - `answer_value` (int)
    - 예: 1~5 Likert 척도
  - `created_at` (datetime)

#### 2-4. analysis_results (연결)
- 실제 성향 분석 결과는 `analysis_results`에 저장 (이미 다른 문서에서 정의)
- 이 페이지에서 제출된 `psy_answers`를 바탕으로 점수/타입을 계산한 뒤, 새로운 `analysis_results` 레코드를 생성

---

## API 설계

### 1. 심리 검사 문항 목록 조회

#### 1) GET /api/psy-test/questions
- **설명**
  - 성격 검사 페이지 진입 시, 50개 문항을 한 번에 가져오기
- **응답 예시**
  ```json
  [
    {
      "id": 1,
      "order": 1,
      "text": "나는 새로운 사람을 만나는 것을 즐긴다.",
      "scaleMin": 1,
      "scaleMax": 5
    },
    {
      "id": 2,
      "order": 2,
      "text": "나는 계획을 세우기보다 즉흥적으로 행동하는 편이다.",
      "scaleMin": 1,
      "scaleMax": 5
    }
  ]
  ```

### 2. 심리 검사 응답 제출

#### 2) POST /api/psy-test/submit
- **설명**
  - 심리 검사 문항 50개에 대한 유저의 응답을 제출
  - 서버에서는 응답을 저장하고, 점수 계산 후 `analysis_results`에 결과를 생성
- **요청 Body 예시**
  ```json
  {
    "sessionId": 999,
    "answers": [
      { "questionId": 1, "value": 4 },
      { "questionId": 2, "value": 2 }
      // ... 최대 50개
    ]
  }
  ```
- **응답 예시**
  ```json
  {
    "analysisResultId": 123,
    "redirectPath": "/analysis-result?resultId=123"
  }
  ```
- **로직 메모**
  - `psy_answers`에 각 응답을 저장
  - 필요 시 `psy_test_sessions` 상태를 `completed`로 변경
  - 점수/타입 계산 로직을 수행해 `analysis_results`에 새 레코드 생성

---

## 화면 요소 ↔ DB/API 매핑 메모
- 뒤로가기
  - 프론트 라우팅(`/mypage` 또는 이전 페이지) 처리, DB 직접 연관 없음
- 심리 검사 문항 섹션(문항 50개)
  - DB: `psy_questions`
  - API: `GET /api/psy-test/questions`
- 제출 버튼
  - API: `POST /api/psy-test/submit`
  - Body: `sessionId`(선택), `answers[]` (각 문항의 `questionId`, `value`)
  - 응답의 `redirectPath` 또는 `analysisResultId`를 사용해 분석 결과 페이지로 이동


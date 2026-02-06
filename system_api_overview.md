# 전체 시스템 개요 (DB & API 설계 요약)

이 문서는 `damacorch_personal` 프로젝트의 주요 페이지 설계 문서들
(`start_page.md`, `login.md`, `signup.md`, `home.md`, `self_check.md`, `psy_test.md`,
`analysis_result.md`, `quest_page.md`, `quest_history.md`, `import_sns.md`, `mypage.md`, `common.md` 등)
을 기반으로 **공통 DB 설계와 API 엔드포인트**를 한 번에 정리한 개요입니다.

---

## 1. 주요 도메인 개요

- **인증/계정**: 로그인, 회원가입, 현재 유저 정보 조회
- **사용자 프로필/셀프체크**: 기본 프로필 + 성향 분석 보조 입력 값
- **심리 검사/분석 결과**: 50문항 심리 검사와 그 결과(`analysis_results`)
- **퀘스트**: 일일/주간 퀘스트, 히스토리(캘린더)
- **SNS 연동**: SNS 채널 연결 및 가져오기 트리거
- **앱 설정/브랜딩**: 서비스 로고 등

---

## 2. DB 설계 요약 (ERD 텍스트)

### 2.1 유저 & 인증 관련

#### 2.1.1 users
- **테이블명**: `users`
- **설명**: 계정 및 기본 프로필 정보 공통 저장소 (인증은 AWS Cognito에서 수행하고, Django는 JWT를 검증하여 사용자 식별)
- **컬럼 (요약)**
  - `id` (bigint, PK)
  - `email` (varchar(255), unique)
  - `name` (varchar(100))
  - `age` (int 또는 birth_year 등)
  - `gender` (varchar(20))
  - `cognito_sub` (varchar(64), unique) — Cognito User Pool의 `sub` 클레임 값 매핑용
  - `created_at` (datetime)
  - `updated_at` (datetime)
  - `last_login_at` (datetime, nullable)

> 참고: 이 프로젝트에서는 **비밀번호 해시 및 JWT 발급/저장 로직을 로컬 DB에 두지 않고**, AWS Cognito가 비밀번호/토큰을 관리하며, 백엔드는 Cognito가 발급한 JWT를 검증하는 역할만 담당합니다.

---

### 2.2 성향 분석/심리 검사 도메인

#### 2.2.1 analysis_results
- **테이블명**: `analysis_results`
- **설명**: 한 번의 성향 분석 결과(캐릭터, 요약, 성향/취향/코칭)를 저장
- **컬럼 (요약)**
  - `id` (bigint, PK)
  - `user_id` (bigint, FK → users.id)
  - `character_name` (varchar(100))
  - `character_image_url` (varchar(255))
  - `summary` (text)
  - `tendency_personality` (text)
  - `tendency_behavior_pattern` (text)
  - `preference_likes` (text)
  - `preference_dislikes` (text)
  - `coaching_tips` (text)
  - `source_type` (varchar(50), nullable)
  - `source_id` (bigint, nullable)
  - `created_at` (datetime)
  - `updated_at` (datetime)

#### 2.2.2 psy_questions
- **테이블명**: `psy_questions`
- **설명**: 성격 검사(50문항) 문항 마스터
- **컬럼 (요약)**
  - `id` (bigint, PK)
  - `code` (varchar(50), nullable)
  - `text` (text)
  - `order_index` (int)
  - `scale_min` (int)
  - `scale_max` (int)
  - `reverse_scored` (boolean)
  - `created_at` (datetime)
  - `updated_at` (datetime)

#### 2.2.3 psy_test_sessions (선택)
- **테이블명**: `psy_test_sessions`
- **설명**: 한 번의 심리 검사 진행 세션
- **컬럼 (요약)**
  - `id` (bigint, PK)
  - `user_id` (bigint, FK → users.id)
  - `status` (varchar(20)) — `"in_progress"`, `"completed"`
  - `created_at` (datetime)
  - `completed_at` (datetime, nullable)

#### 2.2.4 psy_answers
- **테이블명**: `psy_answers`
- **설명**: 심리 검사 문항에 대한 유저 응답
- **컬럼 (요약)**
  - `id` (bigint, PK)
  - `user_id` (bigint, FK → users.id)
  - `session_id` (bigint, FK → psy_test_sessions.id, nullable)
  - `question_id` (bigint, FK → psy_questions.id)
  - `answer_value` (int)
  - `created_at` (datetime)

---

### 2.3 셀프 체크 도메인

#### 2.3.1 self_check_entries
- **테이블명**: `self_check_entries`
- **설명**: 성향 분석 셀프 체크 입력 값(라이프스타일/선호 등)
- **컬럼 (요약)**
  - `id` (bigint, PK)
  - `user_id` (bigint, FK → users.id)
  - `hobby` (text)
  - `sleep_pattern` (varchar(50))
  - `exercise_flag` (boolean)
  - `exercise_per_week` (int)
  - `exercise_type` (varchar(20)) — `"aerobic"`, `"anaerobic"`, `"both"`
  - `pet_type` (varchar(100))
  - `mbti` (varchar(4))
  - `outing_per_week` (int)
  - `speech_audio_path` (varchar(255), nullable)
  - `self_intro_doc_path` (varchar(255), nullable)
  - `created_at` (datetime)

---

### 2.4 퀘스트 도메인

#### 2.4.1 quest_templates
- **테이블명**: `quest_templates`
- **설명**: 퀘스트 마스터(제목, 설명, 유형 등)
- **컬럼 (요약)**
  - `id` (bigint, PK)
  - `title` (varchar(200))
  - `description` (text)
  - `type` (varchar(20)) — `"daily"`, `"weekly"` 등
  - `is_active` (boolean)
  - `created_at` (datetime)
  - `updated_at` (datetime)

#### 2.4.2 user_quests
- **테이블명**: `user_quests`
- **설명**: 유저별 퀘스트 인스턴스(오늘/이번 주 퀘스트, 히스토리)
- **컬럼 (요약)**
  - `id` (bigint, PK)
  - `user_id` (bigint, FK → users.id)
  - `quest_template_id` (bigint, FK → quest_templates.id)
  - `status` (varchar(20)) — `"pending"`, `"completed"`, `"deleted"`
  - `period_date` (date, nullable) — 일간 퀘스트 기준일
  - `week_start_date` (date, nullable) — 주간 퀘스트 주 시작일
  - `created_at` (datetime)
  - `completed_at` (datetime, nullable)

---

### 2.5 SNS 연동 도메인

#### 2.5.1 sns_channels
- **테이블명**: `sns_channels`
- **설명**: 지원하는 SNS 채널 마스터
- **컬럼 (요약)**
  - `id` (bigint, PK)
  - `code` (varchar(50), unique) — `"instagram"`, `"facebook"` 등
  - `name` (varchar(100))
  - `icon_url` (varchar(255), nullable)
  - `is_active` (boolean)
  - `created_at` (datetime)
  - `updated_at` (datetime)

#### 2.5.2 user_sns_accounts
- **테이블명**: `user_sns_accounts`
- **설명**: 유저별 SNS 계정 연동 정보
- **컬럼 (요약)**
  - `id` (bigint, PK)
  - `user_id` (bigint, FK → users.id)
  - `sns_channel_id` (bigint, FK → sns_channels.id)
  - `external_user_id` (varchar(255))
  - `display_name` (varchar(255), nullable)
  - `access_token` (text, nullable)
  - `refresh_token` (text, nullable)
  - `status` (varchar(20)) — `"connected"`, `"revoked"`
  - `connected_at` (datetime)
  - `disconnected_at` (datetime, nullable)
  - `created_at` (datetime)
  - `updated_at` (datetime)

---

### 2.6 앱 설정/브랜딩 도메인

#### 2.6.1 app_settings (선택)
- **테이블명**: `app_settings`
- **설명**: 서비스 전역 설정(로고 URL, 서비스명 등)
- **컬럼 (요약)**
  - `id` (bigint, PK)
  - `key` (varchar(100), unique)
  - `value` (text)
  - `created_at` (datetime)
  - `updated_at` (datetime)

---

## 3. 주요 API 설계 요약

### 3.1 인증/계정 관련 API (AWS Cognito 프록시 + JWT 검증)

- **POST /api/auth/signup**
  - 회원가입 요청을 **백엔드가 Cognito SignUp API로 프록시**
  - Body: `name`, `age`, `gender`, `email`, `password`, `passwordConfirm`
  - 내부 동작 (예시)
    - Cognito User Pool에 사용자 생성 요청
    - 최초 가입 시 `users` 테이블에 `email`, `cognito_sub` 등을 동기화
  - 응답: 가입 상태 및 안내 메시지 (이메일 인증 여부 등)

- **POST /api/auth/login**
  - 이메일/비밀번호 로그인 요청을 **백엔드가 Cognito InitiateAuth(API)를 호출하여 프록시**
  - Body: `email`, `password`
  - 응답: Cognito에서 발급한 `accessToken`, `idToken`(필요 시), `refreshToken` 등을 래핑한 응답

- **POST /api/auth/logout** (선택)
  - 클라이언트가 보유한 JWT/리프레시 토큰을 무효화하는 요청을 **Cognito Global SignOut 등으로 프록시**
  - 또는 단순히 클라이언트 측 토큰 삭제 트리거 용도로 사용

- **GET /api/auth/me**
  - `Authorization: Bearer <JWT>` 헤더로 전달된 **Cognito 액세스 토큰/ID 토큰을 Django에서 검증**
  - 토큰의 `sub`를 `users.cognito_sub`와 매핑하여 현재 로그인 유저 정보 조회
  - 시작 페이지, 홈, 마이페이지 등에서 로그인 상태 체크용

---

### 3.2 성향 분석 결과/마이페이지 관련 API

- **GET /api/analysis-results/{id}**
  - 특정 분석 결과 상세 조회
  - 응답: 캐릭터 이미지/이름, 요약, 성향, 취향, 코칭 텍스트 등

- **GET /api/users/{userId}/analysis-results**
  - 유저별 분석 결과 목록 조회 (마이페이지/히스토리 페이지용)

- **POST /api/analysis-results**
  - 내부 용도: 분석 로직이 결과를 생성해 `analysis_results`에 저장할 때 사용

- **GET /api/mypage**
  - 마이페이지 진입 시, 유저 기본 정보 + 최근 분석 결과 일부 반환

- **POST /api/analysis/start** (선택)
  - "새 성향분석 시작" 버튼 클릭 시 분석 세션 생성 후 검사 페이지로 리다이렉트할 때 사용 가능

---

### 3.3 심리 검사(psy_test) 관련 API

- **GET /api/psy-test/questions**
  - 심리 검사 문항 50개 조회

- **POST /api/psy-test/submit**
  - 50문항 응답 제출
  - Body: `sessionId`(선택), `answers[]: {questionId, value}`
  - 응답: `analysisResultId`, `redirectPath`(`/analysis-result?resultId=...`)

---

### 3.4 셀프 체크(self_check) 관련 API

- **GET /api/self-check**
  - 유저 기본 정보(`users`) + 최근 셀프 체크 값(`self_check_entries`) 조회
  - 폼 초기값에 사용

- **POST /api/self-check/submit**
  - 셀프 체크 폼 제출 및 저장
  - (파일 업로드 API는 별도 엔드포인트로 가정)

- **(예시) POST /api/upload/audio, POST /api/upload/document**
  - 파일 업로드 후, 경로를 `self_check_entries`에 저장

---

### 3.5 퀘스트 관련 API

- **GET /api/home**
  - 홈 화면 요약 데이터
  - 응답: `user`, `character`, `dailyQuests[]`, `weeklyQuest`

- **GET /api/quests**
  - 오늘의 일일 퀘스트 + 이번 주 주간 퀘스트 목록 조회
  - 응답: `{ daily: [...], weekly: [...] }`

- **PATCH /api/quests/{userQuestId}**
  - 개별 퀘스트 상태 변경 (`status`: `pending`, `completed`, `deleted` 등)

- **PATCH /api/quests/bulk-status** (선택)
  - 여러 `userQuestIds`에 대해 상태 일괄 변경

- **GET /api/quest-history**
  - 쿼리 `date=YYYY-MM-DD`
  - 해당 날짜의 일간/주간 퀘스트 수행 기록 조회

- **GET /api/quest-history/summary**
  - 쿼리 `year`, `month`
  - 캘린더용 요약(날짜별 퀘스트 유무, 완료 개수 등)

---

### 3.6 SNS 연동(import_sns) 관련 API

- **GET /api/sns/channels**
  - 지원 SNS 채널 목록 조회 (`sns_channels` 기반)

- **GET /api/me/sns-accounts**
  - 현재 유저의 SNS 연동 현황 (`user_sns_accounts` 기반)

- **POST /api/sns/import**
  - 특정 채널에 대해 가져오기/연동 트리거
  - 응답: OAuth URL 또는 동기화 시작 상태

---

### 3.7 앱 설정/브랜딩(start_page) 관련 API

- **GET /api/app-settings/public** (선택)
  - 시작/공개 페이지에 필요한 로고 URL, 서비스명 등 반환

---

## 4. 페이지별 DB/API 의존 관계 요약

- **시작 페이지(start_page.md)**
  - DB: 선택적으로 `app_settings`
  - API: `GET /api/app-settings/public`, `GET /api/auth/me`

- **로그인(login.md)**
  - DB: `users`, (선택) `auth_tokens`
  - API: `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`

- **회원가입(signup.md)**
  - DB: `users`
  - API: `POST /api/auth/signup`

- **홈(home.md)**
  - DB: `users`, `analysis_results`, `quest_templates`, `user_quests`
  - API: `GET /api/home`

- **마이페이지(mypage.md)**
  - DB: `users`, `analysis_results`
  - API: `GET /api/mypage`, `GET /api/users/{userId}/analysis-results`, (선택) `POST /api/analysis/start`

- **성향 분석 결과(analysis_result.md)**
  - DB: `analysis_results`
  - API: `GET /api/analysis-results/{id}`

- **성격 검사(psy_test.md)**
  - DB: `psy_questions`, `psy_test_sessions`, `psy_answers`, `analysis_results`
  - API: `GET /api/psy-test/questions`, `POST /api/psy-test/submit`

- **성향 분석 셀프 체크(self_check.md)**
  - DB: `users`, `self_check_entries`
  - API: `GET /api/self-check`, `POST /api/self-check/submit`, (파일 업로드 관련 API)

- **퀘스트 페이지(quest_page.md)**
  - DB: `quest_templates`, `user_quests`
  - API: `GET /api/quests`, `PATCH /api/quests/{userQuestId}`, `PATCH /api/quests/bulk-status`

- **퀘스트 히스토리(quest_history.md)**
  - DB: `quest_templates`, `user_quests`
  - API: `GET /api/quest-history`, `GET /api/quest-history/summary`

- **SNS 가져오기(import_sns.md)**
  - DB: `users`, `sns_channels`, `user_sns_accounts`
  - API: `GET /api/sns/channels`, `GET /api/me/sns-accounts`, `POST /api/sns/import`

- **공통 하단 바(common.md)**
  - DB: 없음 (전부 라우팅/네비게이션)
  - API: 간접적으로 각 페이지 API들과 연결

---

## 5. 구현 시 참고 메모

- 실제 구현 시에는 사용하는 프레임워크(NestJS, Spring, Django 등)에 맞춰
  - 엔티티/모델 정의
  - 마이그레이션(SQL)
  - 컨트롤러/서비스/리포지토리
  를 작성하면 됨.
- 보안/인증(JWT, 세션, OAuth) 및 파일 업로드(S3, 로컬 스토리지 등) 정책은
  - 인프라 환경에 따라 추가 설계 필요.

이 문서는 각 페이지별 설계 문서의 **공통 구조를 한 눈에 보는 용도**이므로,
세부 비즈니스 로직 변경 시 이 문서를 함께 업데이트해 주면 전체 아키텍처 파악에 도움이 됩니다.

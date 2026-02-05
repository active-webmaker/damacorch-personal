# 분석 결과(URL에 쿼리로 아이디 전달해서 결과 페이지를 받아옴)
## 페이지에 필요한 UI 요소 목록
뒤로가기 버튼(마이페이지)
캐릭터 이미지 섹션
캐릭터 이름 섹션
요약 섹션
성향(성격, 행동패턴) 섹션
취향(좋아하는 것, 싫어하는 것) 섹션
행동코칭 섹션
마이페이지로 이동 버튼

---
 
## DB 설계
 
### 1. 기본 개념
- **URL 쿼리로 분석 결과 ID(resultId)를 받아서 해당 결과를 조회하는 페이지**
- 한 유저는 여러 번의 분석 결과를 가질 수 있음
- 분석 결과의 핵심 정보(캐릭터, 요약, 성향/취향/코칭)는 하나의 메인 테이블에 모음
 
### 2. 주요 테이블
 
#### 2-1. users (요약)
- 이미 존재한다고 가정(또는 따로 정의)
- **컬럼 예시**
  - `id` (PK, bigint)
  - `email` (unique)
  - `name`
  - `created_at`
  - `updated_at`
 
#### 2-2. analysis_results (분석 결과 메인 테이블)
- **테이블명**: `analysis_results`
- **컬럼**
  - `id` (bigint, PK, auto increment)
    - 분석 결과 고유 ID (URL 쿼리 `resultId`로 사용)
  - `user_id` (bigint, FK → users.id)
    - 이 분석 결과가 속한 유저
  - `character_name` (varchar(100))
    - 캐릭터 이름 섹션
  - `character_image_url` (varchar(255))
    - 캐릭터 이미지 섹션에 사용할 이미지 URL
  - `summary` (text)
    - 요약 섹션 내용
  - `tendency_personality` (text)
    - 성향(성격) 설명
  - `tendency_behavior_pattern` (text)
    - 성향(행동패턴) 설명
  - `preference_likes` (text)
    - 취향 - 좋아하는 것
  - `preference_dislikes` (text)
    - 취향 - 싫어하는 것
  - `coaching_tips` (text)
    - 행동코칭 섹션에 들어갈 코칭 문구들(줄바꿈으로 구분 가능)
  - `source_type` (varchar(50), 선택)
    - 어떤 테스트/퀘스트에서 나온 결과인지 구분 (예: `"quest"`, `"survey"` 등)
  - `source_id` (bigint, 선택)
    - 원본 퀘스트/테스트 결과 ID 등
  - `created_at` (datetime)
  - `updated_at` (datetime)
 
---
 
## API 설계
 
### 1. URL 구조
- 분석 결과 페이지 예시
  - `/analysis-result?resultId={id}`
  - 또는 `/analysis-result/{id}` (라우터에서 path param으로 처리)
 
백엔드는 아래 API를 제공한다고 가정.
 
### 2. 단일 분석 결과 조회
 
#### 1) GET /api/analysis-results/{id}
- **설명**: 특정 분석 결과 ID로 상세 데이터를 조회 (결과 페이지 진입 시 호출)
- **Path 파라미터**
  - `id` (필수): `analysis_results.id`
- **응답 예시**
  - (형태 예시)
  ```json
  {
    "id": 123,
    "userId": 45,
    "characterName": "도시형 탐험가",
    "characterImageUrl": "https://.../characters/explorer.png",
    "summary": "당신은 사람들과 함께할 때 에너지를 얻지만...",
    "tendency": {
      "personality": "타인의 시선을 의식하지만...",
      "behaviorPattern": "압박을 받으면 일을 미루는 경향이 있습니다..."
    },
    "preference": {
      "likes": "새로운 사람 만나기, 짧은 프로젝트, 명확한 목표",
      "dislikes": "불분명한 지시, 장기적인 불확실성"
    },
    "coaching": {
      "tips": "매일 아침 오늘 가장 중요한 한 가지를 정해보세요.\n회의 전에 미리 의견을 정리해두세요."
    },
    "createdAt": "2026-02-05T12:34:56Z"
  }
  ```
 
### 3. 유저별 분석 결과 목록 조회 (마이페이지용)
 
#### 2) GET /api/users/{userId}/analysis-results
- **설명**: 해당 유저의 분석 결과 목록(최근 N개 등) 조회
- **Path 파라미터**
  - `userId`: 유저 ID
- **Query 파라미터(선택)**
  - `limit`: 최대 개수 (기본 20 등)
  - `offset`: 페이징
- **응답 예시**
  ```json
  [
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
  ```
 
### 4. 분석 결과 생성 (선택, 백엔드/AI 로직 용)
 
#### 3) POST /api/analysis-results
- **설명**: 새 분석 결과를 생성 (설문/퀘스트 완료 후 내부적으로 호출)
- **요청 Body 예시**
  ```json
  {
    "userId": 45,
    "characterName": "도시형 탐험가",
    "characterImageUrl": "https://.../characters/explorer.png",
    "summary": "당신은 사람들과 함께할 때 에너지를 얻지만...",
    "tendencyPersonality": "타인의 시선을 의식하지만...",
    "tendencyBehaviorPattern": "압박을 받으면 일을 미루는 경향...",
    "preferenceLikes": "새로운 사람 만나기...",
    "preferenceDislikes": "불분명한 지시...",
    "coachingTips": "매일 아침 오늘 가장 중요한 한 가지를 정해보세요.\n..."
  }
  ```
- **응답 예시**
  ```json
  {
    "id": 123,
    "createdAt": "2026-02-05T12:34:56Z"
  }
  ```
 
---
 
## 화면 요소 ↔ DB/API 매핑 메모
- 뒤로가기 버튼(마이페이지)
  - 프론트 라우팅(`/mypage` 등), 필요 시 userId 사용
- 캐릭터 이미지 섹션
  - DB: `analysis_results.character_image_url`
  - API: `characterImageUrl`
- 캐릭터 이름 섹션
  - DB: `analysis_results.character_name`
  - API: `characterName`
- 요약 섹션
  - DB: `analysis_results.summary`
  - API: `summary`
- 성향(성격, 행동패턴) 섹션
  - DB: `tendency_personality`, `tendency_behavior_pattern`
  - API: `tendency.personality`, `tendency.behaviorPattern`
- 취향(좋아하는 것, 싫어하는 것) 섹션
  - DB: `preference_likes`, `preference_dislikes`
  - API: `preference.likes`, `preference.dislikes`
- 행동코칭 섹션
  - DB: `coaching_tips`
  - API: `coaching.tips`
- 마이페이지로 이동 버튼
  - 프론트 라우팅(`/mypage`), 필요 시 `GET /api/users/{userId}/analysis-results`로 히스토리 조회
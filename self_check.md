# 성향 분석 셀프 체크
## 페이지에 필요한 UI 요소 목록
뒤로가기 버튼
이름, 나이, 성별 폼(회원 가입 시 입력한 정보를 DB에서 자동으로 불러옴)
취미 폼
수면 패턴(시간) 폼
운동여부(O,X) 폼
1주 운동 횟수 폼
운동종류(유산소, 무산소, 둘다) 폼
반려동물 종류 폼
MBTI 폼
주당 외출 횟수 폼
말투 오디오 업로드 파일 폼
자신을 표현할 수 있는 문서 파일 폼
제출 버튼

---

## DB 설계

### 1. 기본 개념
- 이 페이지에서 하는 일
  - 유저가 스스로 본인의 라이프스타일/성향 정보를 입력해서 **성향 분석의 추가 데이터**로 활용
- 필요한 데이터
  - 유저 기본 프로필(이름, 나이, 성별) — 회원가입 시 입력한 내용 재사용
  - 셀프 체크에서 입력하는 추가 정보들(취미, 수면 패턴, 운동, 반려동물, MBTI 등)
  - 업로드 파일(오디오, 문서)의 저장 경로

### 2. 주요 테이블

#### 2-1. users (기본 프로필 재사용)
- **테이블명**: `users`
- 이미 로그인/회원가입/마이페이지에서 사용하는 공통 테이블
- 이 페이지에서 사용하는 컬럼 예시
  - `id` (bigint, PK)
  - `name` (varchar)
  - `age` (int 또는 birth_year 등, 실제 설계에 맞게)
  - `gender` (varchar)

#### 2-2. self_check_entries (셀프 체크 입력 값)
- **테이블명**: `self_check_entries`
- 한 번의 셀프 체크 제출마다 한 레코드 저장 (혹은 마지막 것만 사용해도 됨)
- **컬럼 예시**
  - `id` (bigint, PK)
  - `user_id` (bigint, FK → users.id)
  - `hobby` (text)
  - `sleep_pattern` (varchar(50))
    - 예: "평일 7시간, 주말 9시간" 혹은 시간대
  - `exercise_flag` (boolean)
    - 운동 여부(O,X)
  - `exercise_per_week` (int)
    - 1주 운동 횟수
  - `exercise_type` (varchar(20))
    - 예: `"aerobic"`(유산소), `"anaerobic"`(무산소), `"both"`(둘다)
  - `pet_type` (varchar(100))
    - 반려동물 종류 (없으면 null)
  - `mbti` (varchar(4))
    - 예: "INTJ", "ENFP" 등
  - `outing_per_week` (int)
    - 주당 외출 횟수
  - `speech_audio_path` (varchar(255), nullable)
    - 말투 오디오 업로드 파일 저장 경로
  - `self_intro_doc_path` (varchar(255), nullable)
    - 자신을 표현할 수 있는 문서 파일 저장 경로
  - `created_at` (datetime)

※ 실제 파일은 스토리지(S3 등)에 저장하고, DB에는 경로/키만 저장하는 구조를 가정.

---

## API 설계

### 1. 셀프 체크 초기 데이터 조회 (폼 초기값)

#### 1) GET /api/self-check
- **설명**
  - 성향 분석 셀프 체크 페이지 진입 시, 유저 기본 정보와 최근 셀프 체크 값을 가져와 폼 초기값으로 사용
- **응답 예시**
  ```json
  {
    "user": {
      "id": 45,
      "name": "홍길동",
      "age": 29,
      "gender": "male"
    },
    "lastSelfCheck": {
      "hobby": "등산, 독서",
      "sleepPattern": "평일 6시간, 주말 8시간",
      "exerciseFlag": true,
      "exercisePerWeek": 3,
      "exerciseType": "both",
      "petType": "고양이",
      "mbti": "INFJ",
      "outingPerWeek": 2,
      "speechAudioUrl": "https://.../audio/123.mp3",
      "selfIntroDocUrl": "https://.../docs/456.pdf"
    }
  }
  ```

### 2. 셀프 체크 제출

#### 2) POST /api/self-check/submit
- **설명**
  - 폼에 입력된 셀프 체크 데이터를 제출하고 저장
  - 파일 업로드는 일반적으로 별도 엔드포인트에서 처리하거나, multipart로 함께 전송
- **요청 예시 (JSON + 파일 업로드 분리 가정)**
  1) 파일 업로드 API (예시)
  ```json
  // POST /api/upload/audio
  // POST /api/upload/document
  // 응답으로 파일 URL 또는 경로를 받는다.
  ```
  2) 셀프 체크 제출
  ```json
  {
    "hobby": "등산, 독서",
    "sleepPattern": "평일 6시간, 주말 8시간",
    "exerciseFlag": true,
    "exercisePerWeek": 3,
    "exerciseType": "both",
    "petType": "고양이",
    "mbti": "INFJ",
    "outingPerWeek": 2,
    "speechAudioPath": "/files/audio/123.mp3",
    "selfIntroDocPath": "/files/docs/456.pdf"
  }
  ```
- **응답 예시**
  ```json
  {
    "selfCheckId": 789,
    "message": "셀프 체크 정보가 저장되었습니다."
  }
  ```

---

## 화면 요소 ↔ DB/API 매핑 메모
- 뒤로가기 버튼
  - 프론트 라우팅(`/mypage` 등), DB 직접 연관 없음
- 이름, 나이, 성별 폼(회원 가입 시 입력한 정보를 DB에서 자동으로 불러옴)
  - DB: `users.name`, `users.age`, `users.gender`
  - API: `GET /api/self-check` 응답의 `user` 사용
- 취미 폼
  - DB: `self_check_entries.hobby`
  - API: `GET /api/self-check` (`lastSelfCheck.hobby`), `POST /api/self-check/submit`
- 수면 패턴(시간) 폼
  - DB: `self_check_entries.sleep_pattern`
  - API: 동일
- 운동여부(O,X) 폼
  - DB: `self_check_entries.exercise_flag`
  - API: 동일
- 1주 운동 횟수 폼
  - DB: `self_check_entries.exercise_per_week`
  - API: 동일
- 운동종류(유산소, 무산소, 둘다) 폼
  - DB: `self_check_entries.exercise_type`
  - API: 동일
- 반려동물 종류 폼
  - DB: `self_check_entries.pet_type`
  - API: 동일
- MBTI 폼
  - DB: `self_check_entries.mbti`
  - API: 동일
- 주당 외출 횟수 폼
  - DB: `self_check_entries.outing_per_week`
  - API: 동일
- 말투 오디오 업로드 파일 폼
  - DB: `self_check_entries.speech_audio_path`
  - API: 업로드 API + `POST /api/self-check/submit`
- 자신을 표현할 수 있는 문서 파일 폼
  - DB: `self_check_entries.self_intro_doc_path`
  - API: 업로드 API + `POST /api/self-check/submit`
- 제출 버튼
  - API: `POST /api/self-check/submit` 호출 후, 필요 시 다음 단계(예: 분석 진행 페이지)로 이동
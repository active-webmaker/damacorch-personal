# 로그인
## 페이지에 필요한 UI 요소 목록
뒤로가기 버튼
이메일 폼
비밀번호 폼
폼 서브밋(로그인)

---

## DB 설계

### 1. 기본 개념
- 이 페이지에서 하는 일
  - 사용자가 이메일/비밀번호로 로그인해서 **인증 토큰(세션)**을 발급받는 진입점
- 필요한 데이터
  - 유저 계정 정보 (이메일, 비밀번호 해시 등)
  - 로그인 상태를 표현하기 위한 세션/토큰 정보

### 2. 주요 테이블

#### 2-1. users (유저 계정 정보)
- **테이블명**: `users`
- 서비스 전반에서 공통으로 사용하는 유저 테이블
- **컬럼 예시**
  - `id` (bigint, PK)
  - `email` (varchar(255), unique)
  - `password_hash` (varchar(255))
    - 비밀번호 원문이 아닌 해시값 저장 (예: bcrypt)
  - `name` (varchar(100), nullable)
  - `created_at` (datetime)
  - `updated_at` (datetime)
  - `last_login_at` (datetime, nullable)

#### 2-2. auth_tokens (선택: 세션/토큰 관리)
- **테이블명**: `auth_tokens`
- 서버에서 발급한 액세스 토큰/리프레시 토큰 등을 관리하고 싶을 때 사용 (세션 기반이면 생략 가능)
- **컬럼 예시**
  - `id` (bigint, PK)
  - `user_id` (bigint, FK → users.id)
  - `token` (varchar(255))
    - 액세스 토큰 또는 리프레시 토큰 값 (실제 구현에 따라 길이/형식 조정)
  - `type` (varchar(20))
    - 예: `"access"`, `"refresh"`
  - `expires_at` (datetime)
  - `created_at` (datetime)
  - `revoked_at` (datetime, nullable)

※ 실제 인증 방식(JWT, 세션, OAuth 등)에 따라 이 테이블은 단순 참고용이며, 인프라 설계와 함께 구체화 필요.

---

## API 설계

### 1. 로그인 API

#### 1) POST /api/auth/login
- **설명**
  - 이메일/비밀번호로 로그인 시도
  - 성공 시 토큰 또는 세션 ID를 반환
- **요청 Body 예시**
  ```json
  {
    "email": "user@example.com",
    "password": "plain-password"
  }
  ```
- **응답 예시 (JWT 기반 가정)**
  ```json
  {
    "user": {
      "id": 45,
      "email": "user@example.com",
      "name": "홍길동"
    },
    "accessToken": "jwt-access-token-string",
    "refreshToken": "jwt-refresh-token-string"
  }
  ```
- **검증 로직 메모**
  - `users` 테이블에서 `email`로 조회
  - 입력 받은 `password`를 해시해 `password_hash`와 비교
  - 성공 시
    - 필요하다면 `auth_tokens`에 토큰 레코드 생성
    - `users.last_login_at` 갱신

### 2. 로그아웃 API (선택)

#### 2) POST /api/auth/logout
- **설명**
  - 현재 로그인 상태를 해제 (토큰 무효화 또는 세션 종료)
- **요청 예시 (헤더에 토큰 포함)**
  - `Authorization: Bearer <accessToken>`
- **응답 예시**
  ```json
  {
    "success": true
  }
  ```
- **로직 메모**
  - `auth_tokens`를 사용하는 경우 해당 토큰 레코드의 `revoked_at`을 현재 시간으로 설정
  - 세션 기반이면 서버 세션 제거

### 3. 로그인 유저 정보 조회 (선택)

#### 3) GET /api/auth/me
- **설명**
  - 현재 토큰/세션 기준으로 로그인한 유저 정보 조회
- **응답 예시**
  ```json
  {
    "id": 45,
    "email": "user@example.com",
    "name": "홍길동"
  }
  ```

---

## 화면 요소 ↔ DB/API 매핑 메모
- 뒤로가기 버튼
  - 프론트 라우팅(`/start_page` 또는 이전 페이지) 처리, DB 직접 연관 없음
- 이메일 폼
  - 입력값: `email`
  - API: `POST /api/auth/login` Body에 포함
- 비밀번호 폼
  - 입력값: `password`
  - API: `POST /api/auth/login` Body에 포함
- 폼 서브밋(로그인)
  - API: `POST /api/auth/login` 호출
  - 성공 시
    - 토큰/세션 저장 후 홈 화면 등으로 이동 (`/home`)
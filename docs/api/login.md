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
  - 사용자가 이메일/비밀번호로 로그인해서 **AWS Cognito를 통해 JWT를 발급받는 진입점**
- 필요한 데이터
  - Cognito User Pool 상의 유저 계정 정보 (이메일, 비밀번호 등)
  - 백엔드/프론트에서 사용할 JWT (access token, id token 등)

### 2. 주요 테이블

#### 2-1. users (유저 계정 정보, Cognito 연동)
- **테이블명**: `users`
- 서비스 전반에서 공통으로 사용하는 유저 테이블
- **컬럼 예시**
  - `id` (bigint, PK)
  - `email` (varchar(255), unique)
  - `name` (varchar(100), nullable)
  - `cognito_sub` (varchar(64), unique)
    - Cognito User Pool의 `sub` 클레임과 매핑되는 값
  - `created_at` (datetime)
  - `updated_at` (datetime)
  - `last_login_at` (datetime, nullable)

> 비밀번호 해시 및 토큰 저장은 로컬 DB가 아닌 Cognito가 담당하고, 백엔드는 Cognito가 발급한 JWT를 검증해 `users` 레코드와 매핑합니다.

---

## API 설계

### 1. 로그인 API

#### 1) POST /api/auth/login
- **설명**
  - 이메일/비밀번호로 로그인 시도
  - 백엔드가 AWS Cognito의 **InitiateAuth(또는 관련 로그인 API)**를 호출하는 프록시 역할을 수행
  - 성공 시 Cognito에서 발급한 JWT(access token, id token, refresh token 등)를 프론트에 전달

- **요청 Body 예시**
  ```json
  {
    "email": "user@example.com",
    "password": "plain-password"
  }
  ```
- **응답 예시 (Cognito JWT 기반)**
  ```json
  {
    "user": {
      "id": 45,
      "email": "user@example.com",
      "name": "홍길동"
    },
    "accessToken": "cognito-jwt-access-token-string",
    "refreshToken": "cognito-jwt-refresh-token-string"
  }
  ```
- **검증/연동 로직 메모 (서버 측)**
  - 백엔드는 입력받은 `email`, `password`로 Cognito 로그인 API를 호출
  - Cognito에서 로그인 성공 시 JWT(accessToken 등)를 발급받아 그대로 또는 래핑하여 클라이언트에 반환
  - JWT의 `sub`를 기반으로 `users.cognito_sub` 레코드를 조회/생성하고, `last_login_at` 갱신

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
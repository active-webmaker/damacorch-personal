# 페이지에 필요한 UI 요소 목록
## 회원가입
뒤로가기 버튼
이름 폼
나이 폼
성별 폼
이메일 폼
비밀번호 폼
비밀번호 확인 폼
제출 버튼

---

## DB 설계

### 1. 기본 개념
- 이 페이지에서 하는 일
  - 유저가 이름/나이/성별/이메일/비밀번호를 입력해 **새 계정을 생성**
- 필요한 데이터
  - 유저 계정 정보 (이메일, 비밀번호 해시 등)
  - 프로필 정보 (이름, 나이, 성별)

### 2. 주요 테이블

#### 2-1. users (유저 계정 + 기본 프로필)
- **테이블명**: `users`
- 로그인/셀프체크/마이페이지 등에서 공통으로 사용하는 유저 테이블
- **컬럼 예시**
  - `id` (bigint, PK)
  - `email` (varchar(255), unique)
  - `password_hash` (varchar(255))
    - 비밀번호 원문이 아닌 해시값 저장 (예: bcrypt)
  - `name` (varchar(100))
  - `age` (int 또는 birth_year 등, 실제 설계에 맞게)
  - `gender` (varchar(20))
  - `created_at` (datetime)
  - `updated_at` (datetime)

※ 로그인 페이지의 `users` 정의와 동일한 테이블을 사용하며, 여기서 최초 생성.

---

## API 설계

### 1. 회원가입 API

#### 1) POST /api/auth/signup
- **설명**
  - 회원가입 폼을 제출해 새 유저를 생성
  - 성공 시 로그인 정보(토큰)까지 같이 반환할 수도 있고, 단순히 생성 후 로그인 페이지로 보내도 됨
- **요청 Body 예시**
  ```json
  {
    "name": "홍길동",
    "age": 29,
    "gender": "male",
    "email": "user@example.com",
    "password": "plain-password",
    "passwordConfirm": "plain-password"
  }
  ```
- **검증 로직 메모**
  - `password`와 `passwordConfirm` 일치 여부 확인 (백엔드/프론트 모두에서 검증)
  - `email` 중복 여부 확인 (`users.email` unique)
  - 비밀번호 정책 검증(길이, 복잡도 등)
  - 비밀번호 해시 생성 후 `password_hash`로 저장

- **응답 예시 (회원가입 후 자동 로그인 가정)**
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

또는, 단순 생성만 하고 로그인 페이지로 리다이렉트하는 방식이라면:
  ```json
  {
    "userId": 45,
    "message": "회원가입이 완료되었습니다. 로그인 해주세요."
  }
  ```

---

## 화면 요소 ↔ DB/API 매핑 메모
- 뒤로가기 버튼
  - 프론트 라우팅(`/login` 또는 시작 페이지) 처리, DB 직접 연관 없음
- 이름 폼
  - DB: `users.name`
  - API: `POST /api/auth/signup` Body의 `name`
- 나이 폼
  - DB: `users.age`
  - API: `POST /api/auth/signup` Body의 `age`
- 성별 폼
  - DB: `users.gender`
  - API: `POST /api/auth/signup` Body의 `gender`
- 이메일 폼
  - DB: `users.email`
  - API: `POST /api/auth/signup` Body의 `email`
- 비밀번호 폼
  - DB: `users.password_hash` (해시로 저장)
  - API: `POST /api/auth/signup` Body의 `password`
- 비밀번호 확인 폼
  - DB 컬럼은 없음 (검증용)
  - API: `POST /api/auth/signup` Body의 `passwordConfirm`
- 제출 버튼
  - API: `POST /api/auth/signup` 호출 후, 정책에 따라
    - 자동 로그인 처리 → 홈 화면으로 이동
    - 또는 로그인 페이지(`/login`)로 이동
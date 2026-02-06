# 회원가입
## 페이지에 필요한 UI 요소 목록
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
  - 유저가 이름/나이/성별/이메일/비밀번호를 입력해 **AWS Cognito User Pool에 새 계정을 생성**
- 필요한 데이터
  - Cognito User Pool 상의 계정 정보 (이메일, 비밀번호 등)
  - 로컬 DB에 저장할 프로필 정보 (이름, 나이, 성별, 이메일, Cognito `sub` 등)

### 2. 주요 테이블

#### 2-1. users (유저 계정 + 기본 프로필, Cognito 연동)
- **테이블명**: `users`
- 로그인/셀프체크/마이페이지 등에서 공통으로 사용하는 유저 테이블
- **컬럼 예시**
  - `id` (bigint, PK)
  - `email` (varchar(255), unique)
  - `name` (varchar(100))
  - `age` (int 또는 birth_year 등, 실제 설계에 맞게)
  - `gender` (varchar(20))
  - `cognito_sub` (varchar(64), unique)
    - Cognito User Pool의 `sub` 클레임과 매핑되는 값
  - `created_at` (datetime)
  - `updated_at` (datetime)

> 비밀번호 해시는 로컬 DB에 저장하지 않고 Cognito가 관리하며, 이 페이지에서는 Cognito에 회원가입을 요청한 뒤 성공 시 `users`에 최소한의 프로필 정보와 `cognito_sub`를 동기화합니다.

---

## API 설계

### 1. 회원가입 API

#### 1) POST /api/auth/signup
- **설명**
  - 회원가입 폼을 제출하면 백엔드가 AWS Cognito의 **SignUp API**를 호출하는 프록시 역할을 수행
  - Cognito에서 계정 생성이 성공하면, 해당 유저의 `email`, `cognito_sub` 등 최소한의 정보로 로컬 `users` 레코드를 생성/업데이트
  - 성공 시 로그인 정보(토큰)를 바로 반환하거나, 단순히 생성 후 로그인 페이지로 보내는 방식 선택 가능

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
- **검증/연동 로직 메모**
  - `password`와 `passwordConfirm` 일치 여부 확인 (백엔드/프론트 모두에서 검증)
  - Cognito가 요구하는 비밀번호 정책(길이, 복잡도 등)에 맞는지 검증
  - Cognito SignUp 호출 시 `email` 중복 여부, 비밀번호 정책 위반 여부 등은 Cognito에서 최종 검증
  - Cognito 응답의 `sub`를 활용해 로컬 `users.cognito_sub`를 저장/연동

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
  - Cognito에서 관리
  - API: `POST /api/auth/signup` Body의 `password` (백엔드 → Cognito로 전달)
- 비밀번호 확인 폼
  - DB 컬럼은 없음 (검증용)
  - API: `POST /api/auth/signup` Body의 `passwordConfirm`
- 제출 버튼
  - API: `POST /api/auth/signup` 호출 후, 정책에 따라
    - 자동 로그인 처리 → 홈 화면으로 이동
    - 또는 로그인 페이지(`/login`)로 이동
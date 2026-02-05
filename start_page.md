# 페이지에 필요한 UI 요소 목록
## 시작 페이지
서비스 로고 URL
로그인 버튼(로그인 페이지로 이동)
회원가입 버튼(회원가입 페이지로 이동)

---

## DB 설계

### 1. 기본 개념
- 시작 페이지는 주로 **라우팅과 브랜딩(로고)** 역할이므로, 복잡한 DB는 필요 없음
- 필요한 경우에만 서비스 로고/브랜딩 정보를 설정 테이블로 관리

### 2. 주요 테이블 (선택)

#### 2-1. app_settings (서비스 설정)
- **테이블명**: `app_settings`
- 서비스 전역 설정 값을 key-value 형태로 저장할 때 사용 (선택사항)
- **컬럼 예시**
  - `id` (bigint, PK)
  - `key` (varchar(100), unique)
    - 예: `"service_logo_url"`, `"service_name"`
  - `value` (text)
  - `created_at` (datetime)
  - `updated_at` (datetime)

시작 페이지에서는 `service_logo_url` 값만 사용해도 충분하며, 없다면 프론트에 하드코딩된 기본 로고를 사용해도 됨.

---

## API 설계

### 1. 서비스 로고/브랜딩 정보 조회 (선택)

#### 1) GET /api/app-settings/public
- **설명**
  - 시작 페이지/공개 페이지에서 필요한 공용 설정 정보 조회
- **응답 예시**
  ```json
  {
    "serviceLogoUrl": "https://.../logo.png",
    "serviceName": "성향 분석 서비스"
  }
  ```

### 2. 로그인 상태 확인 (다른 페이지와 연계)

#### 2) GET /api/auth/me
- **설명**
  - 현재 로그인 상태인지 확인
  - 시작 페이지에서 이미 로그인된 유저라면 자동으로 홈(`/home`)으로 보내는 등의 로직에 활용 가능
- **응답 예시 (로그인 상태)**
  ```json
  {
    "id": 45,
    "email": "user@example.com",
    "name": "홍길동"
  }
  ```
- 로그인 안 된 상태라면 401 응답 또는 `null` 응답 형태로 처리 (인증 전략에 따라 결정)

---

## 화면 요소 ↔ DB/API 매핑 메모
- 서비스 로고 URL
  - DB(선택): `app_settings` 테이블의 `service_logo_url` 값
  - API(선택): `GET /api/app-settings/public` 응답의 `serviceLogoUrl`
  - 간단히 하려면 프론트 코드에 상수로 두어도 무방
- 로그인 버튼
  - 프론트 라우팅: `/login` 페이지로 이동
  - 필요 시: 페이지 로딩 시 `GET /api/auth/me` 호출하여 이미 로그인 상태면 버튼 대신 "마이페이지로 이동" 등으로 변경 가능
- 회원가입 버튼
  - 프론트 라우팅: `/signup` 페이지로 이동
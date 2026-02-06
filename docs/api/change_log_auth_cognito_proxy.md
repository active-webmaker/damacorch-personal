# Auth & OpenAPI 변경 내역 (Cognito 프록시 연동)

## 1. 수정된 파일 목록

- `system_api_overview.md`
- `openapi.yaml`
- `docs/api/login.md`
- `docs/api/signup.md`
- `docs/api/home.md`
- `docs/api/quest_history.md`

## 2. system_api_overview.md 변경 요약

- **유저 & 인증 도메인 (`users` 테이블)**
  - `password_hash` 및 로컬 토큰 관리 개념을 제거하고, AWS Cognito가 비밀번호/토큰을 관리한다는 점을 명시.
  - `cognito_sub` 컬럼을 추가하여 Cognito User Pool의 `sub` 클레임과 매핑하도록 설계.
  - 설명을 "인증은 Cognito, Django는 JWT 검증 및 사용자 식별" 구조로 정리.

- **인증/계정 관련 API 섹션**
  - `/api/auth/signup`을 Cognito SignUp API에 대한 프록시 엔드포인트로 정의.
  - `/api/auth/login`을 Cognito InitiateAuth(API)에 대한 프록시 엔드포인트로 정의.
  - `/api/auth/logout`을 Cognito Global SignOut 등으로의 프록시(또는 클라이언트 토큰 삭제 트리거)로 설명.
  - `/api/auth/me`는 Authorization 헤더의 JWT를 검증하고, `users.cognito_sub`와 매핑하여 현재 사용자 정보를 조회한다고 명시.

## 3. openapi.yaml 변경 요약

- **전역 설명 및 보안 스키마 추가**
  - `info.description`에 "인증은 AWS Cognito에서 JWT를 발급/관리하고, 백엔드는 Cognito API를 프록시하거나 JWT를 검증한다"는 내용을 추가.
  - `components.securitySchemes.bearerAuth`를 추가하여 JWT Bearer(Authorization: Bearer <token>) 스키마를 정의.
  - 루트 레벨에 `security: - bearerAuth: []`를 추가하여 기본적으로 모든 엔드포인트가 JWT 인증을 요구하도록 설정.

- **공개 엔드포인트 정의**
  - `/api/auth/signup`, `/api/auth/login`, `/api/app-settings/public`에 `security: []`를 명시하여 인증 없이 호출 가능한 공개 엔드포인트로 정의.

- **Auth 엔드포인트 설명 보정**
  - `/api/auth/signup`의 summary를 "회원가입 (Cognito SignUp 프록시)"로 변경하고, 200 응답 설명에 Cognito User Pool 사용자 생성 및 필요 시 로컬 `users` 동기화를 언급.
  - `/api/auth/login`의 summary를 "이메일/비밀번호 로그인 (Cognito InitiateAuth 프록시)"로 변경하고, 200 응답 설명을 "Cognito에서 발급한 토큰을 반환"으로 수정.

## 4. docs/api/* 변경 요약

- **docs/api/login.md**
  - 로그인 페이지가 "로컬 password_hash 비교 및 auth_tokens 관리"가 아니라, **백엔드가 Cognito 로그인 API를 프록시하고 Cognito JWT를 반환**하는 구조임을 명시.
  - `users` 테이블 정의에서 `password_hash`를 제거하고, `cognito_sub` 컬럼을 추가.
  - 검증 로직 메모를 "email/password → Cognito 호출 → JWT 수신 → `cognito_sub`로 로컬 유저 매핑" 흐름으로 수정.

- **docs/api/signup.md**
  - 회원가입 API가 로컬 비밀번호 해시 저장이 아니라, **Cognito SignUp API 프록시**임을 명시.
  - `users` 테이블 정의에서 `password_hash` 제거, `cognito_sub` 추가.
  - 검증/연동 메모를 Cognito의 비밀번호 정책 및 `sub` 기반 동기화 흐름으로 보정.

- **docs/api/home.md**
  - `GET /api/home`의 인증 설명을 "세션/토큰"에서 **Cognito JWT(Authorization 헤더)**를 검증하여 `userId`/`cognito_sub`를 식별하는 구조로 수정.

- **docs/api/quest_history.md**
  - 인증 설명에서 `userId`가 "토큰/세션"이 아니라 **Cognito JWT에서 추출되는 값**이라는 점을 명시.

이 문서는 AWS Cognito + Django(JWT 검증) 구조로 전환하기 위해 수행된 문서/스펙 변경 내역을 기록하기 위한 용도입니다.

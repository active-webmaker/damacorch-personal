# Django WAS PoC 계획

본 문서는 `openapi.yaml`, `system_api_overview.md`, `docs/api/*`를 기반으로
Django 기반 WAS(Web Application Server)의 PoC(Proof of Concept) 구현 계획을 정리한 것이다.

- 백엔드 프레임워크: Django (DRF 포함 가정)
- 인증: AWS Cognito + JWT (백엔드 프록시 + JWT 검증)
- DB: PostgreSQL
- 실행 환경: Docker (WAS 컨테이너와 DB 컨테이너 분리, docker-compose 사용 가정)

---

## 1. 전체 아키텍처 개요

### 1.1 컨테이너 구성

- **app (django-was)**
  - Django + Django REST Framework
  - `openapi.yaml` 기반으로 API 엔드포인트 구현
  - AWS Cognito 연동 및 JWT 검증 담당
  - PostgreSQL에 접속해 도메인 모델(`users`, `analysis_results`, `self_check_entries`, `user_quests` 등) 관리

- **db (postgres)**
  - PostgreSQL 14.x (또는 프로젝트 기본 버전)
  - 볼륨 마운트로 데이터 영속화 (`postgres-data` 등)
  - 네트워크 상에서 `app` 컨테이너에서만 접근

- (선택) **nginx**
  - PoC 단계에서는 생략 가능하나, 추후 리버스 프록시/정적 파일 서빙을 위해 추가 고려

### 1.2 네트워크/포트

- 내부 Docker 네트워크: `damacorch-net` (가칭)
- `app` 컨테이너: 내부 포트 8000 (호스트 8000 또는 8080으로 맵핑)
- `db` 컨테이너: 내부 포트 5432 (호스트 포트는 개발 시에만 노출하거나, 기본적으로는 내부 전용으로 사용)

---

## 2. Django 프로젝트 구조 (PoC 범위)

### 2.1 앱 구조(예시)

- `config/` – Django 설정, WSGI/ASGI 진입점
- `core/` – 공통 유틸, 인증 헬퍼(Cognito JWT 검증 등)
- `accounts/` – `users` 모델, `/api/auth/*`, `/api/auth/me` 구현
- `analysis/` – `analysis_results`, 심리검사/분석 관련 API
- `selfcheck/` – `self_check_entries`, `/api/self-check*`
- `quests/` – `quest_templates`, `user_quests`, `/api/home`, `/api/quests*`, `/api/quest-history*`
- `sns_integration/` – `sns_channels`, `user_sns_accounts`, `/api/sns*`
- `app_settings/` – `app_settings`, `/api/app-settings/public`

PoC에서는 **모든 기능을 완성**하기보다, 각 도메인에서 대표 API를 1~2개씩 구현하는 것을 목표로 한다.

### 2.2 settings.py 핵심 설정 (개념)

- 데이터베이스: PostgreSQL
  - `ENGINE: django.db.backends.postgresql`
  - `NAME`, `USER`, `PASSWORD`, `HOST=db`, `PORT=5432`
- REST Framework (가정)
  - 기본 인증 클래스로 **커스텀 Cognito JWT 인증 클래스** 추가
  - 기본 권한: `IsAuthenticated` (공개 API는 뷰 단에서 `AllowAny` 적용)

---

## 3. DB 스키마 매핑 (PostgreSQL)

### 3.1 공통: users

`system_api_overview.md` 기준, Cognito 연동을 반영한 `users` 모델:

- `id` (bigserial, PK)
- `email` (varchar(255), unique)
- `name` (varchar(100))
- `age` (int, nullable)
- `gender` (varchar(20), nullable)
- `cognito_sub` (varchar(64), unique)
- `created_at` (timestamptz)
- `updated_at` (timestamptz)
- `last_login_at` (timestamptz, nullable)

Django에서는 **커스텀 User 모델** 또는 별도 Profile 모델 중 하나를 선택할 수 있으나,
PoC에서는 `AbstractBaseUser` 대신 **프로젝트 내부 전용 `User` 모델**로 시작해도 된다.
(단, 장기적으로는 Django auth와의 통합 여부를 재검토)

### 3.2 주요 도메인 테이블 (요약)

`system_api_overview.md`의 ERD를 그대로 PostgreSQL 모델로 매핑:

- **analysis_results**
  - 성향 분석 결과 저장 (`character_name`, `character_image_url`, `summary`, `tendency_*`, `preference_*`, `coaching_tips` 등)
- **psy_questions / psy_test_sessions / psy_answers**
  - 성격 검사 문항, 세션, 응답
- **self_check_entries**
  - 성향 분석 셀프 체크 입력 값
- **quest_templates / user_quests**
  - 퀘스트 마스터 및 유저별 퀘스트 인스턴스
- **sns_channels / user_sns_accounts**
  - SNS 채널 마스터 및 유저별 연동 정보
- **app_settings** (선택)
  - 서비스 로고/이름 등 공개 설정

PoC 단계에서는 **마이그레이션 스크립트**만 정의하고, 상세 인덱스/제약 조건은 최소한으로 유지한다.

---

## 4. 인증 및 AWS Cognito 연동 전략

### 4.1 기본 개념

- 로그인/회원가입은 Django가 직접 비밀번호를 검증/저장하지 않고,
  **AWS Cognito User Pool**에 대한 프록시 API로 동작.
- Django는 `Authorization: Bearer <JWT>` 헤더로 전달된 Cognito JWT를 검증하고,
  `sub` 클레임 기준으로 `users.cognito_sub`와 매핑해 현재 유저를 식별한다.

### 4.2 Auth 관련 엔드포인트

`openapi.yaml` 및 `system_api_overview.md` 기준:

- `POST /api/auth/signup`
  - 역할: Cognito SignUp API 프록시
  - 플로우:
    1. Django가 Cognito SignUp 호출 (email, password 등)
    2. 성공 시 응답의 `sub`를 사용해 `users` 테이블에 레코드 생성/업데이트
    3. 선택: 자동 로그인(토큰 반환) 또는 로그인 페이지로 유도

- `POST /api/auth/login`
  - 역할: Cognito InitiateAuth API 프록시
  - 플로우:
    1. Django가 Cognito 로그인 호출
    2. Cognito에서 받은 `accessToken`, `idToken`, `refreshToken`을 프론트에 반환
    3. `idToken`/`accessToken`의 `sub`로 `users` 레코드 생성/동기화 및 `last_login_at` 갱신

- `POST /api/auth/logout` (선택)
  - 역할: Cognito GlobalSignOut 등 로그아웃 처리 프록시 또는 클라이언트 토큰 삭제 트리거

- `GET /api/auth/me`
  - 역할: 현재 JWT 기준 유저 정보 조회
  - 플로우:
    1. Authorization 헤더의 JWT 검증 (시그니처, 만료, aud 등)
    2. `sub`로 `users` 조회
    3. `UserSummary` 형태로 응답

### 4.3 Django에서의 JWT 검증 구현

- Cognito JWKS(JSON Web Key Set) 엔드포인트에서 공개키 가져오기 (캐싱 필수)
- 토큰 검증 항목:
  - 시그니처 검증
  - `iss`, `aud`, `exp`, `token_use` 등 클레임 체크
- 검증 후 컨텍스트에 `request.user` 또는 별도의 `request.cognito_user` 형태로 정보 제공
- DRF의 `Authentication` 클래스를 커스텀 구현하여 적용

---

## 5. PoC 구현 우선순위 (기능 단위)

### 5.1 1단계: 인프라 및 스켈레톤

1. **Docker 환경 구성**
   - `docker-compose.yml`에 `app`, `db` 서비스 정의
   - `db`: PostgreSQL + 초기 환경 변수/볼륨 설정
   - `app`: Django 기본 프로젝트 생성, `requirements.txt`/`poetry` 등 의존성 정의

2. **Django 기본 세팅**
   - 프로젝트 생성 (`config` 등)
   - PostgreSQL 연결 설정
   - 기본 `users` 모델 및 마이그레이션 생성

3. **헬스체크용 엔드포인트**
   - `/health` 등 간단한 JSON 응답 뷰 (인증 없음)

### 5.2 2단계: 인증/계정 PoC

1. **Cognito 연동 설정**
   - User Pool ID, App Client ID/Secret, Region 등을 환경변수로 관리
   - Cognito API 호출용 헬퍼/서비스 모듈 구현

2. **Auth API 구현 (기본)**
   - `POST /api/auth/signup`
   - `POST /api/auth/login`
   - `GET /api/auth/me`

3. **JWT 인증 미들웨어/DRF Authentication 클래스 구현**
   - 인증이 필요한 대표 엔드포인트에 적용 (예: `/api/home`)

### 5.3 3단계: 핵심 도메인 PoC

`openapi.yaml` 기준, 대표적인 엔드포인트를 일부 선택해 구현한다.

- **홈/퀘스트**
  - `GET /api/home`
  - `GET /api/quests`

- **성향 분석 & 심리 검사**
  - `GET /api/psy-test/questions`
  - `POST /api/psy-test/submit` (내부에서 `analysis_results` 생성까지 포함)

- **셀프 체크**
  - `GET /api/self-check`
  - `POST /api/self-check/submit`

- **분석 결과 조회**
  - `GET /api/analysis-results/{id}`

### 5.4 4단계: SNS 연동 및 부가 기능 (선택)

- SNS 연동 (import_sns)
  - `GET /api/sns/channels`
  - `GET /api/me/sns-accounts`
  - `POST /api/sns/import`
- 앱 설정
  - `GET /api/app-settings/public`

---

## 6. 개발/테스트 플로우

1. **로컬 개발**
   - `docker-compose up`으로 app + db 기동
   - Django `runserver` 또는 gunicorn/uvicorn으로 WAS 실행

2. **마이그레이션 관리**
   - `python manage.py makemigrations`
   - `python manage.py migrate`

3. **테스트 전략(간단)**
   - 유닛 테스트: 각 앱별 `tests.py` 또는 `tests/` 폴더
   - API 테스트: DRF APIClient 또는 Postman/Insomnia로 OpenAPI 스펙에 맞춰 검증

4. **OpenAPI와 동기화**
   - 엔드포인트/스키마 변경 시 `openapi.yaml`을 기준으로 Django Serializer/View를 맞추거나,
     추후 `drf-spectacular` 등으로 스펙 자동 생성도 고려.

---

## 7. 향후 확장 고려사항

- Django 인증 체계와 Cognito 연동 방식 표준화
  - 장기적으로는 Django의 `AuthenticationBackend`와 연동해 admin 등도 Cognito 기반으로 통합할지 여부 결정
- 캐시/성능
  - Psy 질문, 퀘스트 템플릿 등 정적/준정적 데이터는 캐시 (Redis 등) 고려
- 로깅/모니터링
  - Cognito 에러, JWT 검증 실패, DB 장애 등을 중앙 로깅으로 수집
- 배포
  - PoC 이후에는 CI/CD 파이프라인에서 Docker 이미지를 빌드/배포하는 흐름 설계

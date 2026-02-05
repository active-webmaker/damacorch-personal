# 페이지에 필요한 UI 요소 목록
## SNS
뒤로가기
가져오기
채널

---

## DB 설계

### 1. 기본 개념
- 이 페이지에서 하는 일
  - 사용자가 **SNS 계정(채널)**을 선택해서 서비스를 연동하거나, 그 채널에서 데이터를 가져오는 트리거 역할
- 필요한 데이터
  - 어떤 SNS 채널들이 지원되는지 목록
  - 해당 유저가 이미 어떤 SNS 계정을 연동했는지 여부

### 2. 주요 테이블

#### 2-1. users (요약)
- 공통 유저 정보 테이블 (이미 존재한다고 가정)
- **컬럼 예시**
  - `id` (PK, bigint)
  - `email` (unique)
  - `name`
  - `created_at`
  - `updated_at`

#### 2-2. sns_channels (지원 채널 마스터)
- **테이블명**: `sns_channels`
- 어떤 SNS 채널을 지원하는지 정의
- **컬럼**
  - `id` (bigint, PK)
  - `code` (varchar(50), unique)
    - 예: `"instagram"`, `"facebook"`, `"twitter"`, `"kakao"` 등
  - `name` (varchar(100))
    - 사용자에게 보여줄 이름 (예: "인스타그램")
  - `icon_url` (varchar(255), nullable)
    - 채널 아이콘 이미지 URL (있다면)
  - `is_active` (boolean)
    - 현재 사용 가능 여부
  - `created_at` (datetime)
  - `updated_at` (datetime)

#### 2-3. user_sns_accounts (유저별 SNS 연동 정보)
- **테이블명**: `user_sns_accounts`
- 유저가 어떤 SNS 계정을 어떤 채널에 연동했는지 관리
- **컬럼**
  - `id` (bigint, PK)
  - `user_id` (bigint, FK → users.id)
  - `sns_channel_id` (bigint, FK → sns_channels.id)
  - `external_user_id` (varchar(255))
    - SNS 측 유저 ID (예: 인스타그램 user id)
  - `display_name` (varchar(255), nullable)
    - SNS 상에서의 표시 이름/닉네임 (있다면)
  - `access_token` (text, nullable)
    - OAuth 토큰 등 (실제 구현 시에는 암호화/별도 보안 저장 필요)
  - `refresh_token` (text, nullable)
  - `status` (varchar(20))
    - 예: `"connected"`, `"revoked"`
  - `connected_at` (datetime)
  - `disconnected_at` (datetime, nullable)
  - `created_at` (datetime)
  - `updated_at` (datetime)

※ 실제 토큰 보안 정책은 인프라/보안 설계 시 별도 논의 필요. 이 문서에서는 구조만 정의.

---

## API 설계

### 1. 지원 SNS 채널 목록 조회

#### 1) GET /api/sns/channels
- **설명**
  - 현재 서비스에서 지원하는 SNS 채널 목록을 조회
  - "채널" UI 목록을 그릴 때 사용
- **응답 예시**
  ```json
  [
    {
      "id": 1,
      "code": "instagram",
      "name": "인스타그램",
      "iconUrl": "https://.../icons/instagram.png"
    },
    {
      "id": 2,
      "code": "kakao",
      "name": "카카오톡",
      "iconUrl": "https://.../icons/kakao.png"
    }
  ]
  ```

### 2. 유저의 SNS 연동 현황 조회

#### 2) GET /api/me/sns-accounts
- **설명**
  - 현재 로그인한 유저가 어떤 SNS 채널과 연동돼 있는지 조회
  - 채널 목록 옆에 "연동됨" 표시 등 UI 상태 표현 가능
- **응답 예시**
  ```json
  [
    {
      "snsChannel": {
        "id": 1,
        "code": "instagram",
        "name": "인스타그램"
      },
      "status": "connected",
      "displayName": "my_ig_account"
    }
  ]
  ```

### 3. SNS 연동/가져오기 트리거

#### 3) POST /api/sns/import
- **설명**
  - 사용자가 특정 채널을 선택하고 "가져오기" 버튼을 눌렀을 때 호출
  - 실제 OAuth 연동 URL 리다이렉트 또는 백엔드에서 가져오기 작업을 시작하는 트리거로 사용
- **요청 Body 예시**
  ```json
  {
    "snsChannelCode": "instagram"
  }
  ```
- **응답 예시 (OAuth 리다이렉트 URL 예)**
  ```json
  {
    "authUrl": "https://api.instagram.com/oauth/authorize?..."
  }
  ```
- 또는 이미 토큰이 있고, 바로 데이터 동기화를 시작하는 경우
  ```json
  {
    "status": "started",
    "message": "인스타그램 데이터 동기화를 시작했습니다."
  }
  ```

---

## 화면 요소 ↔ DB/API 매핑 메모
- 뒤로가기
  - 프론트 라우팅 처리 (DB 연관 없음)
- 가져오기 버튼
  - API: `POST /api/sns/import` 호출
  - Body: `snsChannelCode` (사용자가 선택한 채널)
- 채널
  - DB: `sns_channels`, `user_sns_accounts`
  - API:
    - 채널 목록: `GET /api/sns/channels`
    - 유저 연동 현황: `GET /api/me/sns-accounts`


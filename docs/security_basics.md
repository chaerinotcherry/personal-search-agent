# 백엔드 보안 기초

## 인증과 인가

인증(Authentication)은 "당신이 누구인지" 확인하는 과정이고, 인가(Authorization)는 "무엇을 할 수 있는지" 결정하는 과정입니다. JWT 토큰 기반 인증은 서버가 상태를 저장하지 않아 확장성이 뛰어납니다. OAuth 2.0은 서드파티 서비스(Google, GitHub)를 통한 인증을 표준화합니다. RBAC(Role-Based Access Control)로 역할에 따라 리소스 접근을 제어합니다.

## SQL 인젝션 방지

SQL 인젝션은 악의적인 SQL 코드를 입력에 삽입해 DB를 공격하는 기법입니다. ORM을 사용하거나 파라미터화된 쿼리(Prepared Statement)를 사용하면 방지됩니다. 절대 사용자 입력을 SQL 문자열에 직접 연결하지 않습니다. 입력값 검증(화이트리스트 방식)으로 예상치 못한 값을 사전에 차단합니다.

## XSS와 CSRF

XSS(Cross-Site Scripting)는 악성 스크립트를 웹 페이지에 삽입하는 공격입니다. 사용자 입력을 그대로 HTML에 출력하지 않고 이스케이프 처리합니다. CSP(Content Security Policy) 헤더로 허용된 스크립트 소스를 제한합니다. CSRF(Cross-Site Request Forgery)는 사용자 몰래 의도치 않은 요청을 보내는 공격입니다. CSRF 토큰, SameSite 쿠키 속성, Origin 헤더 검증으로 방어합니다.

## 민감 정보 관리

비밀번호는 bcrypt, Argon2, scrypt 등 단방향 해시 함수로 저장합니다. API 키, DB 패스워드 등 시크릿은 환경변수나 Secret Manager(AWS Secrets Manager, HashiCorp Vault)로 관리합니다. 코드 저장소에 시크릿을 커밋하지 않습니다. `.gitignore`에 `.env` 파일을 추가하고, git-secrets나 pre-commit 훅으로 실수를 방지합니다.

## HTTPS와 TLS

모든 통신은 HTTPS(TLS 1.2 이상)를 사용합니다. Let's Encrypt로 무료 SSL 인증서를 발급받을 수 있습니다. HSTS(HTTP Strict Transport Security) 헤더로 브라우저가 항상 HTTPS를 사용하도록 강제합니다. 인증서 만료를 모니터링하고 자동 갱신을 설정합니다.

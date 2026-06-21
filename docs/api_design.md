# REST API 설계 모범 사례

## RESTful 설계 원칙

REST(Representational State Transfer)는 HTTP를 활용한 API 설계 아키텍처 스타일입니다. 리소스는 명사로 표현하고(예: `/users`, `/products`), HTTP 메서드로 행위를 나타냅니다. GET은 조회, POST는 생성, PUT/PATCH는 수정, DELETE는 삭제에 사용합니다. URL에 동사를 넣지 않는 것이 원칙입니다(`/getUser` 대신 `GET /users/{id}`).

## URI 설계

컬렉션은 복수형 명사를 사용합니다. 계층 관계는 슬래시로 표현합니다(예: `/users/{id}/orders`). 필터링은 쿼리스트링을 활용합니다(`/products?category=electronics&sort=price`). 버전은 URI(`/v1/users`)나 헤더(`Accept: application/vnd.api+json; version=1`)로 관리합니다. URI는 소문자와 하이픈(-)을 사용하고 밑줄(_)은 피합니다.

## HTTP 상태 코드

올바른 상태 코드 사용이 API 품질의 핵심입니다. 200 OK(성공), 201 Created(생성 완료), 204 No Content(삭제 성공). 400 Bad Request(잘못된 요청), 401 Unauthorized(인증 필요), 403 Forbidden(권한 없음), 404 Not Found(리소스 없음), 409 Conflict(중복), 422 Unprocessable Entity(유효성 오류). 500 Internal Server Error(서버 오류), 503 Service Unavailable(서비스 불가).

## 응답 포맷 일관성

에러 응답 형식을 표준화하면 클라이언트 처리가 쉬워집니다. 성공 시 데이터와 메타정보를, 에러 시 오류 코드, 메시지, 상세 내용을 일관된 구조로 반환합니다. Pagination은 `total`, `page`, `limit`, `items` 필드를 포함하고, 링크 기반 페이지네이션(`next`, `prev` URL)도 고려합니다.

## API 버저닝 전략

URI 버저닝(`/v1/`, `/v2/`)은 직관적이지만 URL이 지저분해집니다. 헤더 버저닝(`API-Version: 2`)은 깔끔하지만 캐싱에 불리합니다. 쿼리 파라미터 버저닝(`?version=2`)은 간편하지만 필수 파라미터처럼 보입니다. 실무에서는 URI 버저닝이 가장 많이 사용되며, 하위 호환성이 깨지는 변경에만 버전을 올립니다.

## 인증과 보안

JWT(JSON Web Token)는 Stateless 인증에 주로 사용됩니다. Access Token은 짧은 유효기간(15분~1시간), Refresh Token은 긴 유효기간(7~30일)으로 설정합니다. API Key는 서버 간 통신에, OAuth 2.0은 서드파티 인증에 적합합니다. HTTPS를 필수로 적용하고, Rate Limiting으로 과도한 요청을 제한합니다. CORS 헤더를 적절히 설정해 브라우저 보안 정책을 준수합니다.

## OpenAPI (Swagger) 문서화

OpenAPI 명세로 API를 문서화하면 프론트엔드 개발자, QA, 외부 파트너와 소통이 원활해집니다. FastAPI는 자동으로 OpenAPI 명세를 생성합니다. 각 엔드포인트에 description, 예시 요청/응답, 에러 케이스를 명시하면 문서 품질이 높아집니다.

# 백엔드 테스트 전략

## 테스트 피라미드

테스트 피라미드는 단위 테스트(Unit) → 통합 테스트(Integration) → E2E 테스트 순으로 비중을 높게 가져가라는 원칙입니다. 단위 테스트는 빠르고 독립적이며 가장 많이 작성합니다. 통합 테스트는 여러 컴포넌트의 협력을 검증합니다. E2E 테스트는 느리고 유지비가 크므로 핵심 흐름만 커버합니다.

## pytest로 FastAPI 테스트

FastAPI는 `TestClient`(httpx 기반)로 동기 테스트를, `AsyncClient`로 비동기 테스트를 지원합니다. `pytest.fixture`로 테스트 DB, 가짜 인증 토큰, 클라이언트를 설정합니다. `pytest-asyncio`로 비동기 테스트를 실행합니다. 테스트용 DB는 SQLite 인메모리 또는 Docker로 실행한 PostgreSQL을 사용합니다.

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
```

## 모킹(Mocking)

외부 API 호출, 이메일 발송, 결제 처리 등을 테스트할 때 실제 서비스를 호출하면 느리고 비용이 발생합니다. `unittest.mock.patch`나 `pytest-mock`의 `mocker`로 외부 의존성을 모킹합니다. FastAPI의 `Depends`를 오버라이드해 DB 세션이나 인증 의존성을 테스트용으로 교체합니다.

## 테스트 커버리지

`pytest-cov`로 커버리지를 측정합니다. 커버리지 100%가 목표가 아니라 중요한 비즈니스 로직이 테스트되었는지가 중요합니다. 에러 경로(예외, 잘못된 입력)도 반드시 테스트합니다. CI/CD 파이프라인에 커버리지 임계값(예: 80%)을 설정해 품질을 유지합니다.

## 부하 테스트

Locust나 k6로 API의 성능 한계를 측정합니다. 동시 사용자 수를 점진적으로 늘리며 응답 시간과 에러율을 모니터링합니다. 병목 지점(DB 쿼리, 외부 API, 메모리 누수)을 찾아 개선합니다. 성능 테스트 결과를 기준치로 삼아 배포 전 회귀 테스트를 진행합니다.

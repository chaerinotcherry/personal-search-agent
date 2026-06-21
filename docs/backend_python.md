# Python 백엔드 개발 기초

## FastAPI 소개

FastAPI는 Python으로 API를 빠르게 개발할 수 있는 현대적인 웹 프레임워크입니다. Starlette와 Pydantic을 기반으로 하며, 자동 문서화(Swagger UI, ReDoc)를 기본 제공합니다. 비동기(async/await)를 완전히 지원해 고성능 API 서버 구현에 적합합니다.

FastAPI의 주요 특징은 타입 힌트를 활용한 자동 유효성 검사입니다. 함수 파라미터에 Python 타입을 선언하면 Pydantic이 자동으로 요청 데이터를 검증하고 변환합니다. 이 덕분에 런타임 오류를 줄이고 개발 생산성을 높일 수 있습니다.

## 라우터 설계

FastAPI에서 라우터는 `APIRouter`를 사용해 기능별로 분리합니다. 예를 들어 사용자 관련 API는 `users.py`에, 상품 관련 API는 `products.py`에 분리해 모듈화합니다. 각 라우터는 prefix와 tags를 지정해 Swagger 문서에서도 깔끔하게 구분됩니다.

```python
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
```

## 의존성 주입 (Dependency Injection)

FastAPI의 `Depends`를 사용하면 공통 로직(인증, DB 세션, 설정값 등)을 재사용할 수 있습니다. 의존성은 중첩이 가능하고 비동기도 지원합니다. 이 패턴을 활용하면 코드 중복 없이 횡단 관심사(Cross-cutting concerns)를 처리할 수 있습니다.

## Pydantic 모델 활용

Pydantic BaseModel을 상속해 요청/응답 스키마를 정의합니다. `validator` 또는 `field_validator`로 커스텀 유효성 검사를 추가할 수 있습니다. `model_config`로 ORM 모드를 활성화하면 SQLAlchemy 모델을 직접 직렬화할 수 있어 편리합니다.

## 미들웨어

미들웨어는 모든 요청/응답을 가로채 처리합니다. CORS 설정, 로깅, 인증 토큰 검증, 요청 속도 제한 등을 미들웨어로 구현합니다. FastAPI에서는 `@app.middleware("http")`로 커스텀 미들웨어를 등록하거나, Starlette의 `BaseHTTPMiddleware`를 상속해 구현합니다.

## 예외 처리

FastAPI는 `HTTPException`으로 HTTP 오류를 반환합니다. `@app.exception_handler`로 전역 예외 핸들러를 등록하면 일관된 오류 응답 형식을 유지할 수 있습니다. 커스텀 예외 클래스를 만들고 핸들러를 등록하는 패턴이 실무에서 많이 사용됩니다.

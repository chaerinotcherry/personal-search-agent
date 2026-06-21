# 동시성과 비동기 프로그래밍

## Python async/await

Python의 asyncio는 이벤트 루프 기반 비동기 프로그래밍을 지원합니다. `async def`로 코루틴을 정의하고, `await`로 I/O 대기 중 다른 코루틴에게 제어권을 넘깁니다. 네트워크 요청, DB 쿼리, 파일 I/O처럼 대기 시간이 긴 작업에서 비동기의 효과가 큽니다. CPU 바운드 작업에는 비동기보다 멀티프로세싱이 적합합니다.

## FastAPI의 비동기 처리

FastAPI는 async/await를 완전히 지원합니다. `async def` 엔드포인트는 asyncio 이벤트 루프에서 실행되고, 동기 `def` 엔드포인트는 스레드풀에서 실행됩니다. `httpx.AsyncClient`로 비동기 HTTP 요청을, `asyncpg`나 `aiomysql`로 비동기 DB 쿼리를 처리합니다. `asyncio.gather()`로 여러 비동기 작업을 동시에 실행해 응답 시간을 줄입니다.

## 백그라운드 태스크

FastAPI의 `BackgroundTasks`로 응답 반환 후 작업을 비동기적으로 처리합니다. 이메일 발송, 파일 처리, 외부 API 호출 등 즉각적인 응답이 필요 없는 작업에 적합합니다. 더 복잡한 비동기 작업 큐가 필요하면 Celery + Redis/RabbitMQ를 사용합니다. Celery는 재시도, 스케줄링, 모니터링(Flower)을 지원합니다.

## 캐싱 전략

Redis는 인메모리 데이터 스토어로 캐싱에 널리 사용됩니다. 데이터베이스 쿼리 결과, API 응답, 세션 정보를 캐싱해 응답 시간을 단축합니다. TTL(Time To Live)로 캐시 만료 시간을 설정하고, 데이터 변경 시 캐시를 무효화(Invalidation)합니다. Cache-Aside, Write-Through, Write-Behind 등 캐싱 패턴을 상황에 맞게 선택합니다.

## 레이트 리미팅

API 남용을 방지하기 위해 요청 횟수를 제한합니다. 슬라이딩 윈도우(Sliding Window) 또는 토큰 버킷(Token Bucket) 알고리즘을 사용합니다. Redis의 `INCR`과 TTL로 간단한 레이트 리미터를 구현할 수 있습니다. 사용자별, IP별, API 키별로 다른 제한을 적용해 유연한 정책을 구성합니다.

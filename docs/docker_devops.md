# Docker와 컨테이너 기반 배포

## Docker 기초

Docker는 애플리케이션을 컨테이너로 패키징해 어디서든 동일하게 실행할 수 있게 합니다. 이미지(Image)는 실행 환경의 스냅샷이고, 컨테이너(Container)는 이미지의 실행 인스턴스입니다. Dockerfile로 이미지를 정의하며, `docker build`, `docker run`, `docker push` 명령으로 빌드·실행·배포합니다.

## Dockerfile 최적화

레이어 캐싱을 활용하려면 자주 변경되는 파일(소스코드)을 Dockerfile 하단에 배치합니다. 의존성 파일(`requirements.txt`, `package.json`)을 먼저 복사하고 설치해 소스코드 변경 시 캐시를 재사용합니다. 멀티 스테이지 빌드로 최종 이미지 크기를 줄입니다. Alpine Linux 기반 이미지를 사용하면 이미지 크기가 대폭 줄어듭니다.

## Docker Compose

여러 컨테이너로 구성된 서비스를 `docker-compose.yml`로 정의하고 `docker compose up`으로 한 번에 실행합니다. `depends_on`으로 서비스 시작 순서를 지정하고 `healthcheck`로 준비 여부를 확인합니다. 볼륨(Volume)으로 데이터를 영속화하고, 네트워크로 서비스 간 통신을 격리합니다. 환경변수는 `.env` 파일로 관리해 민감 정보를 코드에서 분리합니다.

## CI/CD 파이프라인

GitHub Actions, GitLab CI, Jenkins로 자동화 파이프라인을 구성합니다. 코드 푸시 → 테스트 실행 → 이미지 빌드 → 레지스트리 푸시 → 배포 순서로 진행합니다. 브랜치 전략(feature → develop → main)에 따라 개발/스테이징/프로덕션 환경을 분리합니다. 배포 전략으로 블루-그린 배포, 롤링 업데이트, 카나리 배포가 있습니다.

## 서버 모니터링

Prometheus + Grafana로 메트릭을 수집하고 시각화합니다. 주요 모니터링 지표: CPU/메모리 사용률, 요청 처리량(RPS), 응답 시간 P95/P99, 에러율. 로그는 ELK 스택(Elasticsearch, Logstash, Kibana) 또는 Loki + Grafana로 중앙화합니다. 알림은 Slack, PagerDuty 등으로 연동해 온콜 대응을 자동화합니다.

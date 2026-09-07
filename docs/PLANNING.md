# Lina OS 기획과 다음 작업

Lina OS는 설계 단계입니다. OS 이미지·설치기·독립 데스크톱은 아직 구현하지 않았습니다.
[modules.json](../modules.json)이 현재 구성과 Lina 소스 리비전을,
[수용 기준](ACCEPTANCE.md)이 실제 배포에 필요한 증거를 정의합니다.

## OS가 소유하는 계획

| 기획 | 문서 | 요구와 검증 |
| --- | --- | --- |
| Omarchy 기반 에이전트 OS | [전체 설계](plans/260906_lina_os/000_design.md) | 독립 데스크톱, 자동 호스트 작업, 사람의 관찰·인수, 로그인 재사용 |
| 구현 순서 | [구현 단계와 검증](plans/260906_lina_os/002_delivery.md) | 동시 입력, 입력 소유권, 호스트 대상 증명, 복구·업데이트 |
| VM에서 물리 서버로 전환 | [VM·서버 전환](plans/260906_lina_os/003_server_transition.md) | 게스트·외부 호스트 구분, 무인 부팅, 자원 실측, 복구 가능한 전환 |
| 원격 연결 | [Tailscale 온보딩](plans/260906_lina_os/004_tailscale_onboarding.md) | 장비 등록, 다른 장비의 인증된 접속, 중단 후 이어가기 |
| OpenCodex | [설치와 운영](plans/260906_lina_os/006_opencodex.md) | 버전 고정, 서비스 준비, 실제 인증·추론, 설정 보존 |
| OmO Native | [설치와 운영](plans/260906_lina_os/007_omo.md) | 독립 개발 도구, 작업 결과·취소·복구 검증 |

## Lina 제품이 소유하는 계약

아래 링크는 모듈 명세와 같은 Lina 리비전을 가리킵니다. 의존 버전을 바꿀 때 함께 검토합니다.

- [컴퓨터·실행·입력 소유권](https://github.com/thisisjun786/lina/blob/e41ce13bf4566f5850936742186e1643266959e9/docs/plans/platform/001_runtime_contracts.md): 공통 API와 상태 계약
- [모델 선택과 로컬 큐레이션](https://github.com/thisisjun786/lina/blob/e41ce13bf4566f5850936742186e1643266959e9/docs/plans/platform/005_model_onboarding.md): 모델 선택·자원 기준·연결 확인
- [설치 구성과 상태 버전관리](https://github.com/thisisjun786/lina/blob/e41ce13bf4566f5850936742186e1643266959e9/docs/plans/platform/008_refactor_preparation.md): 데이터 홈·체크포인트·복구 경계
- [제품 기획 목록](https://github.com/thisisjun786/lina/blob/e41ce13bf4566f5850936742186e1643266959e9/docs/PLANNING.md): UI·Electron·첨부·이미지·일상·월드 기능

실행 엔진은 Codex이며 프로바이더 연결은 OpenCodex를 기준으로 합니다.
Senpi 실행과 OmO 작업 패키지는 제거됐습니다. OmO Native 필수 설치는 OS 개발 도구 구성이고,
Lina의 첫 실행을 OmO에 종속시키는 요구가 아닙니다.

## 유지할 제품 경계

사용자 데이터는 `LINA_HOME`, 기본 `~/.lina`에 둡니다. OS 메타데이터·소켓·서비스 등록과
데스크톱 상태 위치는 실제 구현에서 별도로 정합니다. 외부 서비스의 데이터는 각 서비스가
소유하며, 전체 복구에는 해당 서비스의 내보내기·복원 절차도 필요합니다.

Lina의 첫 사용자 소개와 OS 설치 준비는 다릅니다. 소개는 처음 한 번 대화로 진행하고,
이후 에이전트 추가도 리나가 돕습니다. OS는 필수 연결·도구 준비를 별도로 확인하며,
연결 장애 때문에 소개나 기억을 초기화하지 않습니다.

공유 로그인과 병렬 GUI 입력은 유지할 요구입니다. 실행 UID·브라우저 프로필·데스크톱
백엔드는 실제 실험 뒤 결정합니다. 자동 실행은 항상 root로 실행한다는 뜻이 아닙니다.
호스트 접근과 실행 격리도 별도로 선택합니다.

계획의 후보·미정 사항을 구현 완료로 표시하지 않습니다. 외부 버전과 인터페이스는 구현 전에
재확인하고, 실제 설치·서비스·디스크 변경에는 구체적인 실행 대상과 권한이 필요합니다.

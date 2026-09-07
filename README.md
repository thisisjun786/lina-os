# Lina OS

Lina OS는 Omarchy 데스크톱과 지속적으로 동작하는 개인 에이전트
**LINA — Lifelong Intelligent Networked Agent**를 묶는 OS 배포판 프로젝트입니다.

**현재는 설계 단계입니다.** 모듈 구성과 설치·데스크톱·복구 요구를 정의하고 있으며,
부팅 이미지와 OS 설치기는 아직 구현하지 않았습니다. 이 저장소를 복제해도
운영 서비스가 설치되지는 않습니다.

## Lina와 Lina OS

[Lina](https://github.com/thisisjun786/lina)는 에이전트, 대화, 페르소나, 메모리,
Codex 작업 실행과 웹 앱을 담당합니다. Lina OS는 고정한 Lina 소스를 기반으로
OS, 데스크톱 연동, 설치 구성, 업데이트와 복구 검증을 담당합니다.

Lina 런타임만 직접 설치하는 구성, 전용 작업 컴퓨터를 연결하는 구성, 전체 OS를
설치하는 구성을 구분합니다. 호스트 접근 권한과 실행 격리도 별도로 선택합니다.
OmO Native는 OS의 독립 개발 도구이며 Lina 실행의 필수 런타임이 아닙니다.

## 설계 읽기

- [모듈 명세](modules.json): 설치 구성, 모듈 소유권, 고정한 Lina 소스 리비전
- [기획과 다음 작업](docs/PLANNING.md): OS 계획과 Lina 제품 계약
- [설치·운영 수용 기준](docs/ACCEPTANCE.md): 실제 환경에서 입증해야 할 동작
- [CI](docs/CI.md): 소스 검사와 OS 실행 검증의 범위

사용자 데이터는 명시한 `LINA_HOME`, 기본 `~/.lina`에 둡니다. 업데이트와 복구는
대화·메모리·작업 공간·인증 정보를 보존해야 합니다. 독립 GUI 입력, 로그인 재사용,
사람의 제어권 인수와 재부팅 복구는 실제 일회용 게스트에서 검증할 요구입니다.

## 기여와 라이선스

[기여 안내](CONTRIBUTING.md)에 따라 짧은 작업 브랜치에서 `dev`로 PR을 보냅니다.
[POLICY.md](POLICY.md)가 CI와 머지 정책을 소유하며, `main` 승격과 OS 배포는
각각 별도로 판단합니다. 버그·기능·호환성·설계 결정 이슈 양식을 제공합니다.

자체 소스와 문서는 [Apache-2.0](LICENSE)으로 제공합니다.
외부 구성요소는 각자의 [라이선스와 고지](THIRD_PARTY_NOTICES.md)를 따릅니다.
[보안 제보](SECURITY.md) · [공개 소스 범위](docs/PUBLICATION.md)

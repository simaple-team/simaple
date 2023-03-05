[![kr](https://img.shields.io/badge/lang-kr-red.svg)](README.md)
[![en](https://img.shields.io/badge/lang-en-red.svg)](README.en.md)

# simaple: Simulation library for Maplestory

`simaple` 은 메이플스토리 내 전투 환경을 분석히기 위한 라이브러리입니다. 

simaple은 클라이언트 리소스를 바탕으로 메이플스토리 내 직업의 시뮬레이션 환경을 구성하고, 적절한 전투 시나리오를 설계하여 스킬별 딜 비중 및 기대 DPM을 계산할 수 있도록 합니다.

- 실제 메이플스토리 내 게임 설정을 바탕으로 한 realistic한 시뮬레이션 환경 제공
- 제시된 캐릭터의 기대 DPM 을 포함한 전투결과 생성 및 분석
- 게임 내 유저 정보를 바탕으로 한 시뮬레이션 환경 제공
- 환산 주스텟을 포함한, 캐릭터 스펙에 대한 다차원적 지표 계산


## Web Client

simaple은 시뮬레이션을 쉽게 진행하기 위한 웹 인터페이스 또한 제공합니다.

![image](https://user-images.githubusercontent.com/39217532/222165238-00926269-e581-4cd6-8e4c-aef5cff8e4ce.gif)
- 웹 클라이언트는 [simaple/web](https://github.com/simaple-team/web) 에서 설치할 수 있습니다.


## Install

- `pip install simaple`

## Documentation

- https://simaple.readthedocs.io/en/latest/


### Community

- [Discord](https://discord.gg/5hgN5EbyA4)
- [Slack](https://join.slack.com/t/maplestorydpmcalc/shared_invite/zt-1lwi3l97o-EH0R9~W97SB8TjsoXnpzpQ)


## Developments & Contribution

- See [CONTRIBUTING](CONTRIBUTING.md)

## 지원되는 기능

### 인게임 시뮬레이션
- interactive한 시뮬레이션 환경 생성
  - 쿨타임 감소 효과, 버프 지속시간 증가, 코어 강화 등 인 게임내 존재하는 모든 변수를 적용한 시뮬레이션 환경을 구축 가능
- 시뮬레이션 진행 결과에 대한 분석
  - DPM 계산
  - 스킬 별 점유율 계산
  - 전체 시뮬레이션 결과를 human-readable format으로 출력하여 custom 분석 

### 아이템 관련
- 스타포스 및 주문서 강화 적용 시 기대되는 아이템 성능 계산 
- GearBlueprint를 통해, 환산 주스텟 등에 사용되는 기준 캐릭터 스펙의 성능 계산
- 환산 주스텟 계산, 스텟별 효율 계산

### 홈페이지 연동
- 홈페이지로부터 정보 공개에 동의한 캐릭터를 simaple object로 로드 기능

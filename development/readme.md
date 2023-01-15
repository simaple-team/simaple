# Table of Contents

<!-- toc -->

- [Contributing to simaple](#contributing-to-simaple)
- [Developing simaple](#developing-simaple)
  - [Prerequisites](#prerequisites)
  - [setup](#setup)
- [Starting Points](#starting-points)
- [Unittest](#unittest)
- [Code style]($code-style)
- [Commit style]($commit-style)
- [Pull Request](#pull-request)
  - [Prerequesites](#pr-prerequiste)
  - [Review process](#review-process)
  - [For BUG FIX PR](#for-bug-fix-pr)
- [ADR](#adrarchitecture-decision-record)
- [Release](#release)

<!-- tocstop -->

# Contributing to simaple

저희는 simaple 라이브러리의 개선에 관심있는 모든 분들의 컨트리뷰트를 환영합니다! &#127881;
여러분이 본 레포지토리에 코드를 통해 기여하기 이전에, 여러분의 생각을 먼저 공유해주세요.

1. 여러분이 새로운 피쳐를 추가하고 싶은 경우. 또는, 버그를 발견했고, 해당 버그를 수정하고 싶은 경우.
  - 구현하고자 하는 내용이 issue list에 있는지 확인해 주세요. 이슈가 없다면 생성해주세요.
  - 해당 이슈에 코멘트를 남겨 기여하고자함을 알리세요. repository manager가 해당 이슈에 당신을 assign해줄 거에요.

2. 아직까지 simaple의 제공 범위에 속하지 않는 새로운 기능을 제안하고 싶은 경우.
  - 여러분이 목표하고자 하는 바를 자세하게 서술하고, repository owner (@meson3241)을 멘션해주세요. repository owner가 해당 이슈를 검토하고, 관련 컨트리뷰터를 소집하고, 해당 기능에 대한 구현 여부를 여러분과 함께 결정할 것입니다.


# Developing simaple


## Prerequisites

- python >=3.9 
- poetry. 개발 환경은 poetry를 활용하여 구성됩니다.
  - poetry의 설치는 https://python-poetry.org/docs/ 를 참조합니다.

## setup

- 본 레포지토리를 clone합니다.
```bash
git clone https://github.com/simaple-team/simaple
cd simaple
```

- `poetry install` 을 통해 개발환경을 설치합니다.
```bash
poetry install
```

# Starting Points
- 인게임 정보와 라이브러리 정보의 불일치를 수정하고자 한다면, `simaple/data` 를 둘러보세요.
  - to add or fix value missmatch between library and  in-game , check `simaple/data`

- 스킬의 동작을 변경하거나 개선하고 싶다면, `simaple/simulate/component` 를 둘러보세요,
  - to fix or improve skill mechanism, check `simaple/simulate/component`

- 직업군 간에 동등한 스펙을 제공하고, 아이템을 세팅하는 과정을 수정하고 싶다면 `simaple/optimize` 와 `simaple/data/baseline` 을 둘러보세요.
  - to contribute about item and stat optimization, check `simaple/optimize` and `simaple/data/baseline`



# Unittest
unittest는 pytest를 이용하여 구성됩니다. 모든 테스트는 tests/ 또는 apptests/ 하위에 작성되어 있습니다. 모든 테스트를 돌리기 위해서는 아래 명령어를 수행합니다.

```bash
poetry run poe unittest
```

만약 특정 파일에 작성된 테스트만을 수행하기를 원한다면 아래를 시도합니다.

```bash
poetry run pytest tests/$FILE_NAME.py
```

테스트 과정에서 발생하는 표준 출력을 포함하여, 테스트 과정에 대한 구체적인 정보는 `-vvsx` option을 통해 제공받을 수 있습니다.

```bash
poetry run pytest -vvsx tests/$FILE_NAME.py
```

pytest 패키지는 단일 테스트 케이스 동작이나, 여러 테스트 파일에 대한 요청을 포함한 다양한 기능을 제공합니다. 보다 자세한 내용은 pytest 라이브러리 문서를 참조하세요.


# Code style
code style은 black, pylint, mypy를 통해 검사됩니다. 
아래 세 테스트를 통과하면, 코드 스타일을 준수하고 있는 것입니다. 각각의 테스트를 동작시키기 위해서 어래의 명령어를 입력하세요.

```bash
poetry run poe format #for black
poetry run poe lint # for pylint
poetry run poe typetest # for mypy
```

- 모든 PR은 merge되기 위해서 위 세 테스트를 통과해야 합니다.
- PR must pass those checks before merged.

# Commit style
- 모든 커밋은 [conventional commit](https://www.conventionalcommits.org/en/v1.0.0/) 을 준수하여 작성하는 것이 권장됩니다.


# Pull Request

## PR Prerequiste
여러분이 PR을 요청하기 이전에, 아래 사항을 확인하세요.
  - tests/ 하위에, 여러분이 작성한 코드를 검증하기 위한 충분한 테스트가 작성되어 있어야 합니다.
  - 여러분의 코드는 [Unittest](#unittest)를 통과해야 합니다.
  - 여러분의 코드는 [code style](#code-style)을 준수해야 합니다.

## Review process
여러분이 작성한 코드를 통해 Pull Request를 작성하면, maintainer가 자신 또는 관련 컨트리뷰터를 assign하여 리뷰할 것입니다. 단, 리뷰는 앞의 테스트 및 코드 스타일을 준수하고 있는 경우에 한정됩니다. CI가 여러분의 코드의 준수 여부를 판독하는데, commit hash 옆에 checked되지 않고 X 표시가 되면 위의 규칙을 준수하고 있지 않은 것입니다. 

어떤 요청이든, 사흘 이내에 해당 PR에 대한 리뷰 또는 코멘트가 작성되어야 합니다. 사흘 이내에 응답을 받지 못했다면, maintainer @meson3241 을 멘션하여 리뷰가 필요함을 노티합니다.

slack 또는 discord를 통해 문의하면 보다 빠르게 답변 및 의사소통을 진행할 수 있습니다.

- (for maintainers) 모든 Review는 [conventional comment](https://conventionalcomments.org/) 를 준수하여 작성합니다.


## For BUG FIX PR
- 버그 픽스 PR은 반드시, 버그로 인해 실패하는 테스트 케이스를 포함해야 합니다.
  - 해당 테스트는 또한, 버그 수정으로 인해 통과되어야 합니다.

# ADR(Architecture decision record)
- 본 프로젝트는 중요한 변경사항을 ADR을 통해 관리합니다.
- 중대한 변경사항을 제안하고자 한다면, development/adr 디렉토리 하위에 ADR template 를 기반으로 하여 ADR을 작성하고, PR을 생성합니다. Maintainer들이 함께 이에 대해 논의하고 수용 여부를 판단할 것입니다.

- We use Architecture decision record for making big change in library.
- To change architecture about library, please make document in development/adr with template and create PR. Maintainers will invited and discuss about given proposal to aceept or not.


# Release
- 본 프로젝트는 develop branch를 사용하지 않습니다. 모든 변경사항은 main에 바로 merge됩니다.
- 프로젝트는 큰 단위의 마일스톤 레벨에서 릴리즈 됩니다. 릴리즈는 버전 태깅(x.y.z)을 통해 달성됩니다.
  - 릴리즈는 readthedocs 웹훅을 트리거합니다.
- 릴리즈 버저닝은 symantic versioning 규칙을 따릅니다.

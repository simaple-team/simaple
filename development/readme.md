# Development

## setup

- 개발 환경은 poetry를 활용하여 구성됩니다.
  - `poetry install` 을 통해 개발환경을 설치합니다.

- We use poetry for configure development environment.
  - run poetry install for create dev environment.


## code style
- black, pylint, mypy를 사용합니다. 
  - 각각의 테스트를 동작시키기 위해서 어래의 명령어를 입력하세요.
    - `poetry run poe format` for black
    - `poetry run poe lint` for pylint
    - `poetry run poe typetest` for mypy

- We use black, pylint, mypy for code styling.
  - run commands below for each test.
    - `poetry run poe format` for black
    - `poetry run poe lint` for pylint
    - `poetry run poe typetest` for mypy

- 모든 PR은 merge되기 위해서 위 세 테스트를 통과해야 합니다.
- PR must pass those checks before merged.

## Git 
- 모든 커밋은 [conventional commit](https://www.conventionalcommits.org/en/v1.0.0/) 을 준수하여 작성합니다.
- every commit may follow [conventional commit](https://www.conventionalcommits.org/en/v1.0.0/)

## Pull Request
- 모든 Review는 [conventional comment](https://conventionalcomments.org/) 를 준수하여 작성합니다.
- every PR review may follow [conventional comment](https://conventionalcomments.org/)

## Unittest
- unittest는 pytest를 이용하여 구성됩니다.
  - tests/ 하위에 작성된 코드를 검증하기 위해 충분한 테스트를 작성합니다.
  - `poetry run poe unittest` 를 통해 전체 테스트를 동작시킬 수 있습니다.

- We use pytest for unittest our library.
  - write under tests/ to provide proper test about your PR
  - you can run whole test via `poetry run poe unittest`

## BUG FIX
- 버그 픽스 PR은 반드시, 버그로 인해 실패하는 테스트 케이스를 포함해야 합니다.
  - 해당 테스트는 또한, 버그 수정으로 인해 통과되어야 합니다.

- Any bug-fix PR may include test code addition or change.
  - test modified or added may fail in previous code.


## ADR(Architecture decision record)
- 본 프로젝트는 중요한 변경사항을 ADR을 통해 관리합니다.
- 중대한 변경사항을 제안하고자 한다면, development/adr 디렉토리 하위에 ADR template 를 기반으로 하여 ADR을 작성하고, PR을 생성합니다. Maintainer들이 함께 이에 대해 논의하고 수용 여부를 판단할 것입니다.

- We use Architecture decision record for making big change in library.
- To change architecture about library, please make document in development/adr with template and create PR. Maintainers will invited and discuss about given proposal to aceept or not.


## Release
- 본 프로젝트는 develop branch를 사용하지 않습니다. 모든 변경사항은 main에 바로 merge됩니다.
- 프로젝트는 큰 단위의 마일스톤 레벨에서 릴리즈 됩니다. 릴리즈는 버전 태깅(x.y.z)을 통해 달성됩니다.
  - 릴리즈는 readthedocs 웹훅을 트리거합니다.
- 릴리즈 버저닝은 symantic versioning 규칙을 따릅니다.


## 그래서, 무엇부터 시작해야 하나요? (So, what i have to do?)
- 인게임 정보와 라이브러리 정보의 불일치를 수정하고자 한다면, `simaple/data` 를 둘러보세요.
  - to add or fix value missmatch between library and  in-game , check `simaple/data`

- 스킬의 동작을 변경하거나 개선하고 싶다면, `simaple/simulate/component` 를 둘러보세요,
  - to fix or improve skill mechanism, check `simaple/simulate/component`

- 직업군 간에 동등한 스펙을 제공하고, 아이템을 세팅하는 과정을 수정하고 싶다면 `simaple/optimize` 와 `simaple/data/baseline` 을 둘러보세요.
  - to contribute about item and stat optimization, check `simaple/optimize` and `simaple/data/baseline`


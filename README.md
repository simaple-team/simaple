# Simultion library for Maplestory

- 메이플스토리에 관련된 다양한 연산을 지원하는 패키지.
- Package for various calculation related with Maplestory.

## Install
- `pip install simaple`

## Functions

### 아이템 관련

- 강화 수치 계산, 강화 수치 역연산
- gear improvement calculation / derivation

### 스텟 관련

- 스텟 공격력 계산, 환산 주스텟 계산

### 홈페이지 연동

- 홈페이지 데이터 불러오기 기능


## Examples

### Hompage data fetch

- Fetch
```python
from simaple.fetch.application.base import KMSFetchApplication
from simaple.gear.slot_name import SlotName

app = KMSFetchApplication()

character_response = app.run("Character-Name")
```

- Load Item information
```python
from simaple.fetch.application.base import KMSFetchApplication
from simaple.gear.slot_name import SlotName

app = KMSFetchApplication()

character_response = app.run("Character-Name")
cap = character_response.get_item(SlotName.cap)

print(cap.show())
```

- Load raw-data for custom application

```python
from simaple.fetch.application.base import KMSFetchApplication

character_response = app.run("Character-Name")
raw_data = character_response.get_raw()

print(raw_data)
```

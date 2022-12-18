# Component code writting rule


### reducer and view
- Component간 상속은 reducer/view가 없는 경우에 한해 허용됩니다.
- reducer와 view method는 상속되어서는 안됩니다.
- reducer/view가 동일하여, 코드 중복을 피하기 위해서는 Trait을 사용해야 합니다.
- 이는 불필요한 Component간 의존성을 제거하여 코드 복잡도를 낮추기 위함입니다.
- Parent Component에 정의된 속성이더라도, 자식 Component에서 재정의하는것이 추천됩니다.
- Component의 모든 속성은 default 값을 가져서는 안됩니다. 이는 불필요한 속성이 주입되는 것을 확인하기 어렵게 합니다.


### Trait
- Trait는 추상 메서드와 구현으로 나뉩니다.
- Trait에 구현된 메서드는 추상 메서드로 지정된 메서드만을 사용할 수 있습니다.
- trait method 명은 `{reducer_method}_{in/None}_{trait_name}` 을 권장합니다.
- Component는 임의의 개수의 Trait을 상속받을 수 있습니다.
- 상속받은 trait 의 메서드는 온전하게 사용되는 것이 권장됩니다. 즉, trait의 메서드 호출이 메서드 구현 코드의 일부로 있지 않고 trait 메서드의 호출이 반환되는것이 reducer 구현의 전부여야 합니다. 다만 이는 권장 사항으로, 코드 중복을 피하면서 코드의 가시성을 해치지 않는 경우 trait method를 구현의 일부로 사용하여도 좋습니다.
- Trait를 사용하기 위해서는 정의된 추상 메서드가 모두 존재해야 합니다. 이는 typetest로 쉽게 확인할 수 있습니다.

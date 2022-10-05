Spec Convention
========

*Spec* 은 simaple에서 내장 객체를 정적 값으로 표현하기 위한 컨벤션입니다.

simaple은 인게임 내의 동작을 묘사하기 위한 라이브러리입니다. 실제 인게임 내에서의 요소들은 굉장히 다양합니다.
여기에는 직업군 속성, 직업군 스킬, 패시브 스텟, 또는 특정한 아이템 세팅을 비롯하여 다양한 요소들이 포함됩니다.
동작을 프로그래밍 언어를 통해 묘사하기 위해서, 이들을 통일된 형태로 표현하여, 공통되고 단일한 인터페이스를 바탕으로 위 값들을 적절히 불러와 simaple object로 매핑할 수 있어야 합니다.
이를 위해 모든 인게임 정보는 simaple Spec convention 을 기반으로 묘사되어집니다. Spec convention을 통해 묘사된 모든 객체는 SpecLoader로 통일된 인터페이스를 바탕으로
쉽게 load될 수 있습니다.

## Fields

모든 Spec은 통일된 인터페이스를 활용하기 위해, 공통적으로 정의된 필드들을 반드시 포함하고 있어야 합니다. 이들 필드들은 작성된 Spec을 올바른 class로 해석되도록 하기 위해 사용됩니다.

### Kind

모든 Spec은 `kind` field를 포함해야 합니다. `kind` field는 이 Spec이 근본적으로 어떤 요소인지를 나타냅니다. Spec은 정의된 kind에 따라 다른 Repository를 통해 해석됩니다.

### Version

Version은 Spec이 어떠한 class로 해석되어야 하는지, 그리고 어떠한 공간에서 정의되었는지를 명시합니다.
Version은 prefix와 classname으로 구성됩니다. 
prefix는 해당 classname이 어디서 정의되는지 명시합니다. prefix는 alphanumeric value 또는 dot(.) 으로 구성되어야 합니다. `simaple.io`, `simaple` namespace는 예약되어 있습니다.
classname은 해당 Spec을 해석할 때 사용할 Class의 이름을 지칭합니다. classname은 prefix와 관계없이 unique해야 합니다. classname은 지정될 Class의 이름과 정확히 일치해야 합니다.

아래와 같은 값들이 Version의 예시로서 사용될 수 있습니다.
- simaple.def/DamageSkillContainer
- custom.metric/QuadraticMetric

### Metadata

### Metadata.label

Metadata는 해당 값을 Repository에서 색인하기 위해 사용됩니다.

### Metadata.annotation

Annotation은 색인되지 않는, 그러나 여러 목적에서 사용되기 위한 값을 명시합니다.

### Data

data field는 실질적인 데이터 값을 명시합니다. 값은 반드시 key - value pair로서 구성되어야 하며 list는 허용되지 않습니다. 각 key는 Class가 인자로 받도록 설정되어 있어야 합니다.

### Patch

patch field 는 제시된 data를 주어진 값에 따라 mutate할 수 있는 patch에 대한 명세입니다. patch field가 정의되어 있다면, Spec은 load될 때 반드시 제시된 patch들을 통해 적절히 번역되어야 합니다.
patch field에는 적용되어야 하는 patch가 순서에 따라 명시되어 있으며, 순서 또는 타입이 맞지 않게 제시된 경우 명시된 Spec은 적절히 load될 수 없으며 해석 실패 또는 잘못된 클래스를 정의하게 됩니다.

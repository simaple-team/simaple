

# Event and Tags

Component에 Reducer들은 Action을 받아들인 후 적절한 Event를 발생시킵니다.
발생한 Event는 Actor에 의해서 해석되거나, 적절한 Callback을 통해 다른 Component의 행동을 규정할 수 있습니다.
즉, Event는 Component-Component 또는 Component-Actor 간의 상호작용을 매개합니다.

Event가 어디에서나 동일하게 해석될 수 있기 위하여, Event는 Tag field를 통해 제시되는 Event의 형식을 규정합니다.
Event Tag를 통해 우리는 Component에서 제시한 Event가 올바르게 해석되기를 기대할 수 있습니다.

각각의 Reducer는 다수의 Event를 발생시킬 수 있습니다.

Event tag는 simaple.simulate.reserved_names에 정의되어 있습니다. 로깅 목적, 또는 커스텀 스킬의 구현과 커스텀 컴포넌트간의 통신을 위해 커스텀 이벤트 태그를 정의하여 사용하는 것은 허용됩니다. 그러나, 그렇게 정의된 태그는 기본 컴포넌트 또는 액터에 의해 해석되지 않을 것임에 유의하십시오.

모든 기본 태그는 global로 시작합니다.

## Default Fields


# Tags

## ACCEPT / REJECT (global.accept, global.reject)

- 모든 Component Reducer는 Action의 수행을 요청받았을 때, Accept 또는 Reject Event를 발생시켜야 합니다. 
ACCEPT는, 해당 요청사항을 수신한 Component가 상태 변화를 수반하였음을 의미합니다. 반대로, REJECT event는
제시된 Action으로 인한 상태 변화가 발생하지 않았음을 의미합니다.
- REJECT event는 다른 event와 함께 전달될 수 없습니다.

### payload
- ACCEPT / REJECT event는 payload를 가지지 않습니다.

## ELAPSED (global.elapsed)

- 이 이벤트는, 컴포넌트내 상태가 시간에 따른 변화를 겪었음을 명시합니다.
- ELAPSED event에 명시된 수치를 통해, Actor는 제시된 delay가 모든 컴포넌트에 대해 적절히 수행되었음을 확인할 수 있습니다.

### payload
```ts
{
    "time": time: float
}
```

## DELAY (global.delay)

- 이 이벤트는, 컴포넌트가 수행한 행동이 유저 클라이언트 상에서의 지연을 수반함을 나타냅니다. 
- 하나의 Action은 다수의 delay event를 수반할 수 있습니다. 이러한 경우, Actor는 이를 적절히 해석하여야 합니다.

### payload
```ts
{
    "time": time: float
}
```

## DAMAGE (global.damage)

- 이 이벤트는, 컴포넌트가 수행한 행동이 몬스터에게 피해를 주어야 함을 나타냅니다.
- 하나의 Action은 다수의 damage event를 수반할 수 있습니다. 이러한 경우, 개개의 damage event는 모두 유효하게 처리되어야 합니다.

### payload

```ts
{
    "damage": damage: float,
    "hit": hit: float,
    "modifier": modifier: dict | None
}
```

## KEYDOWN_END (global.keydown_end)

- 이 이벤트는, 컴포넌트가 키다운 중이고, 키다운이 Action handling 과정에서 종료되었음을 나타냅니다.

### payload
- No payload

## DOT (global.dot)

- 이 이벤트는, 컴포넌트가 수행한 행동이 몬스터에게 DOT 피해를 입혔음을 나타냅니다.
- 이 이벤트는 DAMAGE event와 다르게 피해량 계산이 이루어집니다. 따라서, 별도의 tag가 부여되어 있습니다.

### payload

```ts
{
    "damage": damage: float,
    "hit": hit: float,
}
```

## MOB (global.mob)

- 이 이벤트는, 컴포넌트가 수행한 행동이 몬스터에게 영향을 주어야 함을 나타냅니다.
- 모든 Mob Component에서 콜백으로서 수행되어야 하는 경우 이 태그를 사용해야 합니다.
- Mob Event의 모든 method name은 pre-define되어 Mob이 listening_action을 통해 올바르게 활용할 수 있도록 제시되어야 합니다.

### payload

- method = "add_dot"
```ts
{
    "damage": damage: float
    "lasting_time": lasting_time: float,
    "name": name: str, //must be equal as event.name
}
```

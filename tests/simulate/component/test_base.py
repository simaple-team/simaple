from typing import TypedDict
from unittest.mock import MagicMock, patch

from simaple.simulate.component.base import (
    Component,
    _create_binding_with_store,
    event_tagged_reducer,
    init_component_store,
    no_op_reducer,
    reducer_method,
    regularize_returned_event,
    tag_events_by_method_name,
    view_method,
)
from simaple.simulate.core import Action, Event
from simaple.simulate.core.store import Store
from simaple.simulate.event import NamedEventProvider
from simaple.simulate.reserved_names import Tag


class TestRegularizeReturnedEvent:
    def test_none_input(self):
        """None 입력이 빈 리스트를 반환하는지 테스트"""
        assert regularize_returned_event(None) == []

    def test_single_event(self):
        """단일 이벤트가 리스트로 변환되는지 테스트"""
        event: Event = {
            "name": "test",
            "payload": {},
            "tag": "test",
            "method": "method",
            "handler": "method",
        }
        assert regularize_returned_event(event) == [event]

    def test_event_list(self):
        """이벤트 리스트가 그대로 반환되는지 테스트"""
        events: list[Event] = [
            {
                "name": "test1",
                "payload": {},
                "tag": "test1",
                "method": "method",
                "handler": "method",
            },
            {
                "name": "test2",
                "payload": {},
                "tag": "test2",
                "method": "method",
                "handler": "method",
            },
        ]
        assert regularize_returned_event(events) == events


class TestTagEventsByMethodName:
    def test_tag_events(self):
        """이벤트에 메서드 이름으로 태그가 추가되는지 테스트"""
        events: list[Event] = [
            {
                "name": "test1",
                "payload": {},
                "tag": None,
                "method": "method",
                "handler": "method",
            },
            {
                "name": "test2",
                "payload": {},
                "tag": None,
                "method": "method",
                "handler": "method",
            },
        ]
        tagged_events = tag_events_by_method_name("owner", "method", events)

        # 모든 이벤트에 메서드 이름이 태그로 추가되었는지 확인
        for event in tagged_events[:2]:
            assert event["tag"] == "method"
            assert event["method"] == "method"

        # ACCEPT 태그를 가진 추가 이벤트가 생성되었는지 확인
        assert tagged_events[2]["tag"] == Tag.ACCEPT
        assert tagged_events[2]["name"] == "owner"

    def test_accept_reject_tags(self):
        """ACCEPT 또는 REJECT 태그가 있는 경우 추가 이벤트가 생성되지 않는지 테스트"""
        events: list[Event] = [
            {
                "name": "test1",
                "payload": {},
                "tag": Tag.ACCEPT,
                "method": "method",
                "handler": "method",
            },
            {
                "name": "test2",
                "payload": {},
                "tag": None,
                "method": "method",
                "handler": "method",
            },
        ]
        tagged_events = tag_events_by_method_name("owner", "method", events)

        # 원본 이벤트 수와 동일한지 확인 (추가 ACCEPT 이벤트가 없어야 함)
        assert len(tagged_events) == 2


class StateA(TypedDict):
    value: int


class ComponentA(Component):
    def get_default_state(self) -> StateA:
        return {"value": 0}

    @reducer_method
    def increment(self, payload: int, state: StateA) -> tuple[StateA, list[Event]]:
        state["value"] += payload
        event: Event = {
            "name": "incremented",
            "payload": {"value": state["value"]},
            "tag": None,
            "method": "increment",
            "handler": "increment",
        }
        return state, [event]

    @view_method
    def get_value(self, state: StateA) -> int:
        return state["value"]


class TestComponent:
    def test_component_initialization(self):
        """컴포넌트 초기화와 기본 속성 테스트"""
        component = ComponentA(id="test_id", name="test_component")

        assert component.id == "test_id"
        assert component.name == "test_component"
        assert component.modifier is None
        assert component.disable_access is False

    def test_component_reducers(self):
        """컴포넌트의 리듀서 메서드가 올바르게 등록되는지 테스트"""
        component = ComponentA(id="test_id", name="test_component")

        # __reducers__에 메서드가 등록되었는지 확인
        assert "increment" in component.__reducers__  # type: ignore

    def test_component_views(self):
        """컴포넌트의 뷰 메서드가 올바르게 등록되는지 테스트"""
        component = ComponentA(id="test_id", name="test_component")

        # __views__에 메서드가 등록되었는지 확인
        assert "get_value" in component.__views__  # type: ignore
        assert "accessiblity" in component.__views__  # type: ignore
        assert "info" in component.__views__  # type: ignore

    @patch("simaple.simulate.component.base.compile_into_unsafe_reducer")
    @patch("simaple.simulate.component.base.event_tagged_reducer")
    def test_get_unsafe_reducers(self, mock_event_tagged_reducer, mock_compile):
        """get_unsafe_reducers 메서드가 올바른 형식의 리듀서를 반환하는지 테스트"""
        component = ComponentA(id="test_id", name="test_component")

        # 모의 함수 설정
        mock_reducer = MagicMock()
        mock_event_tagged_reducer.return_value = lambda x: mock_reducer
        mock_compile.return_value = lambda x: x

        unsafe_reducers = component.get_unsafe_reducers()

        assert len(unsafe_reducers) == 1
        assert unsafe_reducers[0]["name"] == ("test_component", "increment")
        assert unsafe_reducers[0]["target_action_signature"] == [
            ("test_component", "increment"),
            ("*", "increment"),
        ]


class TestEventTaggedReducer:
    def test_event_tagged_reducer(self):
        """event_tagged_reducer가 이벤트에 메서드 이름으로 태그를 추가하는지 테스트"""
        event_provider = NamedEventProvider("test_component")

        def test_reducer(action: Action, store: Store) -> list[Event]:
            return [
                {
                    "name": "test",
                    "payload": {},
                    "tag": None,
                    "method": "method",
                    "handler": "method",
                }
            ]

        wrapped_reducer = event_tagged_reducer(
            "test_component", "test_method", event_provider
        )(test_reducer)

        # 모의 객체 생성
        mock_action: Action = {"name": "test", "method": "test_method", "payload": {}}
        mock_store = MagicMock()

        events = wrapped_reducer(mock_action, mock_store)

        assert len(events) == 2
        assert events[0]["tag"] == "test_method"
        assert events[1]["tag"] == Tag.ACCEPT


class TestNoOpReducer:
    def test_no_op_reducer(self):
        """no_op_reducer가 빈 이벤트 리스트를 반환하는지 테스트"""
        mock_action: Action = {"name": "test", "method": "test", "payload": {}}
        mock_store = MagicMock()

        events = no_op_reducer(mock_action, mock_store)

        assert events == []


class TestCreateBindingWithStore:
    def test_create_binding_with_store(self):
        """_create_binding_with_store가 올바른 속성 주소를 생성하는지 테스트"""
        bindings = {"prop1": ".custom.prop1"}
        property_address = _create_binding_with_store(
            "test_component", ["prop1", "prop2"], bindings
        )

        assert property_address["prop1"] == ".custom.prop1"
        assert property_address["prop2"] == ".test_component.prop2"


class TestStoreInteraction:
    def test_init_component_store(self):
        """init_component_store가 스토어에 컴포넌트 상태를 초기화하는지 테스트"""
        mock_store = MagicMock(spec=Store)
        mock_local_store = MagicMock()
        mock_store.local.return_value = mock_local_store

        default_state = {"prop1": 1, "prop2": "test"}

        init_component_store("test_component", default_state, mock_store)

        # local 메서드가 호출되었는지 확인
        mock_store.local.assert_called_once_with("test_component")

        # 각 엔티티가 설정되었는지 확인
        assert mock_local_store.set_entity.call_count == 2

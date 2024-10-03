from simaple.wasm.skill import getAllComponent


def test_get_all_component():
    result = getAllComponent(
        """
---
author: meson3241
environment:
  armor: 300
  character:
    active_buffs: {}
    action_stat:
      buff_duration: 35.0
      cooltime_reduce: 5000.0
      cooltime_reduce_rate: 5.0
      summon_duration: 10.0
    stat:
      DEX: 5483.0
      DEX_multiplier: 485.0
      DEX_static: 27450.0
      INT: 1020.0
      INT_multiplier: 90.0
      INT_static: 400.0
      LUK: 1095.0
      LUK_multiplier: 90.0
      LUK_static: 280.0
      MHP: 28530.0
      MHP_multiplier: 5.0
      MMP: 17335.0
      MMP_multiplier: 5.0
      STR: 2651.0
      STR_multiplier: 111.0
      STR_static: 440.0
      attack_power: 2858
      attack_power_multiplier: 127.0
      boss_damage_multiplier: 352.0
      critical_damage: 107.1
      critical_rate: 122.0
      damage_multiplier: 150.0
      elemental_resistance: 5.0
      final_damage_multiplier: 56.2
      ignored_defence: 94.57
      magic_attack: 1424.0
      magic_attack_multiplier: 4.0
  combat_orders_level: 1
  force_advantage: 1.0
  skill_levels:
    "그라운드 제로": 13
    "매시브 파이어: IRON-B VI": 7
    "매시브 파이어: IRON-B VI (폭발)": 7
    "호밍 미사일 VI": 29
    "레지스탕스 라인 인팬트리": 30
    "로디드 다이스": 30
    "마이크로 미사일 컨테이너": 30
    "멀티플 옵션 : M-FL": 30
    "메이플월드 여신의 축복": 30
    "메카 캐리어": 30
    "메탈아머 전탄발사": 30
    "오버 드라이브": 30
  hexa_improvement_levels:
    "멀티플 옵션 : M-FL": 1
    "마이크로 미사일 컨테이너": 13
    "메탈아머 전탄발사": 3
    "메카 캐리어": 12
  jobtype: mechanic
  level: 285
  mob_level: 285
  passive_skill_level: 0
  use_doping: true
  v_improvements_level: 60
  v_skill_level: 30
  weapon_attack_power: 0
  weapon_pure_attack_power: 0
---
ELAPSE 0
"""
    )
    assert len(result) > 1

    # every component should have a name and id
    for component in result:
        assert component.name is not None
        assert component.id is not None

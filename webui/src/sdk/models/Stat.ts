export interface Stat {
  STR: number;
  LUK: number;
  INT: number;
  DEX: number;

  STR_multiplier: number;
  LUK_multiplier: number;
  INT_multiplier: number;
  DEX_multiplier: number;

  STR_static: number;
  LUK_static: number;
  INT_static: number;
  DEX_static: number;

  attack_power: number;
  magic_attack: number;
  attack_power_multiplier: number;
  magic_attack_multiplier: number;

  critical_rate: number;
  critical_damage: number;

  boss_damage_multiplier: number;
  damage_multiplier: number;
  final_damage_multiplier: number;

  ignored_defence: number;

  MHP: number;
  MMP: number;

  MHP_multiplier: number;
  MMP_multiplier: number;
}

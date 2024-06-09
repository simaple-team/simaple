import type { ActionStat } from "./ActionStat";
import type { Stat } from "./Stat";

export interface MinimalSimulatorConfiguration {
  action_stat: Partial<ActionStat>;
  job: string;

  character_stat: Stat;
  character_level: number;

  combat_orders_level?: number;
  force_advantage?: number;
  elemental_resistance_disadvantage?: number;

  target_armor?: number;
  mob_level?: number;
  weapon_attack_power?: number;
}

import { JobCategory } from "./JobCategory";
import { JobType } from "./JobType";

export interface SimulationSetting {
  tier: string;
  jobtype: JobType;
  job_category: JobCategory;
  level: number;

  use_doping: boolean;
  passive_skill_level: number;
  combat_orders_level: number;
  union_block_count: number;
  link_count: number;
  armor: number;
  mob_level: number;
  force_advantage: number;
  trait_level: number;

  v_skill_level: number;
  v_improvements_level: number;

  weapon_attack_power: number;
  weapon_pure_attack_power: number;
}

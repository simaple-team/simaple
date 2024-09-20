import { PlayLogResponse } from "@/sdk/models";

export interface SkillStatistics {
  name: string;
  damageShare: number;
  totalDamage: number;
  damagePerSecond: number;
  useCount: number;
  damagePerUse: number;
  // TODO: add hitcount and averageDamagePerHit
}

export type BattleStatistics = SkillStatistics[];

export function getBattleStatistics(logs: PlayLogResponse[]): BattleStatistics {
  const record: Record<string, SkillStatistics> = {};

  const damages = logs.flatMap((log) => log.damages);
  const totalDamage = damages.reduce((acc, damage) => acc + damage.damage, 0);

  for (const damage of damages) {
    const skillName = damage.name;

    if (!record[skillName]) {
      record[skillName] = {
        name: skillName,
        damageShare: 0,
        totalDamage: 0,
        damagePerSecond: 0,
        useCount: 0,
        damagePerUse: 0,
      };
    }

    const statistics = record[skillName];

    statistics.totalDamage += damage.damage;
    statistics.useCount += 1;
  }

  for (const skillName in record) {
    const statistics = record[skillName];
    statistics.damageShare = statistics.totalDamage / totalDamage;
    statistics.damagePerSecond =
      statistics.totalDamage / logs[logs.length - 1].clock;
    statistics.damagePerUse = statistics.totalDamage / statistics.useCount;
  }

  return Object.values(record);
}

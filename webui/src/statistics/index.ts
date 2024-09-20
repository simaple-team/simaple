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
  const skillStatistics: Record<string, SkillStatistics> = {};

  const damageRecord = logs.flatMap((log) => log.damage_records);
  const totalDamage = damageRecord.reduce((acc, record) => acc + record.damage, 0);

  for (const damage_record of damageRecord) {
    const skillName = damage_record.name;

    if (!skillStatistics[skillName]) {
      skillStatistics[skillName] = {
        name: skillName,
        damageShare: 0,
        totalDamage: 0,
        damagePerSecond: 0,
        useCount: 0,
        damagePerUse: 0,
      };
    }

    const statistics = skillStatistics[skillName];

    statistics.totalDamage += damage_record.damage;
    statistics.useCount += 1;
  }

  for (const skillName in skillStatistics) {
    const statistics = skillStatistics[skillName];
    statistics.damageShare = statistics.totalDamage / totalDamage;
    statistics.damagePerSecond =
      statistics.totalDamage / logs[logs.length - 1].clock;
    statistics.damagePerUse = statistics.totalDamage / statistics.useCount;
  }

  return Object.values(skillStatistics);
}

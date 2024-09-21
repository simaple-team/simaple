import { PlayLogResponse } from "@/sdk/models";

export interface SkillStatistics {
  name: string;
  damageShare: number;
  totalDamage: number;
  damagePerSecond: number;
  useCount: number;
  damagePerUse: number;
  hitCount: number;
  averageDamagePerHit: number;
}

export type BattleStatistics = SkillStatistics[];

export function getBattleStatistics(logs: PlayLogResponse[]): BattleStatistics {
  const result: Record<string, SkillStatistics> = {};

  const damageRecords = logs.flatMap((log) => log.damage_records);
  const totalDamage = damageRecords.reduce(
    (acc, record) => acc + record.damage,
    0,
  );

  for (const record of damageRecords) {
    const skillName = record.name;

    if (!result[skillName]) {
      result[skillName] = {
        name: skillName,
        damageShare: 0,
        totalDamage: 0,
        damagePerSecond: 0,
        useCount: 0,
        damagePerUse: 0,
        hitCount: 0,
        averageDamagePerHit: 0,
      };
    }

    const statistics = result[skillName];

    statistics.totalDamage += record.damage;
    statistics.useCount += 1;
    statistics.hitCount += record.hit;
  }

  for (const skillName in result) {
    const statistics = result[skillName];
    statistics.damageShare = statistics.totalDamage / totalDamage;
    statistics.damagePerSecond =
      statistics.totalDamage / logs[logs.length - 1].clock;
    statistics.damagePerUse = statistics.totalDamage / statistics.useCount;
    statistics.averageDamagePerHit =
      statistics.totalDamage / statistics.hitCount;
  }

  return Object.values(result);
}

export function getCumulativeDamage(
  logs: PlayLogResponse[],
): { clock: number; damage: number }[] {
  return logs.map((log, index) => {
    return {
      clock: log.clock,
      damage: logs
        .slice(0, index + 1)
        .reduce((sum, log) => sum + log.total_damage, 0),
    };
  });
}

export function getIntervalDamage(
  logs: PlayLogResponse[],
  interval: number,
): { end: number; [skillName: string]: number }[] {
  const chunks: PlayLogResponse[][] = [];

  for (const playLog of logs) {
    while (playLog.clock >= interval * chunks.length) {
      chunks.push([]);
    }
    chunks[chunks.length - 1].push(playLog);
  }

  const data = chunks.map((chunk, index) => {
    const end = interval * (index + 1);
    const record: Record<string, number> = {};

    for (const playLog of chunk) {
      for (const damageRecord of playLog.damage_records) {
        if (!record[damageRecord.name]) {
          record[damageRecord.name] = 0;
        }
        record[damageRecord.name] += damageRecord.damage;
      }
    }

    return { end, ...record };
  });

  return data;
}

export function getSkillNamesDamageDesc(logs: PlayLogResponse[]) {
  const damageRecords = logs.flatMap((log) => log.damage_records);
  const record: Record<string, number> = {};

  for (const damageRecord of damageRecords) {
    const skillName = damageRecord.name;

    if (!record[skillName]) {
      record[skillName] = 0;
    }

    record[skillName] += damageRecord.damage;
  }

  return Object.entries(record)
    .sort(([, a], [, b]) => b - a)
    .map(([name]) => name);
}

export function getStack(logs: PlayLogResponse[], skillName: string) {
  return logs
    .filter((log, index) => log.clock !== logs[index + 1]?.clock)
    .map((log) => ({
      clock: log.clock,
      stack: log.running_view[skillName].stack!,
    }));
}

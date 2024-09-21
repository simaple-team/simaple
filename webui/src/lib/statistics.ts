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

export function getCumulativeDamage(
  logs: PlayLogResponse[],
): { clock: number; damage: number }[] {
  return logs.map((log, index) => {
    return {
      clock: log.clock,
      damage: logs
        .slice(0, index + 1)
        .reduce((sum, log) => sum + log.damage, 0),
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
      for (const damage of playLog.damages) {
        if (!record[damage.name]) {
          record[damage.name] = 0;
        }
        record[damage.name] += damage.damage;
      }
    }

    return { end, ...record };
  });

  return data;
}

export function getSkillNamesDamageDesc(logs: PlayLogResponse[]) {
  const damages = logs.flatMap((log) => log.damages);
  const record: Record<string, number> = {};

  for (const damage of damages) {
    const skillName = damage.name;

    if (!record[skillName]) {
      record[skillName] = 0;
    }

    record[skillName] += damage.damage;
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

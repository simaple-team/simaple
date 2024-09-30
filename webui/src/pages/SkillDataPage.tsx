import { SkillIcon } from "@/components/SkillIcon";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableRow } from "@/components/ui/table";
import { useSkillData } from "@/hooks/useSkillData";
import { SkillComponent, Stat } from "@/sdk/models";

interface SkillComponentExtra extends SkillComponent {
  cooldown_duration?: number;
  delay?: number;
  damage?: number;
  hit?: number;
  periodic_interval?: number;
  periodic_damage?: number;
  periodic_hit?: number;
  disable_validity?: boolean;
  stat?: Stat;
  modifier?: Stat;
  lasting_duration?: number;
  apply_buff_duration?: boolean;
  maximum_keydown_time?: number;
  keydown_prepare_delay?: number;
  keydown_end_delay?: number;
}

const STAT_NAMES: Record<keyof Stat, string> = {
  STR: "STR",
  DEX: "DEX",
  INT: "INT",
  LUK: "LUK",
  STR_multiplier: "STR%",
  DEX_multiplier: "DEX%",
  INT_multiplier: "INT%",
  LUK_multiplier: "LUK%",
  STR_static: "STR(고정)",
  DEX_static: "DEX(고정)",
  INT_static: "INT(고정)",
  LUK_static: "LUK(고정)",
  attack_power: "공격력",
  magic_attack: "마력",
  attack_power_multiplier: "공격력%",
  magic_attack_multiplier: "마력%",
  critical_rate: "크확",
  critical_damage: "크뎀",
  boss_damage_multiplier: "보공%",
  damage_multiplier: "데미지%",
  ignored_defence: "방무",
  elemental_resistance: "내성무시",
  final_damage_multiplier: "최종뎀%",
  MHP: "최대체력",
  MHP_multiplier: "최대체력%",
  MMP: "최대마력",
  MMP_multiplier: "최대마력%",
};

function formatStat(stat: Stat) {
  return (Object.entries(stat) as [keyof Stat, number][])
    .filter(([_, value]) => value !== 0)
    .map(([key, value]) => `${STAT_NAMES[key]}: ${value}`)
    .join("\n");
}

function isStat(value: unknown): value is Stat {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const result =
    Object.values(value).every((v) => typeof v === "number") &&
    "STR" in value &&
    "DEX" in value &&
    "INT" in value &&
    "LUK" in value;

  return result;
}

function SkillComponentCard(props: { skillComponent: SkillComponentExtra }) {
  const { skillComponent } = props;

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const {
    id,
    name,
    listening_actions,
    binds,
    cooldown_duration,
    delay,
    damage,
    hit,
    periodic_damage,
    periodic_hit,
    periodic_interval,
    stat,
    modifier,
    disable_validity,
    lasting_duration,
    apply_buff_duration,
    maximum_keydown_time,
    keydown_prepare_delay,
    keydown_end_delay,
    ...rest
  } = skillComponent;

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <span className="flex items-center gap-2">
            <SkillIcon name={name} />
            {name}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableBody>
            {listening_actions && Object.keys(listening_actions).length > 0 ? (
              <TableRow>
                <TableCell>트리거</TableCell>
                <TableCell className="whitespace-pre-wrap">
                  {JSON.stringify(listening_actions, null, 2)}
                </TableCell>
              </TableRow>
            ) : null}
            {cooldown_duration ? (
              <TableRow>
                <TableCell>쿨타임</TableCell>
                <TableCell>{cooldown_duration}ms</TableCell>
              </TableRow>
            ) : null}
            {delay ? (
              <TableRow>
                <TableCell>딜레이</TableCell>
                <TableCell>{delay}ms</TableCell>
              </TableRow>
            ) : null}
            {damage ? (
              <TableRow>
                <TableCell>데미지</TableCell>
                <TableCell>{damage}%</TableCell>
              </TableRow>
            ) : null}
            {hit ? (
              <TableRow>
                <TableCell>타수</TableCell>
                <TableCell>{hit}회</TableCell>
              </TableRow>
            ) : null}
            {periodic_interval ? (
              <TableRow>
                <TableCell>틱 간격</TableCell>
                <TableCell>{periodic_interval}ms</TableCell>
              </TableRow>
            ) : null}
            {periodic_damage ? (
              <TableRow>
                <TableCell>틱 데미지</TableCell>
                <TableCell>{periodic_damage}%</TableCell>
              </TableRow>
            ) : null}
            {periodic_hit ? (
              <TableRow>
                <TableCell>틱 타수</TableCell>
                <TableCell>{periodic_hit}회</TableCell>
              </TableRow>
            ) : null}
            {maximum_keydown_time ? (
              <TableRow>
                <TableCell>최대 키다운 시간</TableCell>
                <TableCell>{maximum_keydown_time}ms</TableCell>
              </TableRow>
            ) : null}
            {keydown_prepare_delay ? (
              <TableRow>
                <TableCell>키다운 준비 시간</TableCell>
                <TableCell>{keydown_prepare_delay}ms</TableCell>
              </TableRow>
            ) : null}
            {keydown_end_delay ? (
              <TableRow>
                <TableCell>키다운 종료 시간</TableCell>
                <TableCell>{keydown_end_delay}ms</TableCell>
              </TableRow>
            ) : null}
            {stat ? (
              <TableRow>
                <TableCell>스탯</TableCell>
                <TableCell className="whitespace-pre-wrap">
                  {formatStat(stat)}
                </TableCell>
              </TableRow>
            ) : null}
            {modifier ? (
              <TableRow>
                <TableCell>추가 스탯</TableCell>
                <TableCell className="whitespace-pre-wrap">
                  {formatStat(modifier)}
                </TableCell>
              </TableRow>
            ) : null}
            {disable_validity ? (
              <TableRow>
                <TableCell>직접 시전 불가</TableCell>
                <TableCell>예</TableCell>
              </TableRow>
            ) : null}
            {lasting_duration ? (
              <TableRow>
                <TableCell>지속 시간</TableCell>
                <TableCell>{lasting_duration}ms</TableCell>
              </TableRow>
            ) : null}
            {apply_buff_duration != null ? (
              <TableRow>
                <TableCell>벞지 적용</TableCell>
                <TableCell>{apply_buff_duration ? "예" : "아니오"}</TableCell>
              </TableRow>
            ) : null}
            {Object.entries(rest).map(([key, value]) => (
              <TableRow key={key}>
                <TableCell>{key}</TableCell>
                <TableCell className="whitespace-pre-wrap">
                  {isStat(value)
                    ? formatStat(value)
                    : JSON.stringify(value, null, 2)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

export function SkillDataPage() {
  const { skillComponents } = useSkillData();

  return (
    <div className="grow grid grid-cols-3 gap-2 p-4 overflow-y-scroll max-w-[1400px]">
      {skillComponents.map((skillComponent) => (
        <SkillComponentCard
          key={skillComponent.name}
          skillComponent={skillComponent}
        />
      ))}
    </div>
  );
}

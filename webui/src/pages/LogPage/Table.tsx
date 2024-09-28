import { SkillIcon } from "@/components/SkillIcon";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useWorkspace } from "@/hooks/useWorkspace";
import { damageFormatter, secFormatter } from "@/lib/formatters";
import { PlayLogResponse } from "@/sdk/models";
import { useMemo } from "react";

export const VadilityTable = ({ playLog }: { playLog: PlayLogResponse }) => {
  const { usedSkillNames } = useWorkspace();
  const { validity_view: validityView } = playLog;
  // 쿨이 돌고 있거나 사용한 적이 있는 스킬만 남기고, 노쿨 스킬은 제외한다.
  const skills = useMemo(
    () =>
      Object.entries(validityView).filter(
        (x) =>
          (x[1].time_left > 0 || usedSkillNames.includes(x[0])) &&
          x[1].cooldown_duration > 0,
      ),
    [validityView, usedSkillNames],
  );

  return (
    <Table>
      <TableHeader className="sticky top-0 bg-background">
        <TableRow>
          <TableHead>스킬명</TableHead>
          <TableHead>남은 쿨타임</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {skills.map(([key, value]) => (
          <TableRow key={key}>
            <TableCell>
              <div className="flex items-center gap-2">
                <SkillIcon name={key} />
                {key}
              </div>
            </TableCell>
            <TableCell>{secFormatter(value.time_left)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};

export const RunningTable = ({ playLog }: { playLog: PlayLogResponse }) => {
  const { running_view: runningView } = playLog;
  const runningSkills = useMemo(
    () =>
      Object.entries(runningView)
        .filter((x) => x[1].time_left > 0)
        .sort((a, b) => a[1].time_left - b[1].time_left),
    [runningView],
  );

  return (
    <Table>
      <TableHeader className="sticky top-0 bg-background">
        <TableRow>
          <TableHead>스킬명</TableHead>
          <TableHead>남은 지속시간</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {runningSkills.map(([key, value]) => (
          <TableRow key={key}>
            <TableCell>
              <div className="flex items-center gap-2">
                <SkillIcon name={key} />
                {key}
              </div>
            </TableCell>
            <TableCell>{secFormatter(value.time_left)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};

export const DamageTable = ({ playLog }: { playLog: PlayLogResponse }) => {
  const { damage_records: damageRecords } = playLog;
  const damages = useMemo(
    () => Object.values(damageRecords).sort((a, b) => a.damage - b.damage),
    [damageRecords],
  );

  return (
    <Table>
      <TableHeader className="sticky top-0 bg-background">
        <TableRow>
          <TableHead>스킬명</TableHead>
          <TableHead>데미지</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {damages.map(({ name, damage }, i) => (
          <TableRow key={i}>
            <TableCell>
              <div className="flex items-center gap-2">
                <SkillIcon name={name} />
                {name}
              </div>
            </TableCell>
            <TableCell>{damageFormatter(damage)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};

export const BuffTable = ({ playLog }: { playLog: PlayLogResponse }) => {
  return (
    <Table>
      <TableHeader className="sticky top-0 bg-background">
        <TableRow>
          <TableHead>스탯</TableHead>
          <TableHead>수치</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {Object.entries(playLog.buff_view).map(([key, value]) => (
          <TableRow key={key}>
            <TableCell>{key}</TableCell>
            <TableCell>{String(value)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};

export const EventTable = ({ playLog }: { playLog: PlayLogResponse }) => {
  return (
    <Table>
      <TableHeader className="sticky top-0 bg-background">
        <TableRow>
          <TableHead>태그</TableHead>
          <TableHead>이름</TableHead>
          <TableHead>핸들러</TableHead>
          <TableHead>메소드</TableHead>
          <TableHead>페이로드</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {playLog.events.map((event, i) => (
          <TableRow key={i}>
            <TableCell>{event.tag}</TableCell>
            <TableCell>{event.name}</TableCell>
            <TableCell>{event.handler}</TableCell>
            <TableCell>{event.method}</TableCell>
            <TableCell>
              <pre className="h-24 overflow-scroll">
                {JSON.stringify(event.payload, null, 2)}
              </pre>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};

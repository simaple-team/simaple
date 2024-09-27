import { SkillIcon } from "@/components/SkillIcon";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
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
import { cn } from "@/lib/utils";
import { PlayLogResponse } from "@/sdk/models";
import * as React from "react";
import { useEffect, useMemo, useState } from "react";
import { ErrorBoundary } from "react-error-boundary";

interface LogRowProps {
  playLog: PlayLogResponse;

  isSelected?: boolean;

  onSelect?: (playLog: PlayLogResponse) => void;
}

const LogRow = (props: LogRowProps) => {
  const { playLog, isSelected, onSelect } = props;

  const hasRejectedEvent = playLog.events.some(
    (event) => event.tag === "global.reject",
  );

  function handleClick() {
    onSelect?.(playLog);
  }

  return (
    <TableRow
      onClick={handleClick}
      className={cn(
        isSelected ? "bg-primary/10 hover:bg-primary/15" : "cursor-pointer",
        hasRejectedEvent && "bg-red-200",
      )}
    >
      <TableCell>{secFormatter(playLog.clock)}</TableCell>
      <TableCell>
        {playLog.action.method} {playLog.action.name}{" "}
        {playLog.action.payload ? JSON.stringify(playLog.action.payload) : ""}
      </TableCell>
      <TableCell>{damageFormatter(playLog.total_damage)}</TableCell>
    </TableRow>
  );
};

const VadilityTable = ({ playLog }: { playLog: PlayLogResponse }) => {
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
        <TableHead>스킬명</TableHead>
        <TableHead>남은 쿨타임</TableHead>
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

const RunningTable = ({ playLog }: { playLog: PlayLogResponse }) => {
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
        <TableHead>스킬명</TableHead>
        <TableHead>남은 지속시간</TableHead>
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

const DamageTable = ({ playLog }: { playLog: PlayLogResponse }) => {
  const { damage_records: damageRecords } = playLog;
  const damages = useMemo(
    () => Object.values(damageRecords).sort((a, b) => a.damage - b.damage),
    [damageRecords],
  );

  return (
    <Table>
      <TableHeader className="sticky top-0 bg-background">
        <TableHead>스킬명</TableHead>
        <TableHead>데미지</TableHead>
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

const BuffTable = ({ playLog }: { playLog: PlayLogResponse }) => {
  return (
    <Table>
      <TableHeader className="sticky top-0 bg-background">
        <TableHead>스탯</TableHead>
        <TableHead>수치</TableHead>
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

const EventTable = ({ playLog }: { playLog: PlayLogResponse }) => {
  return (
    <Table>
      <TableHeader className="sticky top-0 bg-background">
        <TableHead>태그</TableHead>
        <TableHead>이름</TableHead>
        <TableHead>핸들러</TableHead>
        <TableHead>메소드</TableHead>
        <TableHead>페이로드</TableHead>
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

const LogPage: React.FC = () => {
  const { history } = useWorkspace();
  const [selectedLog, setSelectedLog] = useState<PlayLogResponse | null>(null);
  const [currentView, setCurrentView] = useState<
    "validity" | "buff" | "running" | "events" | "damage"
  >("validity");
  const [autoSelectLast, setAutoSelectLast] = useState(true);

  useEffect(() => {
    if (autoSelectLast) {
      setSelectedLog(history[history.length - 1]);
    }
  }, [history, autoSelectLast]);

  const reversedHistory = useMemo(() => {
    return history.slice().reverse();
  }, [history]);

  return (
    <ErrorBoundary
      fallbackRender={({ error }) => <div>Error: {error.message}</div>}
    >
      <div className="flex flex-col overflow-scroll">
        <div className="py-2 px-4">
          <div className="flex items-center gap-1">
            <Checkbox
              id="autoSelectLast"
              checked={autoSelectLast}
              onCheckedChange={(x) => setAutoSelectLast(Boolean(x))}
            />
            <Label htmlFor="autoSelectLast" className="text-sm">
              계산 후 마지막 로그 자동 선택
            </Label>
          </div>
        </div>
        <div
          className={cn(
            "flex h-[calc(100%-3rem)] border-r border-t border-border/40 transition-all",
            currentView === "events" ? "max-w-[1600px]" : "max-w-[1200px]",
          )}
        >
          <div className="w-[600px] flex">
            <Table>
              <TableHeader className="sticky top-0 bg-background">
                <TableHead>시간</TableHead>
                <TableHead>행동</TableHead>
                <TableHead>데미지</TableHead>
              </TableHeader>
              <TableBody>
                {reversedHistory.map((playLog, i) => (
                  <LogRow
                    key={i}
                    playLog={playLog}
                    onSelect={setSelectedLog}
                    isSelected={selectedLog === playLog}
                  />
                ))}
              </TableBody>
            </Table>
          </div>
          {selectedLog ? (
            <div className="flex-grow flex h-full border-l border-border/40">
              {currentView === "validity" && (
                <VadilityTable playLog={selectedLog} />
              )}
              {currentView === "running" && (
                <RunningTable playLog={selectedLog} />
              )}
              {currentView === "damage" && (
                <DamageTable playLog={selectedLog} />
              )}
              {currentView === "buff" && <BuffTable playLog={selectedLog} />}
              {currentView === "events" && <EventTable playLog={selectedLog} />}
            </div>
          ) : (
            <div className="flex-grow p-4 flex items-center justify-center">
              <span>로그를 선택해주세요</span>
            </div>
          )}
          <div className="flex flex-col border-l border-border/40">
            <button
              className={`flex justify-center items-center px-4 h-20 ${
                currentView === "validity" ? "bg-primary/10" : ""
              }`}
              onClick={() => setCurrentView("validity")}
            >
              쿨타임
            </button>
            <button
              className={`flex justify-center items-center px-4 h-20 ${
                currentView === "running" ? "bg-primary/10" : ""
              }`}
              onClick={() => setCurrentView("running")}
            >
              지속
            </button>
            <button
              className={`flex justify-center items-center px-4 h-20 ${
                currentView === "damage" ? "bg-primary/10" : ""
              }`}
              onClick={() => setCurrentView("damage")}
            >
              데미지
            </button>
            <button
              className={`flex justify-center items-center px-4 h-20 ${
                currentView === "buff" ? "bg-primary/10" : ""
              }`}
              onClick={() => setCurrentView("buff")}
            >
              버프
            </button>
            <button
              className={`flex justify-center items-center px-4 h-20 ${
                currentView === "events" ? "bg-primary/10" : ""
              }`}
              onClick={() => setCurrentView("events")}
            >
              이벤트
            </button>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
};

export default LogPage;

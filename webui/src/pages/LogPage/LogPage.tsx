import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
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
import {
  BuffTable,
  DamageTable,
  EventTable,
  RunningTable,
  VadilityTable,
} from "./Table";

interface LogRowProps {
  playLog: PlayLogResponse & {
    hasRejectedEvent: boolean;
    hasHighlightedSkill: boolean;
  };

  isSelected?: boolean;

  onSelect?: (playLog: PlayLogResponse) => void;
}

const LogRow = (props: LogRowProps) => {
  const { playLog, isSelected, onSelect } = props;

  function handleClick() {
    onSelect?.(playLog);
  }

  return (
    <TableRow
      onClick={handleClick}
      className={cn(
        isSelected ? "bg-primary/10 hover:bg-primary/15" : "cursor-pointer",
        playLog.hasHighlightedSkill && "bg-blue-200",
        playLog.hasRejectedEvent && "bg-red-200",
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

const LogPage: React.FC = () => {
  const { history } = useWorkspace();
  const [selectedLog, setSelectedLog] = useState<PlayLogResponse | null>(null);
  const [currentView, setCurrentView] = useState<
    "validity" | "buff" | "running" | "events" | "damage"
  >("validity");
  const [autoSelectLast, setAutoSelectLast] = useState(true);
  const [skillNameHighlight, setSkillNameHighlight] = useState<string>("NONE");

  const damageEmittedSkillNames = useMemo(
    () =>
      history
        .flatMap((x) => x.damage_records.flatMap((y) => y.name))
        .filter((x, i, arr) => arr.indexOf(x) === i),
    [history],
  );

  const processedHistory = useMemo(() => {
    return history
      .slice()
      .reverse()
      .map((x) => {
        const hasHighlightedSkill = x.damage_records.some((y) =>
          y.name.includes(skillNameHighlight),
        );
        const hasRejectedEvent = x.events.some(
          (event) => event.tag === "global.reject",
        );
        return { ...x, hasHighlightedSkill, hasRejectedEvent };
      });
  }, [history, skillNameHighlight]);

  useEffect(() => {
    if (autoSelectLast) {
      setSelectedLog(history[history.length - 1]);
    }
  }, [history, autoSelectLast]);

  return (
    <ErrorBoundary
      fallbackRender={({ error }) => <div>Error: {error.message}</div>}
    >
      <div className="flex flex-col overflow-scroll">
        <div className="flex items-center py-2 px-4 gap-2">
          <div className="flex items-center gap-1">
            <Label className="text-sm">다음 스킬이 포함된 로그 강조:</Label>
            <Select
              value={skillNameHighlight}
              onValueChange={setSkillNameHighlight}
            >
              <SelectTrigger className="w-64">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={"NONE"}>없음</SelectItem>
                {damageEmittedSkillNames.map((skillName) => (
                  <SelectItem key={skillName} value={skillName}>
                    {skillName}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="border-r border-border/40 h-6" />
          <div className="flex items-center gap-1">
            <Switch
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
                <TableRow>
                  <TableHead>시간</TableHead>
                  <TableHead>행동</TableHead>
                  <TableHead>데미지</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {processedHistory.map((playLog, i) => (
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

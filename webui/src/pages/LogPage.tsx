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
import { useMemo, useState } from "react";
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
        isSelected ? "bg-primary/10" : "cursor-pointer",
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
  return (
    <Table>
      <TableHeader className="sticky top-0 bg-background">
        <TableHead>스킬명</TableHead>
        <TableHead>남은 쿨타임</TableHead>
      </TableHeader>
      <TableBody>
        {Object.entries(playLog.validity_view).map(([key, value]) => (
          <TableRow key={key}>
            <TableCell>{key}</TableCell>
            <TableCell>{secFormatter(value.time_left)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};

const RunningTable = ({ playLog }: { playLog: PlayLogResponse }) => {
  return (
    <Table>
      <TableHeader className="sticky top-0 bg-background">
        <TableHead>스킬명</TableHead>
        <TableHead>활성화</TableHead>
        <TableHead>남은 지속시간</TableHead>
      </TableHeader>
      <TableBody>
        {Object.entries(playLog.validity_view).map(([key, value]) => (
          <TableRow key={key}>
            <TableCell>{key}</TableCell>
            <TableCell>{value.valid ? "O" : "X"}</TableCell>
            <TableCell>{secFormatter(value.time_left)}</TableCell>
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
    "validity" | "buff" | "running" | "events"
  >("validity");

  const reversedHistory = useMemo(() => {
    return history.slice().reverse();
  }, [history]);

  return (
    <div
      className={cn(
        "flex h-[calc(100%-3rem)] border-r border-border/40 transition-all",
        currentView === "events" ? "max-w-[1600px]" : "max-w-[1200px]",
      )}
    >
      <ErrorBoundary
        fallbackRender={({ error }) => <div>Error: {error.message}</div>}
      >
        <div className="w-[600px] flex">
          <Table>
            <TableHeader className="sticky top-0 bg-background">
              <TableHead>시간</TableHead>
              <TableHead>행동</TableHead>
              <TableHead>데미지</TableHead>
            </TableHeader>
            <TableBody>
              {reversedHistory.map((playLog) => (
                <LogRow
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
      </ErrorBoundary>
    </div>
  );
};

export default LogPage;

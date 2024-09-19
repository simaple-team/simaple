import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useWorkspace } from "@/hooks/useWorkspace";
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

  function handleClick() {
    onSelect?.(playLog);
  }

  return (
    <TableRow
      onClick={handleClick}
      className={isSelected ? "bg-primary/10" : ""}
    >
      <TableCell>{playLog.clock}ms</TableCell>
      <TableCell>
        {playLog.action.method} {playLog.action.name}{" "}
        {playLog.action.payload ? JSON.stringify(playLog.action.payload) : ""}
      </TableCell>
      <TableCell>{Math.round(playLog.damage).toLocaleString()}</TableCell>
    </TableRow>
  );
};

interface LogDetailProps {
  playLog: PlayLogResponse;
}

const LogDetail = (props: LogDetailProps) => {
  const { playLog } = props;

  return (
    <Tabs defaultValue="cooldown" className="p-4 h-full">
      <TabsList>
        <TabsTrigger value="cooldown">쿨타임</TabsTrigger>
        <TabsTrigger value="running">지속시간</TabsTrigger>
        <TabsTrigger value="buff">적용된 버프</TabsTrigger>
      </TabsList>
      <div className="flex flex-col h-[calc(100vh-10rem)]">
        <ScrollArea>
          <TabsContent value="cooldown">
            <Table>
              <TableHeader>
                <TableHead>스킬명</TableHead>
                <TableHead>남은 쿨타임</TableHead>
              </TableHeader>
              <TableBody>
                {Object.entries(playLog.validity_view).map(([key, value]) => (
                  <TableRow key={key}>
                    <TableCell>{key}</TableCell>
                    <TableCell>{value.time_left}ms</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TabsContent>
          <TabsContent value="running">
            <Table>
              <TableHeader>
                <TableHead>스킬명</TableHead>
                <TableHead>활성화</TableHead>
                <TableHead>남은 지속시간</TableHead>
              </TableHeader>
              <TableBody>
                {Object.entries(playLog.validity_view).map(([key, value]) => (
                  <TableRow key={key}>
                    <TableCell>{key}</TableCell>
                    <TableCell>{value.valid ? "O" : "X"}</TableCell>
                    <TableCell>{value.time_left}ms</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TabsContent>
          <TabsContent value="buff">
            <Table>
              <TableHeader>
                <TableHead>스탯</TableHead>
                <TableHead>수치</TableHead>
              </TableHeader>
              <TableBody>
                {Object.entries(playLog.buff_view).map(([key, value]) => (
                  <TableRow key={key}>
                    <TableCell>{key}</TableCell>
                    <TableCell>{value}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TabsContent>
        </ScrollArea>
      </div>
    </Tabs>
  );
};

const LogPage: React.FC = () => {
  const { history } = useWorkspace();
  const [selectedLog, setSelectedLog] = useState<PlayLogResponse | null>(null);

  const reversedHistory = useMemo(() => {
    return history.slice().reverse();
  }, [history]);

  return (
    <div className="grow grid grid-cols-2 h-[calc(100%-3rem)]">
      <ErrorBoundary
        fallbackRender={({ error }) => <div>Error: {error.message}</div>}
      >
        {selectedLog ? <LogDetail playLog={selectedLog} /> : <div />}
        <Table>
          <TableHeader>
            <TableHead>시간</TableHead>
            <TableHead>행동</TableHead>
            <TableHead>데미지</TableHead>
          </TableHeader>
          <TableBody>
            {reversedHistory.map((playLog) => (
              <LogRow
                key={playLog.hash}
                playLog={playLog}
                onSelect={setSelectedLog}
                isSelected={selectedLog === playLog}
              />
            ))}
          </TableBody>
        </Table>
      </ErrorBoundary>
    </div>
  );
};

export default LogPage;

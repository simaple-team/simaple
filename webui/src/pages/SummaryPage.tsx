import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useWorkspace } from "@/hooks/useWorkspace";
import { damageFormatter, percentageFormatter } from "@/lib/formatters";
import { getBattleStatistics } from "@/statistics";
import { useMemo, useState } from "react";
import { ErrorBoundary } from "react-error-boundary";

export function SummaryPage() {
  const { history } = useWorkspace();
  const [sortBy, setSortBy] = useState("totalDamage");
  const [order, setOrder] = useState("desc");

  const battleStats = useMemo(() => getBattleStatistics(history), [history]);
  const sortedBattleStats = useMemo(
    () =>
      battleStats.slice().sort((a, b) => {
        if (sortBy === "totalDamage") {
          return order === "asc"
            ? a.totalDamage - b.totalDamage
            : b.totalDamage - a.totalDamage;
        } else if (sortBy === "useCount") {
          return order === "asc"
            ? a.useCount - b.useCount
            : b.useCount - a.useCount;
        }
        return 0;
      }),
    [battleStats, sortBy, order],
  );

  return (
    <div className="grow p-4">
      <ErrorBoundary
        fallbackRender={({ error }) => <div>Error: {error.message}</div>}
      >
        <div className="flex items-center gap-2">
          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="w-60">
              <SelectValue placeholder="정렬 기준" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="totalDamage">누적 데미지 정렬</SelectItem>
              <SelectItem value="useCount">사용횟수 정렬</SelectItem>
            </SelectContent>
          </Select>
          <Select value={order} onValueChange={setOrder}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="순서" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="desc">내림차순</SelectItem>
              <SelectItem value="asc">오름차순</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <Table className="max-w-screen-lg">
          <TableHeader>
            <TableHead>스킬</TableHead>
            <TableHead>누적 데미지</TableHead>
            <TableHead>데미지 점유율</TableHead>
            <TableHead>평균 데미지 (초당)</TableHead>
            <TableHead>사용횟수</TableHead>
            <TableHead>평균 데미지 (1회당)</TableHead>
          </TableHeader>
          <TableBody>
            {sortedBattleStats.map((stats, index) => (
              <TableRow
                key={stats.name}
                className={index % 2 === 0 ? "bg-gray-100" : ""}
              >
                <TableCell>{stats.name}</TableCell>
                <TableCell>{damageFormatter(stats.totalDamage)}</TableCell>
                <TableCell>{percentageFormatter(stats.damageShare)}</TableCell>
                <TableCell>{damageFormatter(stats.damagePerSecond)}</TableCell>
                <TableCell>{stats.useCount}회</TableCell>
                <TableCell>{damageFormatter(stats.damagePerUse)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </ErrorBoundary>
    </div>
  );
}

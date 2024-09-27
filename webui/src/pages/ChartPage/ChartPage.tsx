import { CumulativeDamageChart } from "@/pages/ChartPage/CumulativeDamageChart";
import { IntervalDamageChart } from "@/pages/ChartPage/IntervalDamageChart";
import { StackChart } from "@/pages/ChartPage/StackChart";
import UptimeChart from "@/pages/ChartPage/UptimeChart";
import { useWorkspace } from "@/hooks/useWorkspace";
import * as React from "react";
import { ErrorBoundary } from "react-error-boundary";

const ChartPage: React.FC = () => {
  const { history } = useWorkspace();

  if (history.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        데이터가 없습니다.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 p-4 grow overflow-y-scroll">
      <ErrorBoundary
        fallbackRender={({ error }) => <div>Error: {error.message}</div>}
      >
        <CumulativeDamageChart />
        <IntervalDamageChart />
        <UptimeChart />
        <StackChart />
      </ErrorBoundary>
    </div>
  );
};

export default ChartPage;

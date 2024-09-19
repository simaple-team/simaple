import { usePreference } from "@/hooks/usePreference";
import { useWorkspace } from "@/hooks/useWorkspace";
import * as React from "react";
import { ErrorBoundary } from "react-error-boundary";
import Chart from "../components/Chart";

const ChartPage: React.FC = () => {
  const { history } = useWorkspace();
  const { chartSetting } = usePreference();

  return (
    <div className="grow">
      <ErrorBoundary
        fallbackRender={({ error }) => <div>Error: {error.message}</div>}
      >
        <Chart
          key={JSON.stringify(chartSetting)}
          history={history}
          setting={chartSetting}
        />
      </ErrorBoundary>
    </div>
  );
};

export default ChartPage;

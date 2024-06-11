import * as React from "react";
import Chart from "../components/Chart";
import { usePreference } from "../hooks/usePreference";
import { useWorkspace } from "../hooks/useWorkspace";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

const Editor: React.FC = () => {
  const { history, playLog, run } = useWorkspace();
  const { chartSetting } = usePreference();
  const [plan, setPlan] = React.useState("");

  if (!playLog) {
    return <></>;
  }

  function handleRun() {
    run(plan);
  }

  return (
    <div className="flex">
      <div className="flex flex-col w-[520px] p-4 gap-2">
        <Textarea
          spellCheck={false}
          className="grow"
          value={plan}
          onChange={(e) => setPlan(e.currentTarget.value)}
        />
        <Button onClick={handleRun}>Calculate</Button>
      </div>
      <div className="grow">
        <Chart history={history} setting={chartSetting} />
      </div>
    </div>
  );
};

export default Editor;

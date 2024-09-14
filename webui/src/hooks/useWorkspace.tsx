import { BaselineConfiguration, PlayLog } from "@/sdk/models";
import * as React from "react";
import { usePySimaple } from "./useSimaple";

type WorkspaceProviderProps = { children: React.ReactNode };

function useWorkspaceState() {
  const { pySimaple, uow, syncFs } = usePySimaple();

  const [currentSimulatorId, setCurrentSimulatorId] = React.useState<string>();
  const [history, setHistory] = React.useState<PlayLog[]>([]);
  const playLog = history[history.length - 1];

  const skillNames = React.useMemo(
    () => (playLog ? Object.keys(playLog.validity_view) : []),
    [playLog],
  );

  function updateSimulatorId(id: string) {
    setCurrentSimulatorId(id);

    const logs = pySimaple.getAllLogs(id, uow);
    setHistory(logs.flatMap((log) => log.logs));
  }

  async function createBaselineSimulator(configuration: BaselineConfiguration) {
    const id = pySimaple.createSimulatorFromBaseline(configuration, uow);

    updateSimulatorId(id);
    await syncFs();
  }

  function loadSimulator(id: string) {
    updateSimulatorId(id);
  }

  function run(plan: string) {
    if (!currentSimulatorId) {
      return;
    }

    const logs = pySimaple.runSimulatorWithPlan(currentSimulatorId, plan, uow);
    setHistory(logs.flatMap((log) => log.logs));
  }

  return {
    currentSimulatorId,
    history,
    playLog,
    skillNames,
    createBaselineSimulator,
    loadSimulator,
    run,
  };
}

const WorkspaceStateContext = React.createContext<
  ReturnType<typeof useWorkspaceState> | undefined
>(undefined);

function WorkspaceProvider({ children }: WorkspaceProviderProps) {
  const value = useWorkspaceState();

  return (
    <WorkspaceStateContext.Provider value={value}>
      {children}
    </WorkspaceStateContext.Provider>
  );
}

function useWorkspace() {
  const context = React.useContext(WorkspaceStateContext);
  if (context === undefined) {
    throw new Error("useWorkspace must be used within a WorkspaceProvider");
  }
  return context;
}

export { useWorkspace, WorkspaceProvider };

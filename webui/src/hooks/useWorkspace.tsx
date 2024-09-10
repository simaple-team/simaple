import {
  BaselineConfiguration,
  PlayLog,
  SimulatorResponse,
} from "@/sdk/models";
import * as React from "react";
import { usePySimaple } from "./useSimaple";

type WorkspaceProviderProps = { children: React.ReactNode };

function useWorkspaceState() {
  const { pySimaple, uow } = usePySimaple();

  const [currentSimulatorId, setCurrentSimulatorId] = React.useState<string>();
  const [simulators, setSimulators] = React.useState<SimulatorResponse[]>([]);
  const [history, setHistory] = React.useState<PlayLog[]>([]);
  const playLog = history[history.length - 1];

  React.useLayoutEffect(() => {
    getAllSimulators();
  }, []);

  function updateSimulatorId(id: string) {
    setCurrentSimulatorId(id);

    const logs = pySimaple.getAllLogs(id, uow);
    setHistory(logs.flatMap((log) => log.logs));
  }

  function getAllSimulators() {
    setSimulators(pySimaple.queryAllSimulator(uow));
  }

  function createBaselineSimulator(configuration: BaselineConfiguration) {
    const id = pySimaple.createSimulatorFromBaseline(configuration, uow);

    updateSimulatorId(id);
    getAllSimulators();
  }

  function loadSimulator(id: string) {
    updateSimulatorId(id);
    getAllSimulators();
  }

  function run(plan: string) {
    if (!currentSimulatorId) {
      return;
    }

    const logs = pySimaple.runSimulatorWithPlan(currentSimulatorId, plan, uow);
    setHistory(logs.flatMap((log) => log.logs));
  }

  return {
    simulators,
    currentSimulatorId,
    history,
    playLog,
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

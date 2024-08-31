import {
  BaselineConfiguration,
  MinimalSimulatorConfiguration,
  PlayLog,
  SimulatorResponse,
} from "@/sdk/models";
import * as React from "react";
import { sdk } from "../sdk";

type WorkspaceProviderProps = { children: React.ReactNode };

function useWorkspaceState() {
  const [currentSimulatorId, setCurrentSimulatorId] = React.useState<string>();
  const [simulators, setSimulators] = React.useState<SimulatorResponse[]>([]);
  const [history, setHistory] = React.useState<PlayLog[]>([]);
  const playLog = history[history.length - 1];

  React.useLayoutEffect(() => {
    getAllSimulators();
  }, []);

  async function updateSimulatorId(id: string) {
    setCurrentSimulatorId(id);

    const logs = await sdk.getLogs(id);
    setHistory(logs.flatMap((log) => log.logs));
  }

  async function getAllSimulators() {
    await sdk.getAllSimulators().then((res) => setSimulators(res));
    return;
  }

  async function createMinimalSimulator(
    configuration: MinimalSimulatorConfiguration,
  ) {
    const simulator = await sdk.createMinimalSimulator(configuration);

    await updateSimulatorId(simulator.id);
    await getAllSimulators();
  }

  async function createBaselineSimulator(configuration: BaselineConfiguration) {
    await sdk.initializeConfiguration();
    const simulator = await sdk.createBaselineSimulator(configuration);

    await updateSimulatorId(simulator.id);
    await getAllSimulators();
  }

  async function loadSimulator(id: string) {
    await updateSimulatorId(id);
    await getAllSimulators();
  }

  async function run(plan: string) {
    if (!currentSimulatorId) {
      return;
    }

    const logs = await sdk.run(currentSimulatorId, { plan });
    setHistory(logs.flatMap((log) => log.logs));
  }

  return {
    simulators,
    currentSimulatorId,
    history,
    playLog,
    createMinimalSimulator,
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

export { WorkspaceProvider, useWorkspace };

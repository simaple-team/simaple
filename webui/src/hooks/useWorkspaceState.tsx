import { PlayLog } from "@/sdk/models";
import * as React from "react";
import { usePySimaple } from "./useSimaple";

type WorkspaceProviderProps = { children: React.ReactNode };

function useWorkspaceState() {
  const { pySimaple } = usePySimaple();

  const [plan, setPlan] = React.useState<string>("");
  const [simulationEnvironment, setSimulationEnvironment] =
    React.useState<Record<string, unknown>>();
  const [history, setHistory] = React.useState<PlayLog[]>([]);
  const playLog = history[history.length - 1];

  const skillNames = React.useMemo(
    () => (playLog ? Object.keys(playLog.validity_view) : []),
    [playLog],
  );

  const run = React.useCallback(() => {
    const provider =
    simulationEnvironment ??
      pySimaple.computeSimulationEnvironmentFromProvider(plan);

    if (!simulationEnvironment) {
      setSimulationEnvironment(provider);
    }

    const logs = pySimaple.run(plan, provider);
    setHistory(logs.flatMap((log) => log.logs));
  }, [pySimaple, simulationEnvironment, plan]);

  const runAsync = React.useCallback(() => {
    return new Promise<void>((resolve) => {
      setTimeout(() => {
        run();
        resolve();
      }, 0);
    });
  }, [run]);

  return {
    plan,
    setPlan,
    history,
    playLog,
    skillNames,
    run,
    runAsync,
  };
}

export const WorkspaceStateContext = React.createContext<
  ReturnType<typeof useWorkspaceState> | undefined
>(undefined);

export function WorkspaceProvider({ children }: WorkspaceProviderProps) {
  const value = useWorkspaceState();

  return (
    <WorkspaceStateContext.Provider value={value}>
      {children}
    </WorkspaceStateContext.Provider>
  );
}

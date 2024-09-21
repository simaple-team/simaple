import { PlayLogResponse } from "@/sdk/models";
import * as React from "react";
import { usePySimaple } from "./useSimaple";
import { useLocalStorageValue } from "@react-hookz/web";

type WorkspaceProviderProps = { children: React.ReactNode };

function useWorkspaceState() {
  const { pySimaple } = usePySimaple();

  const { value: storedWorkspace, set: setWorkspace } = useLocalStorageValue<{
    plan: string;
  }>("workspace");

  const [plan, setPlan] = React.useState<string>(storedWorkspace?.plan ?? "");
  const [history, setHistory] = React.useState<PlayLogResponse[]>([]);

  const playLog = history[history.length - 1];
  const skillNames = React.useMemo(
    () => (playLog ? Object.keys(playLog.validity_view) : []),
    [playLog],
  );

  React.useEffect(() => {
    setWorkspace({ plan });
  }, [plan, setWorkspace]);

  const run = React.useCallback(() => {
    const isEnvironmentProvided = pySimaple.hasEnvironment(plan);
    const planToRun = isEnvironmentProvided
      ? plan
      : pySimaple.provideEnvironmentAugmentedPlan(plan);

    if (!isEnvironmentProvided) {
      setPlan(planToRun);
    }

    const logs = pySimaple.runPlan(planToRun);
    setHistory(logs.flatMap((log) => log.logs));
  }, [pySimaple, plan]);

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

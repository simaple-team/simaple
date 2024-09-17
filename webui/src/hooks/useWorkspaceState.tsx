import { PlayLog } from "@/sdk/models";
import * as React from "react";
import { usePySimaple } from "./useSimaple";

type WorkspaceProviderProps = { children: React.ReactNode };

function useWorkspaceState() {
  const { pySimaple } = usePySimaple();

  const [plan, setPlan] = React.useState<string>("");
  const [serializedCharacterProvider, setSerializedCharacterProvider] =
    React.useState<Record<string, unknown>>();
  const [history, setHistory] = React.useState<PlayLog[]>([]);
  const playLog = history[history.length - 1];

  const skillNames = React.useMemo(
    () => (playLog ? Object.keys(playLog.validity_view) : []),
    [playLog],
  );

  const run = React.useCallback(() => {
    const provider =
      serializedCharacterProvider ??
      pySimaple.getSerializedCharacterProvider(plan);

    if (!serializedCharacterProvider) {
      setSerializedCharacterProvider(provider);
    }

    const logs = pySimaple.run(plan, provider);
    setHistory(logs.flatMap((log) => log.logs));
  }, [pySimaple, serializedCharacterProvider, plan]);

  return {
    plan,
    setPlan,
    history,
    playLog,
    skillNames,
    run,
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

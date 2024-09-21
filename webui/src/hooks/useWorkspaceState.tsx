import {
  BaselineEnvironmentProvider,
  PlayLogResponse,
  SkillComponent,
} from "@/sdk/models";
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
  const [skillComponents, setSkillComponents] = React.useState<
    SkillComponent[]
  >([]);

  const playLog = history[history.length - 1];
  const skillNames = React.useMemo(
    () => (playLog ? Object.keys(playLog.validity_view) : []),
    [playLog],
  );

  const skillComponentMap = React.useMemo(
    () =>
      skillComponents.reduce(
        (acc, component) => {
          acc[component.name] = component;
          return acc;
        },
        {} as Record<string, SkillComponent>,
      ),
    [skillComponents],
  );

  React.useEffect(() => {
    setWorkspace({ plan });
  }, [plan, setWorkspace]);

  React.useEffect(() => {
    const components = pySimaple.getAllComponent();
    setSkillComponents(components);
  }, [pySimaple]);

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

  const getIconPath = React.useCallback(
    (skillName: string) => {
      const component = skillComponentMap[skillName];
      return `/icons/${component?.id.split("-")[0]}.png`;
    },
    [skillComponentMap],
  );

  const getInitialPlanFromBaselineEnvironment = React.useCallback(
    (baseline: BaselineEnvironmentProvider) => {
      return pySimaple.getInitialPlanFromBaselineEnvironment(baseline);
    },
    [pySimaple],
  );

  return {
    plan,
    setPlan,
    history,
    skillNames,
    run,
    runAsync,
    getIconPath,
    getInitialPlanFromBaselineEnvironment,
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

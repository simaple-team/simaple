import {
  BaselineEnvironmentProvider,
  OperationLogResponse,
  SkillComponent,
} from "@/sdk/models";
import { useLocalStorageValue } from "@react-hookz/web";
import * as React from "react";
import { useEffect, useMemo, useState } from "react";
import { usePySimaple } from "./useSimaple";
import { usePreference } from "./usePreference";

type WorkspaceProviderProps = { children: React.ReactNode };

function useWorkspaceState() {
  const { pySimaple } = usePySimaple();
  const { preferences } = usePreference();

  const { value: storedWorkspace, set: setWorkspace } = useLocalStorageValue<{
    plan: string;
  }>("workspace");

  const [plan, setPlan] = React.useState<string>(storedWorkspace?.plan ?? "");
  const [operationLogs, setOperationLogs] = React.useState<
    OperationLogResponse[]
  >([]);
  const [skillComponents, setSkillComponents] = React.useState<
    SkillComponent[]
  >([]);
  const [errorMessage, setErrorMessage] = React.useState("");

  const playLog = operationLogs[operationLogs.length - 1]?.logs[0];
  const skillNames = React.useMemo(
    () => (playLog ? Object.keys(playLog.validity_view) : []),
    [playLog],
  );

  const unfilteredHistory = React.useMemo(
    () =>
      operationLogs
        .flatMap((x) => x.logs)
        .map((x) => ({
          ...x,
          clock: x.clock - preferences.startClock,
        })),
    [operationLogs],
  );
  const history = React.useMemo(
    () =>
      unfilteredHistory.filter(
        (x) =>
          x.clock >= 0 &&
          (preferences.duration === null || x.clock <= preferences.duration),
      ),
    [unfilteredHistory, preferences],
  );
  const usedSkillNames = useMemo(
    () =>
      skillNames.filter((name) =>
        history.some((log) =>
          log.events.find(
            (event) => event.name === name && event.method === "use",
          ),
        ),
      ),
    [skillNames, history],
  );

  const skillComponentMap = useMemo(
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

  useEffect(() => {
    setWorkspace({ plan });
  }, [plan, setWorkspace]);

  useEffect(() => {
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

    const result = pySimaple.runPlan(planToRun);

    if (!result.success) {
      setErrorMessage(result.message);
      return;
    }
    setOperationLogs(result.data);
  }, [pySimaple, plan]);

  const runAsync = React.useCallback(() => {
    return new Promise<void>((resolve, reject) => {
      setTimeout(() => {
        try {
          run();
          resolve();
        } catch (error) {
          reject(error);
        }
      }, 0);
    });
  }, [run]);

  const clearErrorMessage = React.useCallback(() => {
    setErrorMessage("");
  }, []);

  const getIconPath = React.useCallback(
    (skillName: string) => {
      const component = skillComponentMap[skillName];
      return `/icons/${component?.id.split("-")[0]}.png`;
    },
    [skillComponentMap],
  );

  const getInitialPlanFromBaseline = React.useCallback(
    (baseline: BaselineEnvironmentProvider) => {
      return pySimaple.getInitialPlanFromBaseline(baseline);
    },
    [pySimaple],
  );

  return {
    plan,
    setPlan,
    unfilteredHistory,
    history,
    playLog,
    skillNames,
    usedSkillNames,
    errorMessage,
    clearErrorMessage,
    run,
    runAsync,
    getIconPath,
    getInitialPlanFromBaseline,
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

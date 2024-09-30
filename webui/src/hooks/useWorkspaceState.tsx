import {
  BaselineEnvironmentProvider,
  OperationLogResponse,
} from "@/sdk/models";
import { useLocalStorageValue } from "@react-hookz/web";
import * as React from "react";
import { useEffect, useMemo } from "react";
import { usePreference } from "./usePreference";
import { usePySimaple } from "./useSimaple";

type WorkspaceProviderProps = { children: React.ReactNode };

function useWorkspaceState() {
  const { pySimaple } = usePySimaple();
  const { preferences } = usePreference();

  const { value: storedWorkspace, set: setWorkspace } = useLocalStorageValue<{
    plan: string;
  }>("workspace");

  const [plan, setPlan] = React.useState<string>(storedWorkspace?.plan ?? "");
  const [submittedPlan, setSubmittedPlan] = React.useState<string>("");
  const [operationLogs, setOperationLogs] = React.useState<
    OperationLogResponse[]
  >([]);
  const [errorMessage, setErrorMessage] = React.useState("");

  const unfilteredHistory = React.useMemo(
    () =>
      operationLogs
        .flatMap((x) => x.logs)
        .map((x) => ({
          ...x,
          clock: x.clock - preferences.startClock,
        })),
    [operationLogs, preferences.startClock],
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

  const skillNames = React.useMemo(
    () =>
      unfilteredHistory[0]
        ? Object.keys(unfilteredHistory[0].validity_view)
        : [],
    [unfilteredHistory],
  );
  const usedSkillNames = useMemo(
    () =>
      skillNames.filter((name) =>
        unfilteredHistory.some((log) =>
          log.events.find(
            (event) => event.name === name && event.method === "use",
          ),
        ),
      ),
    [skillNames, unfilteredHistory],
  );

  useEffect(() => {
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

    const result = pySimaple.runPlan(planToRun);

    console.log(result);

    if (!result.success) {
      setErrorMessage(result.message);
      return;
    }
    setSubmittedPlan(planToRun);
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

  const getInitialPlanFromBaseline = React.useCallback(
    (baseline: BaselineEnvironmentProvider) => {
      return pySimaple.getInitialPlanFromBaseline(baseline);
    },
    [pySimaple],
  );

  return {
    plan,
    setPlan,
    submittedPlan,
    unfilteredHistory,
    history,
    skillNames,
    usedSkillNames,
    errorMessage,
    clearErrorMessage,
    run,
    runAsync,
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

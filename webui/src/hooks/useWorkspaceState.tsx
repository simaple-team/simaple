import { pySimaple } from "@/sdk";
import { OperationLogResponse } from "@/sdk/models";
import { useLocalStorageValue } from "@react-hookz/web";
import { ok } from "neverthrow";
import * as React from "react";
import { useEffect, useMemo } from "react";
import { match } from "ts-pattern";
import { usePreference } from "./usePreference";

type WorkspaceProviderProps = { children: React.ReactNode };

function useWorkspaceState() {
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

  const run = React.useCallback(async () => {
    return pySimaple
      .hasEnvironment(plan)
      .andThen((hasEnv) => {
        return match(hasEnv)
          .with(true, () => ok(plan))
          .with(false, () =>
            pySimaple.provideEnvironmentAugmentedPlan(plan).andTee(setPlan),
          )
          .exhaustive();
      })
      .andThen((augmentedPlan) =>
        match(submittedPlan)
          .with("", () => pySimaple.runPlan(augmentedPlan))
          .otherwise(() =>
            pySimaple.runPlanWithHint(
              submittedPlan,
              operationLogs,
              augmentedPlan,
            ),
          )
          .andTee(() => setSubmittedPlan(augmentedPlan)),
      )
      .match(setOperationLogs, setErrorMessage);
  }, [plan, submittedPlan, operationLogs]);

  const clearErrorMessage = React.useCallback(() => {
    setErrorMessage("");
  }, []);

  const getInitialPlanFromMetadata = React.useCallback(
    (metadata: Parameters<typeof pySimaple.getInitialPlanFromMetadata>[0]) => {
      return pySimaple.getInitialPlanFromMetadata(metadata);
    },
    [],
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
    getInitialPlanFromMetadata,
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

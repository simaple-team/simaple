import { pySimaple } from "@/sdk";
import { SkillComponent } from "@/sdk/models";
import * as React from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useWorkspace } from "./useWorkspace";

type SkillDataProviderProps = { children: React.ReactNode };

function useSkillDataState() {
  const { submittedPlan } = useWorkspace();

  const [skillComponents, setSkillComponents] = useState<SkillComponent[]>([]);

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
    if (!pySimaple || !submittedPlan) {
      return;
    }

    async function run() {
      const result = await pySimaple.getAllComponent(submittedPlan);

      if (!result.success) {
        console.error(result.message);
        return;
      }

      setSkillComponents(result.data);
    }
    run();
  }, [submittedPlan]);

  const getIconPath = useCallback(
    (skillName: string) => {
      const component = skillComponentMap[skillName];
      return `/icons/${component?.id.split("-")[0]}.png`;
    },
    [skillComponentMap],
  );

  return {
    getIconPath,
    skillComponents,
  };
}

const SkillDataStateContext = React.createContext<
  ReturnType<typeof useSkillDataState> | undefined
>(undefined);

function SkillDataProvider({ children }: SkillDataProviderProps) {
  const value = useSkillDataState();

  return (
    <SkillDataStateContext.Provider value={value}>
      {children}
    </SkillDataStateContext.Provider>
  );
}

function useSkillData() {
  const context = React.useContext(SkillDataStateContext);
  if (context === undefined) {
    throw new Error("useSkillData must be used within a SkillDataProvider");
  }
  return context;
}

export { SkillDataProvider, useSkillData };

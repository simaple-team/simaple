import { SkillComponent } from "@/sdk/models";
import * as React from "react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { usePySimaple } from "./useSimaple";

type SkillDataProviderProps = { children: React.ReactNode };

function useSkillDataState() {
  const { pySimaple } = usePySimaple();

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
    const components = pySimaple.getAllComponent();
    setSkillComponents(components);
  }, [pySimaple]);

  const getIconPath = useCallback(
    (skillName: string) => {
      const component = skillComponentMap[skillName];
      return `/icons/${component?.id.split("-")[0]}.png`;
    },
    [skillComponentMap],
  );

  return {
    getIconPath,
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

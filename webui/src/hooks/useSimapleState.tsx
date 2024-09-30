import { pySimaple as _pySimaple } from "@/sdk";
import * as React from "react";
import { PySimaple } from "../sdk";

type PySimapleProviderProps = { children: React.ReactNode };

function usePySimapleState() {
  const [isLoading, setIsLoading] = React.useState(false);
  const [pySimaple, setPySimaple] = React.useState<PySimaple>();

  const isLoaded = React.useMemo(() => !!pySimaple, [pySimaple]);

  async function load() {
    try {
      setIsLoading(true);

      setPySimaple(_pySimaple);
    } finally {
      setIsLoading(false);
    }
  }

  return {
    pySimaple,
    isLoading,
    isLoaded,
    load,
  };
}

export const PySimapleStateContext = React.createContext<
  ReturnType<typeof usePySimapleState> | undefined
>(undefined);

export function PySimapleProvider({ children }: PySimapleProviderProps) {
  const value = usePySimapleState();

  return (
    <PySimapleStateContext.Provider value={value}>
      {children}
    </PySimapleStateContext.Provider>
  );
}

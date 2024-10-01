import * as React from "react";
import { pySimaple } from "../sdk";

type PySimapleProviderProps = { children: React.ReactNode };

function usePySimapleState() {
  const [isLoading, setIsLoading] = React.useState(false);
  const [isLoaded, setIsLoaded] = React.useState(false);

  async function load() {
    try {
      setIsLoading(true);

      await pySimaple.ready();

      setIsLoaded(true);
    } finally {
      setIsLoading(false);
    }
  }

  return {
    isLoading,
    isLoaded,
    load,
  };
}

const PySimapleStateContext = React.createContext<
  ReturnType<typeof usePySimapleState> | undefined
>(undefined);

function PySimapleProvider({ children }: PySimapleProviderProps) {
  const value = usePySimapleState();

  return (
    <PySimapleStateContext.Provider value={value}>
      {children}
    </PySimapleStateContext.Provider>
  );
}

function usePySimaple() {
  const context = React.useContext(PySimapleStateContext);
  if (context === undefined) {
    throw new Error("usePySimaple must be used within a PySimapleProvider");
  }
  return context;
}

export { PySimapleProvider, usePySimaple };

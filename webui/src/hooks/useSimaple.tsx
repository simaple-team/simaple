import * as React from "react";
import { loadPySimaple, PySimaple, PySimapleUow } from "../sdk";

type PySimapleProviderProps = { children: React.ReactNode };

function usePySimapleState() {
  const [isLoading, setIsLoading] = React.useState(false);
  const [pySimaple, setPySimaple] = React.useState<PySimaple>();
  const [uow, setUow] = React.useState<PySimapleUow>();

  const isLoaded = React.useMemo(() => !!pySimaple, [pySimaple]);

  async function load() {
    try {
      const handle = await window.showDirectoryPicker();
      setIsLoading(true);

      const pySimaple = await loadPySimaple({ fileSystemHandle: handle });

      setPySimaple(pySimaple);
      setUow(pySimaple.createUow());
    } finally {
      setIsLoading(false);
    }
  }

  return {
    pySimaple,
    uow,
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

function usePySimapleBeforeLoad() {
  const context = React.useContext(PySimapleStateContext);
  if (context === undefined) {
    throw new Error("usePySimaple must be used within a PySimapleProvider");
  }
  return context as ReturnType<typeof usePySimapleState>;
}

function usePySimaple() {
  const context = React.useContext(PySimapleStateContext);
  if (context === undefined) {
    throw new Error("usePySimaple must be used within a PySimapleProvider");
  }
  if (!context.pySimaple) {
    throw new Error("PySimaple is not loaded");
  }
  return context as ReturnType<typeof usePySimapleState> & {
    pySimaple: PySimaple;
    uow: PySimapleUow;
  };
}

export { PySimapleProvider, usePySimapleBeforeLoad, usePySimaple };

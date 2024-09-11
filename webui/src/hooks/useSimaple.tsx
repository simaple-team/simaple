import * as React from "react";
import { loadPySimaple, PySimaple, PySimapleUow } from "../sdk";

type PySimapleProviderProps = { children: React.ReactNode };

function usePySimapleState() {
  const [isLoading, setIsLoading] = React.useState(false);
  const [pySimaple, setPySimaple] = React.useState<PySimaple>();
  const [fileSystem, setFileSystem] = React.useState<any>();
  const [uow, setUow] = React.useState<PySimapleUow>();

  const isLoaded = React.useMemo(() => !!pySimaple, [pySimaple]);

  async function load() {
    try {
      setIsLoading(true);

      const { pySimaple, fileSystem } = await loadPySimaple();

      setPySimaple(pySimaple);
      setUow(pySimaple.createUow());
      setFileSystem(fileSystem);
    } finally {
      setIsLoading(false);
    }
  }

  /**
   * Sync memory file system to indexedDB.
   */
  async function syncFs() {
    console.log("syncFs: syncing memory file system to indexedDB");
    console.log(fileSystem);
    if (!fileSystem) {
      console.warn("syncFs: FileSystem is not loaded");
      return;
    }
    const error = await new Promise((resolve) =>
      fileSystem.syncfs(false, resolve),
    );

    if (error) {
      throw new Error(`syncFs: Failed to sync to IndexedDB: ${error}`);
    }
  }

  return {
    pySimaple,
    uow,
    syncFs,
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

export { PySimapleProvider, usePySimaple, usePySimapleBeforeLoad };

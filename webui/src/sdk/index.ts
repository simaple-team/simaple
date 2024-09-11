import { loadPyodide } from "pyodide";
import { SimulatorResponse } from "./models";
import { BaselineConfiguration } from "./models/BaselineConfiguration";
import { OperationLog } from "./models/OperationLog";

export interface PySimapleUow {}

export interface PySimaple {
  createUow(): PySimapleUow;
  queryAllSimulator(uow: PySimapleUow): SimulatorResponse[];
  createSimulatorFromBaseline(
    configuration: BaselineConfiguration,
    uow: PySimapleUow,
  ): string;
  runSimulatorWithPlan(
    id: string,
    plan: string,
    uow: PySimapleUow,
  ): OperationLog[];
  getLatestLog(id: string, uow: PySimapleUow): OperationLog;
  getAllLogs(id: string, uow: PySimapleUow): OperationLog[];
}

export async function loadPySimaple() {
  const pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.2/full/",
  });

  pyodide.FS.mkdirTree("/simaple-cache");
  await pyodide.FS.mount(pyodide.FS.filesystems.IDBFS, {}, "/simaple-cache");
  const error = await new Promise((resolve) =>
    pyodide.FS.syncfs(true, resolve),
  );

  if (error) {
    throw new Error(`Failed to sync from IndexedDB: ${error}`);
  }

  await pyodide.loadPackage("pydantic", { checkIntegrity: false });
  await pyodide.loadPackage("micropip", { checkIntegrity: false });
  await pyodide.loadPackage("sqlite3", { checkIntegrity: false });
  await pyodide.loadPackage("lzma", { checkIntegrity: false });

  const micropip = pyodide.pyimport("micropip");
  await micropip.install("loguru");
  await micropip.install("lark");
  await micropip.install("numpy");
  await micropip.install("pyyaml");
  await micropip.install("pyfunctional");
  await micropip.install("simaple", false, false);

  return {
    pySimaple: pyodide.runPython(`
  from simaple.app import wasm
  import os
  print(os.listdir('/simaple-cache'))
  wasm`),
    fileSystem: pyodide.FS,
  };
}

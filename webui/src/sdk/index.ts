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

export interface PySimapleProps {
  /**
   * The file system handle to mount to the Python environment.
   * If not provided, the Python environment will not have access to the file system.
   */
  fileSystemHandle?: FileSystemDirectoryHandle;
}

export async function loadPySimaple(props: PySimapleProps): Promise<PySimaple> {
  const { fileSystemHandle } = props;

  const pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.2/full/",
  });
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

  if (fileSystemHandle) {
    await pyodide.mountNativeFS("/simaple-cache", fileSystemHandle);
  }

  return pyodide.runPython(`
  from simaple.app import wasm
  wasm`) as Promise<PySimaple>;
}

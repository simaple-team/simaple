import { loadPyodide } from "pyodide";
import { OperationLogResponse } from "./models/OperationLogResponse.schema";
import { SIMAPLE_FILE_NAME } from "../../public/simaple_dependency";
export interface PySimapleUow {}

export interface PySimaple {
  runPlan(plan: string): OperationLogResponse[];
  hasEnvironment(plan: string): boolean;
  provideEnvironmentAugmentedPlan(plan: string): string;
}

export async function loadPySimaple() {
  const pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.2/full/",
  });

  await pyodide.loadPackage(["pydantic", "micropip", "sqlite3", "lzma"], {
    checkIntegrity: false,
  });

  const micropip = pyodide.pyimport("micropip");
  await micropip.install(["loguru", "lark", "numpy", "pyyaml", "pyfunctional"]);

  await micropip.install(
    `${window.location.origin}/${SIMAPLE_FILE_NAME}`,
    false,
    false,
  );

  return {
    pySimaple: pyodide.runPython(`
  import simaple.wasm as wasm
  wasm`),
  };
}

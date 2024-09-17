import { loadPyodide } from "pyodide";
import { OperationLog } from "./models/OperationLog";

export interface PySimapleUow {}

export interface PySimaple {
  run(
    plan: string,
    serializedCharacterProvider: Record<string, unknown>,
  ): OperationLog[];
  getSerializedCharacterProvider(plan: string): Record<string, unknown>;
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

  if (import.meta.env.DEV) {
    await micropip.install(
      "http://localhost:8000/simaple-0.4.2-py3-none-any.whl",
      false,
      false,
    );

    return {
      pySimaple: pyodide.runPython(`
    import simaple.wasm as wasm
    wasm`),
    };
  }

  await micropip.install(
    "https://simaple.pages.dev/simaple-0.4.2-py3-none-any.whl",
    false,
    false,
  );

  return {
    pySimaple: pyodide.runPython(`
  import simaple.wasm as wasm
  wasm`),
  };
}

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

  if (import.meta.env.DEV) {
    const handle = await window.showDirectoryPicker();
    console.log(handle);

    await pyodide.mountNativeFS("/tmp", handle);

    return {
      pySimaple: pyodide.runPython(`
    import sys
    import os
    sys.path.append('/tmp')
    print(os.listdir('/tmp'))
    import simaple.wasm as wasm
    wasm`),
    };
  }

  await micropip.install("simaple", false, false);

  return {
    pySimaple: pyodide.runPython(`
  import simaple.wasm as wasm
  wasm`),
  };
}

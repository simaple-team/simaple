/* eslint-disable no-undef */

import { SIMAPLE_FILE_NAME } from "./dependency.mjs";
import "https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js";

async function loadPyodideAndPackages() {
  self.pyodide = await loadPyodide();
  await self.pyodide.loadPackage(["pydantic", "micropip", "sqlite3", "lzma"], {
    checkIntegrity: false,
  });

  const micropip = self.pyodide.pyimport("micropip");
  await micropip.install(["loguru", "lark", "numpy", "pyyaml", "pyfunctional"]);

  await micropip.install(
    `${location.origin}/${SIMAPLE_FILE_NAME}`,
    false,
    false,
  );

  const pySimaple = await self.pyodide.runPythonAsync(`
      import simaple.wasm as wasm
      wasm`);

  return pySimaple;
}
let pyodideReadyPromise = loadPyodideAndPackages();

self.onmessage = async (event) => {
  const pyodide = await pyodideReadyPromise;
  const { id, method, ...params } = event.data;
  let result;

  try {
    switch (method) {
      case "ready":
        break;
      case "runPlan":
        result = await pyodide.runPlan(params.plan);
        break;
      case "getInitialPlanFromBaseline":
        result = await pyodide.getInitialPlanFromBaseline(params.baselineEnvironmentProvider);
        break;
      case "hasEnvironment":
        result = await pyodide.hasEnvironment(params.plan);
        break;
      case "provideEnvironmentAugmentedPlan":
        result = await pyodide.provideEnvironmentAugmentedPlan(params.plan);
        break;
      case "getAllComponent":
        result = await pyodide.getAllComponent(params.plan);
        break;
      default:
        throw new Error(`Unknown method: ${method}`);
    }
    self.postMessage({ id, result });
  } catch (error) {
    self.postMessage({ id, error: error.message });
  }
};

/* eslint-disable no-undef */

importScripts("/dependency.js");
importScripts("https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js");

async function loadPyodideAndPackages() {
  self.pyodide = await loadPyodide();
  await self.pyodide.loadPackage(["pydantic", "micropip", "sqlite3", "lzma"], {
    checkIntegrity: false,
  });

  const micropip = self.pyodide.pyimport("micropip");
  await micropip.install(["loguru", "lark", "numpy", "pyyaml", "pyfunctional"]);

  await micropip.install(
    `${location.origin}/${globalThis.SIMAPLE_FILE_NAME}`,
    false,
    false,
  );

  const pySimaple = await self.pyodide.runPythonAsync(`
      import simaple.api.prod as wasm
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
        result = pyodide.runPlan(params.plan);
        result = result.toJs({ dict_converter: Object.fromEntries });
        break;
      case "runPlanWithHint":
        result = pyodide.runPlanWithHint(
          params.previousPlan,
          params.history,
          params.plan,
        );
        result = result.toJs({ dict_converter: Object.fromEntries });
        break;
      case "getInitialPlanFromBaseline":
        result = pyodide.getInitialPlanFromBaseline(
          params.baselineEnvironmentProvider,
        );
        break;
      case "hasEnvironment":
        result = pyodide.hasEnvironment(params.plan);
        break;
      case "provideEnvironmentAugmentedPlan":
        result = pyodide.provideEnvironmentAugmentedPlan(params.plan);
        break;
      case "getAllComponent":
        result = pyodide.getAllComponent(params.plan);
        result = result.toJs({ dict_converter: Object.fromEntries });
        break;
      default:
        throw new Error(`Unknown method: ${method}`);
    }
    self.postMessage({
      id,
      result: {
        success: true,
        data: result,
      },
    });
  } catch (error) {
    self.postMessage({
      id,
      result: {
        success: false,
        error: error.message,
      },
    });
  }
};

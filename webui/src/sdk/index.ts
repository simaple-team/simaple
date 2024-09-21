import { loadPyodide } from "pyodide";
import { OperationLogResponse } from "./models/OperationLogResponse.schema";
import { SIMAPLE_FILE_NAME } from "./dependency";
import { BaselineEnvironmentProvider, SkillComponent } from "./models";
export interface PySimapleUow {}

export interface PySimaple {
  runPlan(plan: string): OperationLogResponse[];
  getInitialPlanFromBaseline(
    baselineEnvironmentProvider: BaselineEnvironmentProvider,
  ): string;
  hasEnvironment(plan: string): boolean;
  provideEnvironmentAugmentedPlan(plan: string): string;
  getAllComponent(): SkillComponent[];
}

export async function loadPySimaple(): Promise<{ pySimaple: PySimaple }> {
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

  const pySimaple = await pyodide.runPythonAsync(`
    import simaple.wasm as wasm
    wasm`);

  return {
    pySimaple: {
      runPlan: pySimaple.runPlan,
      getInitialPlanFromBaseline: pySimaple.getInitialPlanFromBaseline,
      hasEnvironment: pySimaple.hasEnvironment,
      provideEnvironmentAugmentedPlan:
        pySimaple.provideEnvironmentAugmentedPlan,
      getAllComponent: () =>
        pySimaple.getAllComponent().toJs({
          dict_converter: Object.fromEntries,
        }),
    },
  };
}

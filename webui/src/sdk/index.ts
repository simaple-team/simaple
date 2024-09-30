import { OperationLogResponse } from "./models/OperationLogResponse.schema";
import { SuccessResponse } from "./models/SuccessResponse.schema.manual";
import { ErrorResponse } from "./models/ErrorResponse.schema";
import { BaselineEnvironmentProvider, SkillComponent } from "./models";

// Initialize the Web Worker
const pyodideWorker = new Worker(new URL("./webworker.mjs", import.meta.url), {
  type: "module",
});

// Store callbacks for resolving promises
const callbacks: Record<string, (data: unknown) => void> = {};

// Handle messages received from the worker
pyodideWorker.onmessage = (event) => {
  const { id, result } = event.data;
  const onSuccess = callbacks[id];
  delete callbacks[id];
  onSuccess(result);
};

// Generate unique IDs for each message
let idCounter = 0;
function generateId() {
  idCounter = (idCounter + 1) % Number.MAX_SAFE_INTEGER;
  return idCounter;
}

// Send a message to the worker and return a promise
function sendMessage(message: {
  method: string;
  [key: string]: unknown;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
}): Promise<any> {
  return new Promise((resolve) => {
    const id = generateId();
    callbacks[id] = resolve;
    pyodideWorker.postMessage({ id, ...message });
  });
}

export interface PySimaple {
  ready(): Promise<void>;
  runPlan(
    plan: string,
  ): Promise<SuccessResponse<OperationLogResponse[]> | ErrorResponse>;
  getInitialPlanFromBaseline(
    baselineEnvironmentProvider: BaselineEnvironmentProvider,
  ): Promise<string>;
  hasEnvironment(plan: string): Promise<boolean>;
  provideEnvironmentAugmentedPlan(plan: string): Promise<string>;
  getAllComponent(
    plan: string,
  ): Promise<SuccessResponse<SkillComponent[]> | ErrorResponse>;
}

// Define multiple methods
const pySimaple: PySimaple = {
  ready: () => sendMessage({ method: "ready" }),
  runPlan: (plan: string) => sendMessage({ method: "runPlan", plan }),
  getInitialPlanFromBaseline: (baselineEnvironmentProvider: unknown) =>
    sendMessage({
      method: "getInitialPlanFromBaseline",
      baselineEnvironmentProvider,
    }),
  hasEnvironment: (plan: string) =>
    sendMessage({ method: "hasEnvironment", plan }),
  provideEnvironmentAugmentedPlan: (plan: string) =>
    sendMessage({ method: "provideEnvironmentAugmentedPlan", plan }),
  getAllComponent: (plan: string) =>
    sendMessage({ method: "getAllComponent", plan }),
};

// Export the methods
export { pySimaple };

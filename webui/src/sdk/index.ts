import { err, ok, ResultAsync } from "neverthrow";
import {
  BaselineEnvironmentProvider,
  OperationLogResponse,
  SkillComponent,
} from "./models";

// Initialize the Web Worker
const pyodideWorker = new Worker(new URL("./webworker.mjs", import.meta.url), {
  type: "module",
});

// Store callbacks for resolving promises
const callbacks: Record<string, (data: unknown) => void> = {};

// Handle messages received from the worker
pyodideWorker.onmessage = (event) => {
  const { id, result } = event.data;
  const cb = callbacks[id];
  delete callbacks[id];

  if (result.success) {
    cb(ok(result.data));
  } else {
    cb(err(result.error));
  }
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
}): ResultAsync<any, string> {
  return new ResultAsync(
    new Promise((resolve) => {
      const id = generateId();
      // @ts-ignore
      callbacks[id] = resolve;
      pyodideWorker.postMessage({ id, ...message });
    }),
  );
}

export interface PySimaple {
  ready(): ResultAsync<void, string>;
  runPlan(plan: string): ResultAsync<OperationLogResponse[], string>;
  runPlanWithHint(
    previousPlan: string,
    history: OperationLogResponse[],
    plan: string,
  ): ResultAsync<OperationLogResponse[], string>;
  getInitialPlanFromBaseline(
    baselineEnvironmentProvider: BaselineEnvironmentProvider,
  ): ResultAsync<string, string>;
  hasEnvironment(plan: string): ResultAsync<boolean, string>;
  provideEnvironmentAugmentedPlan(plan: string): ResultAsync<string, string>;
  getAllComponent(plan: string): ResultAsync<SkillComponent[], string>;
}

// Define multiple methods
const pySimaple: PySimaple = {
  ready: () => sendMessage({ method: "ready" }),
  runPlan: (plan: string) => sendMessage({ method: "runPlan", plan }),
  runPlanWithHint: (
    previousPlan: string,
    history: OperationLogResponse[],
    plan: string,
  ) => sendMessage({ method: "runPlanWithHint", previousPlan, history, plan }),
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

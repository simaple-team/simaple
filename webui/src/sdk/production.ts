import { err, ok, ResultAsync } from "neverthrow";
import { PySimaple } from "./interface";

// Initialize the Web Worker
const pyodideWorker = new Worker(new URL("./webworker.js", import.meta.url));

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

// Define multiple methods
const pySimaple: PySimaple = {
  ready: () => sendMessage({ method: "ready" }),
  runPlan: (plan) => sendMessage({ method: "runPlan", plan }),
  runPlanWithHint: (previousPlan, history, plan) =>
    sendMessage({ method: "runPlanWithHint", previousPlan, history, plan }),
  getInitialPlanFromMetadata: (metadata) =>
    sendMessage({
      method: "getInitialPlanFromMetadata",
      metadata,
    }),
  hasEnvironment: (plan) => sendMessage({ method: "hasEnvironment", plan }),
  provideEnvironmentAugmentedPlan: (plan) =>
    sendMessage({ method: "provideEnvironmentAugmentedPlan", plan }),
  getAllComponent: (plan) => sendMessage({ method: "getAllComponent", plan }),
};

// Export the methods
export { pySimaple };

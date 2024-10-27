import { okAsync, ResultAsync } from "neverthrow";
import { PySimaple } from "./interface";

const API_ENDPOINT = "http://localhost:8000";

const fetcher = async (url: string, body: unknown) => {
  const response = await fetch(url, {
    method: "POST",
    body: JSON.stringify(body),
    headers: {
      "Content-Type": "application/json",
    },
  });
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
};

export const pySimaple: PySimaple = {
  ready: () => okAsync(null),
  runPlan: (plan) =>
    ResultAsync.fromPromise(
      fetcher(`${API_ENDPOINT}/runPlan`, { plan }),
      (error: any) => error.message,
    ),
  runPlanWithHint: (previous_plan, history, plan) =>
    ResultAsync.fromPromise(
      // intentionally using runPlan; runPlanWithHint breaks on pySimaple changes
      fetcher(`${API_ENDPOINT}/runPlan`, {
        plan,
      }),
      (error: any) => error.message,
    ),
  getInitialPlanFromBaseline: (baselineEnvironmentProvider) =>
    ResultAsync.fromPromise(
      fetcher(
        `${API_ENDPOINT}/getInitialPlanFromBaseline`,
        baselineEnvironmentProvider,
      ),
      (error: any) => error.message,
    ),
  hasEnvironment: (plan) =>
    ResultAsync.fromPromise(
      fetcher(`${API_ENDPOINT}/hasEnvironment`, { plan }),
      (error: any) => error.message,
    ),
  provideEnvironmentAugmentedPlan: (plan) =>
    ResultAsync.fromPromise(
      fetcher(`${API_ENDPOINT}/provideEnvironmentAugmentedPlan`, { plan }),
      (error: any) => error.message,
    ),
  getAllComponent: (plan) =>
    ResultAsync.fromPromise(
      fetcher(`${API_ENDPOINT}/getAllComponent`, { plan }),
      (error: any) => error.message,
    ),
};

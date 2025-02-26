import { ResultAsync } from "neverthrow";
import {
  BaselineEnvironmentProvider,
  OperationLogResponse,
  SkillComponent,
} from "./models";
import { NexonApiEnvironmentProvider } from "./models/NexonApiEnvironmentProvider.schema";

export interface PySimaple {
  ready(): ResultAsync<null, string>;
  runPlan(plan: string): ResultAsync<OperationLogResponse[], string>;
  runPlanWithHint(
    previousPlan: string,
    history: OperationLogResponse[],
    plan: string,
  ): ResultAsync<OperationLogResponse[], string>;
  getInitialPlanFromMetadata(metadata: {
    author?: string;
    provider:
      | {
          name: "BaselineEnvironmentProvider";
          data: BaselineEnvironmentProvider;
        }
      | {
          name: "NexonAPIEnvironmentProvider";
          data: NexonApiEnvironmentProvider;
        };
  }): ResultAsync<string, string>;
  hasEnvironment(plan: string): ResultAsync<boolean, string>;
  provideEnvironmentAugmentedPlan(plan: string): ResultAsync<string, string>;
  getAllComponent(plan: string): ResultAsync<SkillComponent[], string>;
}

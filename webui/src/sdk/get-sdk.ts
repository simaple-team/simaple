import {
  CreateSnapshotCommand,
  MinimalSimulatorConfiguration,
  RequestRun,
  SimulatorResponse,
} from "./models";
import { BaselineConfiguration } from "./models/BaselineConfiguration";
import { OperationLog } from "./models/OperationLog";
import { Skill } from "./models/Skill";
import { SnapshotResponse } from "./models/SnapshotResponse";

export function getSDK({
  baseUrl = "localhost:8000",
  fetchFn = fetch,
}: {
  baseUrl: string;
  fetchFn: (url: string, init?: RequestInit) => Promise<Response>;
}) {
  async function _request(url: string, requestInit: RequestInit = {}) {
    return fetchFn(`${baseUrl}${url}`, {
      ...requestInit,
      headers: {
        ...(requestInit.headers ?? {}),
        "content-type": "application/json",
      },
    }).then((res) => res.json());
  }

  async function getAllSimulators(): Promise<SimulatorResponse[]> {
    return _request(`/workspaces`);
  }

  async function createMinimalSimulator(
    configuration: MinimalSimulatorConfiguration,
  ): Promise<SimulatorResponse> {
    return _request(`/workspaces`, {
      method: "POST",
      body: JSON.stringify(configuration),
    });
  }

  async function createBaselineSimulator(
    configuration: BaselineConfiguration,
  ): Promise<SimulatorResponse> {
    return _request(`/workspaces/baseline`, {
      method: "POST",
      body: JSON.stringify(configuration),
    });
  }

  async function getAllSnapshots(): Promise<SnapshotResponse[]> {
    return _request(`/snapshots`);
  }

  async function createSnapshot(
    req: CreateSnapshotCommand,
  ): Promise<SnapshotResponse> {
    return _request(`/snapshots`, {
      method: "POST",
      body: JSON.stringify(req),
    });
  }

  async function loadFromSnapshot(id: string): Promise<string> {
    return _request(`/snapshots/${id}/load`, {
      method: "POST",
    });
  }

  async function run(id: string, req: RequestRun): Promise<OperationLog[]> {
    return _request(`/workspaces/run/${id}`, {
      method: "POST",
      body: JSON.stringify(req),
    });
  }

  async function getLatestLog(id: string): Promise<OperationLog> {
    return _request(`/workspaces/logs/${id}/latest`);
  }

  async function getLogs(id: string): Promise<OperationLog[]> {
    return _request(`/workspaces/logs/${id}`);
  }

  async function getSkills(): Promise<Skill[]> {
    return _request(`/skills`);
  }

  return {
    getAllSimulators,
    createMinimalSimulator,
    createBaselineSimulator,
    getAllSnapshots,
    createSnapshot,
    loadFromSnapshot,
    run,
    getLatestLog,
    getLogs,
    getSkills,
  };
}

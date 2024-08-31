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
import { loadPyodide } from 'pyodide'
import {AsyncLock} from 'async-lock'


export function getSDK({
  baseUrl = "localhost:8000",
  fetchFn = fetch,
}: {
  baseUrl: string;
  fetchFn: (url: string, init?: RequestInit) => Promise<Response>;
}) {
  var isloaded = false;
  var pySimapleWasm, pySimapleUow;
  var uniqueSimulatorId = 0;
  var lock = false;

  async function initializeConfiguration(){
    if (lock) {
      while (lock) {
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
    }
    lock = true;
    if (isloaded) return;

    // Load Pyodide
    let pyodide = await loadPyodide({ indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.2/full/"});
    await pyodide.loadPackage("pydantic", { checkIntegrity: false });
    await pyodide.loadPackage("micropip", { checkIntegrity: false });
    await pyodide.loadPackage("sqlite3", { checkIntegrity: false });
    await pyodide.loadPackage("lzma", { checkIntegrity: false });

    const micropip = pyodide.pyimport("micropip");
    await micropip.install('loguru');
    await micropip.install('lark');
    await micropip.install('numpy');
    await micropip.install('pyyaml');
    await micropip.install('pyfunctional');
    //await micropip.install('simaple', false, false);
  
    let handle = await (window as any).showDirectoryPicker();
    console.log(handle);

    await pyodide.mountNativeFS('/tmp', handle);

    pySimapleWasm = await pyodide.runPython(`
    import sys
    import os
    sys.path.append('/tmp')
    print(os.listdir('/tmp'))
    from simaple.app import wasm
    wasm`);
    pySimapleUow = pySimapleWasm.createUow();
    isloaded = true;
    console.log("Laod done")
    lock = false;
  }

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
    if (!isloaded) {
      return [];
    }
    let simulators = pySimapleWasm.queryAllSimulator(pySimapleUow);
    return simulators;
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
    uniqueSimulatorId = pySimapleWasm.createSimulatorFromBaseline(
      configuration,
      pySimapleUow
    );
    return {"id": uniqueSimulatorId};
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
    return pySimapleWasm.runSimulatorWithPlan(
      id, req.plan, 
      pySimapleUow);
  }

  async function getLatestLog(id: string): Promise<OperationLog> {
    return pySimapleWasm.getLatestLog(id, pySimapleUow);
  }

  async function getLogs(id: string): Promise<OperationLog[]> {
    return pySimapleWasm.getAllLogs(id, pySimapleUow);
  }

  async function getSkills(): Promise<Skill[]> {
    return _request(`/skills`);
  }

  return {
    initializeConfiguration,
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

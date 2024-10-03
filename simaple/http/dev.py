from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import simaple.wasm as wasm
from simaple.container.environment_provider import BaselineEnvironmentProvider
from simaple.wasm.models.simulation import OperationLogResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PlanRequest(BaseModel):
    plan: str


class PlanWithHintRequest(BaseModel):
    plan: str
    previous_plan: str
    history: list[OperationLogResponse]


@app.post("/runPlan")
def runPlan(req: PlanRequest):
    return wasm.runPlan(req.plan)


@app.post("/hasEnvironment")
def hasEnvironment(req: PlanRequest):
    return wasm.hasEnvironment(req.plan)


@app.post("/provideEnvironmentAugmentedPlan")
def provideEnvironmentAugmentedPlan(req: PlanRequest):
    return wasm.provideEnvironmentAugmentedPlan(req.plan)


@app.post("/getAllComponent")
def getAllComponent(req: PlanRequest):
    return wasm.getAllComponent(req.plan)


@app.post("/getInitialPlanFromBaseline")
def getInitialPlanFromBaseline(baseline: BaselineEnvironmentProvider):
    return wasm.getInitialPlanFromBaseline(baseline)


@app.post("/runPlanWithHint")
def runPlanWithHint(req: PlanWithHintRequest):
    return wasm.runPlanWithHint(req.previous_plan, req.history, req.plan)

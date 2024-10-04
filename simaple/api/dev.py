from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import simaple.api.base as api
from simaple.api.models.simulation import OperationLogResponse
from simaple.container.environment_provider import BaselineEnvironmentProvider

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
def run_plan(req: PlanRequest):
    return api.run_plan(req.plan)


@app.post("/hasEnvironment")
def has_environment(req: PlanRequest):
    return api.has_environment(req.plan)


@app.post("/provideEnvironmentAugmentedPlan")
def provide_environment_augmented_plan(req: PlanRequest):
    return api.provide_environment_augmented_plan(req.plan)


@app.post("/getInitialPlanFromBaseline")
def get_initial_plan_from_baseline(baseline: BaselineEnvironmentProvider):
    return api.get_initial_plan_from_baseline(baseline)


@app.post("/runPlanWithHint")
def run_plan_with_hint(req: PlanWithHintRequest):
    return api.run_plan_with_hint(req.previous_plan, req.history, req.plan)


@app.post("/getAllComponent")
def get_all_component(req: PlanRequest):
    return api.get_all_component(req.plan)

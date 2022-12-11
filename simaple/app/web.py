import fastapi
from fastapi.middleware.cors import CORSMiddleware

from simaple.app.routers.statistics import statistics_router
from simaple.app.routers.workspace import router


class SimapleWeb(fastapi.FastAPI):
    def __init__(self):
        super().__init__()

        self.include_router(router)
        self.include_router(statistics_router)


app = SimapleWeb()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

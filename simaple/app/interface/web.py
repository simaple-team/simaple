import fastapi
from fastapi.middleware.cors import CORSMiddleware

from simaple.app.interface.container import WebContainer, WebSetting
from simaple.app.interface.handler import add_exception_handlers
from simaple.app.interface.routers import snapshot, statistics, workspace
from simaple.app.interface.routers.component_spec import component_spec_router
from simaple.app.interface.routers.snapshot import snapshot_router
from simaple.app.interface.routers.statistics import statistics_router
from simaple.app.interface.routers.workspace import router


class SimapleWeb(fastapi.FastAPI):
    def __init__(self):
        super().__init__()

        container = WebContainer()
        container.config.from_pydantic(WebSetting())
        container.wire(packages=[statistics, workspace, snapshot])

        self.container: WebContainer = container

        self.include_router(router)
        self.include_router(statistics_router)
        self.include_router(snapshot_router)
        self.include_router(component_spec_router)

    def reset_database(self):
        self.container.sql_database().delete()
        self.container.sql_database().create()


app = SimapleWeb()
add_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

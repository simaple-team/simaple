import fastapi

from simaple.app.routers.workspace import router


class SimapleWeb(fastapi.FastAPI):
    def __init__(self):
        super().__init__()

        self.include_router(router)


app = SimapleWeb()

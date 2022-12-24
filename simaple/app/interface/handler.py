import fastapi
from fastapi.responses import JSONResponse

from simaple.app.application.exception import ApplicationError


def add_exception_handlers(app: fastapi.FastAPI):
    @app.exception_handler(ApplicationError)
    async def unicorn_exception_handler(
        request: fastapi.Request, exc: ApplicationError
    ):
        return JSONResponse(
            status_code=409,
            content={"message": f"{exc}"},
        )

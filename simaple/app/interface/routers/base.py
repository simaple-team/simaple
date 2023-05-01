import fastapi
from dependency_injector.wiring import Provide

from simaple.app.interface.container import WebContainer

UowProvider = fastapi.Depends(Provide[WebContainer.unit_of_work])

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from gardem_api import broker, logger, routes
from gardem_api.config import settings
from gardem_api.life import life_control


def create_app() -> FastAPI:
    logger.setup()
    broker.setup()

    app = FastAPI(
        debug=settings.DEBUG,
        title="Gardem API",
        summary="this api are used for manage one gardem of productive plants",
        description="this api are used for manage one gardem of productive plants",
        version="1.0",
        openapi_url="/doc/openapi.json",
        docs_url="/doc/swagger",
        redoc_url=None,
        lifespan=life_control,
        default_response_class=ORJSONResponse,
    )

    routes.init_app(app)

    return app

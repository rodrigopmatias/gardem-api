from fastapi import APIRouter, Depends, FastAPI

from gardem_api.auth import User, current_user

router = APIRouter(prefix="/v1/auth", tags=["auth"])


def init_app(app: FastAPI) -> None:
    app.include_router(router)


@router.get("/who-are-you")
async def who_are_you(user: User = Depends(current_user)) -> User:
    return user

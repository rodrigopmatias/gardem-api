from fastapi import APIRouter, Depends, FastAPI, HTTPException, Response, status
from sqlalchemy import func, select, update

from gardem_api.auth import User, current_user
from gardem_api.db import Datasource, datasource
from gardem_api.routes.gardens import models, schema

router = APIRouter(prefix="/v1/gardens", tags=["gardens"])


def init_app(app: FastAPI) -> None:
    app.include_router(router)


@router.post("", status_code=status.HTTP_201_CREATED)
async def gardem_create(
    body: schema.GardemEditable,
    user: User = Depends(current_user),
    db: Datasource = Depends(datasource),
) -> schema.Gardem:
    if not user.allowed("gradem:create"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have access for this resource"
        )

    async with db() as tx:
        obj = models.Gardem(**body.model_dump())
        tx.add(obj)
        await tx.commit()
        await tx.refresh(obj)

        return schema.Gardem.model_validate(obj)


@router.get("")
async def gardem_all(
    offset: int = 0,
    limit: int = 30,
    user: User = Depends(current_user),
    db: Datasource = Depends(datasource),
) -> schema.GardemListResult:
    if not user.allowed("gradem:list"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have access for this resource"
        )

    stmt = select(models.Gardem).offset(offset).limit(limit)
    stmt_count = select(func.count(models.Gardem.id))
    async with db() as tx:
        count = (await tx.execute(stmt_count)).scalar_one()
        query = (await tx.execute(stmt)).scalars()

        return schema.GardemListResult(
            count=count,
            next=None,
            previous=None,
            items=[schema.Gardem.model_validate(obj) for obj in query],
        )


@router.get("/{id:int}")
async def gardem_retrive(
    id: int, user: User = Depends(current_user), db: Datasource = Depends(datasource)
) -> schema.Gardem:
    if not user.allowed("gradem:retrive"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have access for this resource"
        )

    async with db() as tx:
        stmt = select(models.Gardem).where(models.Gardem.id == id)
        obj = (await tx.execute(stmt)).scalar_one_or_none()

        if not obj:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"gardem with id {id} not found"
            )

        return schema.Gardem.model_validate(obj)


@router.patch("/{id:int}")
async def gardem_partial_update(
    id: int,
    body: schema.GardemEditable,
    user: User = Depends(current_user),
    db: Datasource = Depends(datasource),
) -> schema.Gardem:
    if not user.allowed("gradem:update"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have access for this resource"
        )

    async with db() as tx:
        stmt = select(models.Gardem).where(models.Gardem.id == id)
        obj = (await tx.execute(stmt)).scalar_one_or_none()

        if not obj:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"gardem with id {id} not found"
            )

        stmt = (
            update(models.Gardem)
            .where(models.Gardem.id == id)
            .values(**body.model_dump(exclude_unset=True))
        )
        await tx.execute(stmt)
        await tx.commit()
        await tx.refresh(obj)

        return schema.Gardem.model_validate(obj)


@router.put("/{id:int}")
async def gardem_update_or_create(
    id: int,
    body: schema.GardemEditable,
    response: Response,
    user: User = Depends(current_user),
    db: Datasource = Depends(datasource),
) -> schema.Gardem:
    async with db() as tx:
        stmt = select(models.Gardem).where(models.Gardem.id == id)
        obj = (await tx.execute(stmt)).scalar_one_or_none()

        if not obj:
            if not user.allowed("gradem:create"):
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN, "you not have access for this resource"
                )

            obj = models.Gardem(id=id, **body.model_dump())
            tx.add(obj)
            response.status_code = status.HTTP_201_CREATED
        else:
            if not user.allowed("gradem:update"):
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN, "you not have access for this resource"
                )

            stmt = (
                update(models.Gardem)
                .where(models.Gardem.id == id)
                .values(**body.model_dump(exclude_unset=True))
            )
            await tx.execute(stmt)

        await tx.commit()
        await tx.refresh(obj)

        return schema.Gardem.model_validate(obj)


@router.delete("/{id:int}", status_code=status.HTTP_204_NO_CONTENT)
async def gardem_delete(
    id: int, user: User = Depends(current_user), db: Datasource = Depends(datasource)
) -> None:
    if not user.allowed("gradem:delete"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have access for this resource"
        )

    async with db() as tx:
        stmt = select(models.Gardem).where(models.Gardem.id == id)
        obj = (await tx.execute(stmt)).scalar_one_or_none()

        if not obj:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"gardem with id {id} not found"
            )

        await tx.delete(obj)
        await tx.commit()

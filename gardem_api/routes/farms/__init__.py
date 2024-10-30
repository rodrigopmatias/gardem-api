from fastapi import APIRouter, Depends, FastAPI, HTTPException, Response, status
from sqlalchemy import func, select, update

from gardem_api.auth import User, current_user
from gardem_api.db import Datasource, datasource
from gardem_api.routes.farms import models, schema

router = APIRouter(prefix="/v1/farms", tags=["farms"])


def init_app(app: FastAPI) -> None:
    app.include_router(router)


@router.post("", status_code=status.HTTP_201_CREATED)
async def farm_create(
    body: schema.FarmEditable,
    user: User = Depends(current_user),
    db: Datasource = Depends(datasource),
) -> schema.Farm:
    if not user.allowed("farm:create"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have access for this resource"
        )

    async with db() as tx:
        obj = models.Farm(**body.model_dump())
        tx.add(obj)
        await tx.commit()
        await tx.refresh(obj)

        return schema.Farm.model_validate(obj)


@router.get("")
async def farm_all(
    offset: int = 0,
    limit: int = 30,
    user: User = Depends(current_user),
    db: Datasource = Depends(datasource),
) -> schema.FarmListResult:
    if not user.allowed("farm:list"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have access for this resource"
        )

    stmt = select(models.Farm).offset(offset).limit(limit)
    stmt_count = select(func.count(models.Farm.id))
    async with db() as tx:
        count = (await tx.execute(stmt_count)).scalar_one()
        query = (await tx.execute(stmt)).scalars()

        return schema.FarmListResult(
            count=count,
            next=None,
            previous=None,
            items=[schema.Farm.model_validate(obj) for obj in query],
        )


@router.get("/{id:int}")
async def farm_retrive(
    id: int, user: User = Depends(current_user), db: Datasource = Depends(datasource)
) -> schema.Farm:
    if not user.allowed("farm:retrive"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have access for this resource"
        )

    async with db() as tx:
        stmt = select(models.Farm).where(models.Farm.id == id)
        obj = (await tx.execute(stmt)).scalar_one_or_none()

        if not obj:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"gardem with id {id} not found"
            )

        return schema.Farm.model_validate(obj)


@router.patch("/{id:int}")
async def farm_partial_update(
    id: int,
    body: schema.FarmEditable,
    user: User = Depends(current_user),
    db: Datasource = Depends(datasource),
) -> schema.Farm:
    if not user.allowed("farm:update"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have access for this resource"
        )

    async with db() as tx:
        stmt = select(models.Farm).where(models.Farm.id == id)
        obj = (await tx.execute(stmt)).scalar_one_or_none()

        if not obj:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"farm with id {id} not found"
            )

        stmt = (
            update(models.Farm)
            .where(models.Farm.id == id)
            .values(**body.model_dump(exclude_unset=True))
        )
        await tx.execute(stmt)
        await tx.commit()
        await tx.refresh(obj)

        return schema.Farm.model_validate(obj)


@router.put("/{id:int}")
async def farm_update_or_create(
    id: int,
    body: schema.FarmEditable,
    response: Response,
    user: User = Depends(current_user),
    db: Datasource = Depends(datasource),
) -> schema.Farm:
    async with db() as tx:
        stmt = select(models.Farm).where(models.Farm.id == id)
        obj = (await tx.execute(stmt)).scalar_one_or_none()

        if not obj:
            if not user.allowed("farm:create"):
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN, "you not have access for this resource"
                )

            obj = models.Farm(id=id, **body.model_dump())
            tx.add(obj)
            response.status_code = status.HTTP_201_CREATED
        else:
            if not user.allowed("farm:update"):
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN, "you not have access for this resource"
                )

            stmt = (
                update(models.Farm)
                .where(models.Farm.id == id)
                .values(**body.model_dump(exclude_unset=True))
            )
            await tx.execute(stmt)

        await tx.commit()
        await tx.refresh(obj)

        return schema.Farm.model_validate(obj)


@router.delete("/{id:int}", status_code=status.HTTP_204_NO_CONTENT)
async def farm_delete(
    id: int, user: User = Depends(current_user), db: Datasource = Depends(datasource)
) -> None:
    if not user.allowed("farm:delete"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have access for this resource"
        )

    async with db() as tx:
        stmt = select(models.Farm).where(models.Farm.id == id)
        obj = (await tx.execute(stmt)).scalar_one_or_none()

        if not obj:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"farm with id {id} not found"
            )

        await tx.delete(obj)
        await tx.commit()

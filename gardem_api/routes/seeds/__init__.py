from fastapi import APIRouter, Depends, FastAPI, HTTPException, Response, status
from sqlalchemy import func, select, update

from gardem_api.auth import User, current_user
from gardem_api.db import Datasource, datasource
from gardem_api.routes.seeds import models, schema

router = APIRouter(prefix="/v1/seeds", tags=["seeds"])


def init_app(app: FastAPI) -> None:
    app.include_router(router)


@router.post("", status_code=status.HTTP_201_CREATED)
async def seed_create(
    body: schema.SeedEditale,
    user: User = Depends(current_user),
    db: Datasource = Depends(datasource),
) -> schema.Seed:
    if not user.allowed("seeds:create"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have permission for this resource"
        )

    async with db() as tx:
        obj = models.Seed(**body.model_dump())
        tx.add(obj)
        await tx.commit()
        await tx.refresh(obj)

        return schema.Seed.model_validate(obj)


@router.get("")
async def seed_list(
    offset: int = 0,
    limit: int = 30,
    user: User = Depends(current_user),
    db: Datasource = Depends(datasource),
) -> schema.SeedListResult:
    if not user.allowed("seeds:list"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have permission for this resource"
        )

    stmt = select(models.Seed).offset(offset).limit(limit)
    stmt_count = select(func.count(models.Seed.id))
    async with db() as tx:
        count = (await tx.execute(stmt_count)).scalar_one()
        query = (await tx.execute(stmt)).scalars()

        return schema.SeedListResult(
            count=count, items=[schema.Seed.model_validate(seed) for seed in query]
        )


@router.get("/{id:int}")
async def seed_retrive(
    id: int, user: User = Depends(current_user), db: Datasource = Depends(datasource)
) -> schema.Seed:
    if not user.allowed("seeds:retrive"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have permission for this resource"
        )

    stmt = select(models.Seed).where(models.Seed.id == id)
    async with db() as tx:
        obj = (await tx.execute(stmt)).scalar_one_or_none()

        if not obj:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"seed with id {id} not found"
            )

        return schema.Seed.model_validate(obj)


@router.patch("/{id:int}")
async def seed_partial_update(
    id: int,
    body: schema.SeedEditale,
    user: User = Depends(current_user),
    db: Datasource = Depends(datasource),
) -> schema.Seed:
    if not user.allowed("seeds:partial-update"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have permission for this resource"
        )

    stmt = select(models.Seed).where(models.Seed.id == id)
    async with db() as tx:
        obj = (await tx.execute(stmt)).scalar_one_or_none()

        if not obj:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"seed with id {id} not found"
            )

        stmt = (
            update(models.Seed)
            .where(models.Seed.id == id)
            .values(body.model_dump(exclude_unset=True))
        )

        await tx.execute(stmt)
        await tx.commit()
        await tx.refresh(obj)

        return schema.Seed.model_validate(obj)


@router.put("/{id:int}")
async def seed_update_or_create(
    id: int,
    response: Response,
    body: schema.SeedEditale,
    user: User = Depends(current_user),
    db: Datasource = Depends(datasource),
) -> schema.Seed:
    stmt = select(models.Seed).where(models.Seed.id == id)
    async with db() as tx:
        obj = (await tx.execute(stmt)).scalar_one_or_none()

        if not obj:
            if not user.allowed("seed:create"):
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN,
                    "you not have permission for this resource",
                )

            obj = models.Seed(id=id, **body.model_dump())
            tx.add(obj)
            response.status_code = status.HTTP_201_CREATED
        else:
            if not user.allowed("seed:update"):
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN,
                    "you not have permission for this resource",
                )

            stmt = (
                update(models.Seed)
                .where(models.Seed.id == id)
                .values(body.model_dump(exclude_unset=True))
            )
            await tx.execute(stmt)

        await tx.commit()
        await tx.refresh(obj)

        return schema.Seed.model_validate(obj)


@router.delete("/{id:int}", status_code=status.HTTP_204_NO_CONTENT)
async def seed_delete(
    id: int,
    user: User = Depends(current_user),
    db: Datasource = Depends(datasource),
) -> None:
    if not user.allowed("seeds:delete"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have permission for this resource"
        )

    stmt = select(models.Seed).where(models.Seed.id == id)
    async with db() as tx:
        obj = (await tx.execute(stmt)).scalar_one_or_none()

        if not obj:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"seed with id {id} not found"
            )

        await tx.delete(obj)
        await tx.commit()

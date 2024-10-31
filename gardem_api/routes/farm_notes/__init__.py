from fastapi import APIRouter, Depends, FastAPI, HTTPException, Response, status
from sqlalchemy import func, select, update

from gardem_api.auth import User, current_user
from gardem_api.db import Datasource, datasource
from gardem_api.routes.farm_notes import models, schema

router = APIRouter(prefix="/v1/farms", tags=["farms"])


def init_app(app: FastAPI) -> None:
    app.include_router(router)


@router.post("/{farm_id:int}/notes", status_code=status.HTTP_201_CREATED)
async def farm_note_create(
    farm_id: int,
    body: schema.FarmNoteEditable,
    user: User = Depends(current_user),
    db: Datasource = Depends(datasource),
) -> schema.FarmNote:
    if not user.allowed("farm_notes:create"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have access for this resource"
        )

    async with db() as tx:
        obj = models.FarmNote(farm_id=farm_id, **body.model_dump())

        tx.add(obj)
        await tx.commit()
        await tx.refresh(obj)

        return schema.FarmNote.model_validate(obj)


@router.get("/{farm_id:int}/notes")
async def farm_note_all(
    farm_id: int,
    offset: int = 0,
    limit: int = 30,
    user: User = Depends(current_user),
    db: Datasource = Depends(datasource),
) -> schema.FarmNoteListResult:
    if not user.allowed("farm_notes:list"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have access for this resource"
        )

    sentences = [models.FarmNote.farm_id == farm_id]

    async with db() as tx:
        stmt = select(models.FarmNote).where(*sentences).offset(offset).limit(limit)
        stmt_count = select(func.count(models.FarmNote.id)).where(*sentences)

        query = (await tx.execute(stmt)).scalars()
        count = (await tx.execute(stmt_count)).scalar_one()

        return schema.FarmNoteListResult(
            count=count,
            next=None,
            previous=None,
            items=[schema.FarmNote.model_validate(note) for note in query],
        )


@router.get("/{farm_id:int}/notes/{id:int}")
async def farm_note_retrive(
    id: int,
    farm_id: int,
    user: User = Depends(current_user),
    db: Datasource = Depends(datasource),
) -> schema.FarmNote:
    if not user.allowed("farm_notes:retrive"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have access for this resource"
        )

    sentences = [models.FarmNote.id == id, models.FarmNote.farm_id == farm_id]

    async with db() as tx:
        stmt = select(models.FarmNote).where(*sentences)
        obj = (await tx.execute(stmt)).scalar_one_or_none()

        if not obj:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"on farm {farm_id} not found note {id}"
            )

        return schema.FarmNote.model_validate(obj)


@router.patch("/{farm_id:int}/notes/{id:int}")
async def farm_note_partial_update(
    id: int,
    farm_id: int,
    body: schema.FarmNoteUpdatable,
    user: User = Depends(current_user),
    db: Datasource = Depends(datasource),
) -> schema.FarmNote:
    if not user.allowed("farm_notes:retrive"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have access for this resource"
        )

    sentences = [models.FarmNote.id == id, models.FarmNote.farm_id == farm_id]

    async with db() as tx:
        stmt = select(models.FarmNote).where(*sentences)
        obj = (await tx.execute(stmt)).scalar_one_or_none()

        if not obj:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"on farm {farm_id} not found note {id}"
            )

        stmt = (
            update(models.FarmNote)
            .where(*sentences)
            .values(**body.model_dump(exclude_unset=True))
        )
        await tx.execute(stmt)
        await tx.commit()
        await tx.refresh(obj)

        return schema.FarmNote.model_validate(obj)


@router.put("/{farm_id:int}/notes/{id:int}")
async def farm_note_update(
    id: int,
    farm_id: int,
    body: schema.FarmNoteUpdatable,
    response: Response,
    user: User = Depends(current_user),
    db: Datasource = Depends(datasource),
) -> schema.FarmNote:
    if not user.allowed("farm_notes:retrive"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have access for this resource"
        )

    sentences = [models.FarmNote.id == id, models.FarmNote.farm_id == farm_id]

    async with db() as tx:
        stmt = select(models.FarmNote).where(*sentences)
        obj = (await tx.execute(stmt)).scalar_one_or_none()

        if not obj:
            obj = models.FarmNote(id=id, farm_id=farm_id, **body.model_dump())
            await tx.add(obj)
            response.status_code = status.HTTP_201_CREATED
        else:
            stmt = (
                update(models.FarmNote)
                .where(*sentences)
                .values(**body.model_dump(exclude_unset=True))
            )
            await tx.execute(stmt)

        await tx.commit()
        await tx.refresh(obj)

        return schema.FarmNote.model_validate(obj)


@router.delete("/{farm_id:int}/notes/{id:int}", status_code=status.HTTP_204_NO_CONTENT)
async def farm_note_delete(
    id: int,
    farm_id: int,
    user: User = Depends(current_user),
    db: Datasource = Depends(datasource),
) -> None:
    if not user.allowed("farm_notes:retrive"):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "you not have access for this resource"
        )

    sentences = [models.FarmNote.id == id, models.FarmNote.farm_id == farm_id]

    async with db() as tx:
        stmt = select(models.FarmNote).where(*sentences)
        obj = (await tx.execute(stmt)).scalar_one_or_none()

        if not obj:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, f"on farm {farm_id} not found note {id}"
            )

        await tx.delete(obj)
        await tx.commit()

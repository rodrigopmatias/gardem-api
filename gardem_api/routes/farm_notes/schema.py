from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

type FarmNoteType = Literal["note", "investment"]


class FarmNoteUpdatable(BaseModel):
    note: str


class FarmNoteEditable(FarmNoteUpdatable):
    farm_id: int
    note_type: FarmNoteType = Field(default="note")
    value: Decimal = Field(default=0.00)


class FarmNoteReadOnly(BaseModel):
    id: int
    created_at: datetime


class FarmNote(FarmNoteEditable, FarmNoteReadOnly):
    model_config = ConfigDict(from_attributes=True)


class FarmNoteListResult(BaseModel):
    count: int = 0
    next: str | None = None
    previous: str | None = None
    items: list[FarmNote] = Field(default_factory=lambda: [])

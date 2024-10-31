from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

type NoteType = Literal["note", "investment"]


class NoteUpdatable(BaseModel):
    note: str


class NoteEditable(NoteUpdatable):
    note_type: NoteType = Field(default="note")
    value: Decimal = Field(default=0.00)


class NoteReadOnly(BaseModel):
    id: int
    farm_id: int
    created_at: datetime


class Note(NoteEditable, NoteReadOnly):
    model_config = ConfigDict(from_attributes=True)


class NoteListResult(BaseModel):
    count: int = 0
    next: str | None = None
    previous: str | None = None
    items: list[Note] = Field(default_factory=lambda: [])

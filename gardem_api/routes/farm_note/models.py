from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from gardem_api.db import DBModel
from gardem_api.routes.farm_note.schema import FarmNoteType


class FarmNote(DBModel):
    __tablename__ = "farm_notes"

    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id"))
    created_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    note: Mapped[str] = mapped_column(Text())
    note_type: Mapped[FarmNoteType] = mapped_column(String(20), default="note")
    value: Mapped[Decimal] = mapped_column(DECIMAL(2, 10), default=0.00)

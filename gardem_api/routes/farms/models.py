from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from gardem_api.db import DBModel
from gardem_api.routes.farms.schema import FarmState


class Farm(DBModel):
    __tablename__ = "farms"

    code: Mapped[str] = mapped_column(String(10), unique=True)
    born_date: Mapped[date] = mapped_column(Date(), index=True)
    state: Mapped[FarmState] = mapped_column(String(20), index=True)
    gardem_id: Mapped[int] = mapped_column(ForeignKey("gardens.id"))
    seed_id: Mapped[int] = mapped_column(ForeignKey("seeds.id"))

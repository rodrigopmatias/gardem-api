from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from gardem_api.db import DBModel


class Seed(DBModel):
    __tablename__ = "seeds"

    name: Mapped[str] = mapped_column(String(100))

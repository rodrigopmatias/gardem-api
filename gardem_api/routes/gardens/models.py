from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from gardem_api.db import DBModel


class Gardem(DBModel):
    __tablename__ = "gardens"

    code: Mapped[str] = mapped_column(String(10), unique=True)
    size: Mapped[int] = mapped_column(Integer())

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

type FarmState = Literal["germinating", "vegetating", "fruiting", "ripening", "dying"]


class FarmEditable(BaseModel):
    code: str
    born_date: date
    gardem_id: int
    seed_id: int
    state: FarmState


class FarmReadOnly(BaseModel):
    id: int


class Farm(FarmEditable, FarmReadOnly):
    model_config = ConfigDict(from_attributes=True)


class FarmListResult(BaseModel):
    count: int = 0
    next: str | None = None
    previous: str | None = None
    items: list[Farm] = Field(default_factory=lambda: [])

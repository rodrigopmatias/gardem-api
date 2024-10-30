from pydantic import BaseModel, ConfigDict, Field


class GardemEditable(BaseModel):
    code: str
    size: int


class GardemReadOnly(BaseModel):
    id: int


class Gardem(GardemEditable, GardemReadOnly):
    model_config = ConfigDict(from_attributes=True)


class GardemListResult(BaseModel):
    count: int = 0
    next: str | None = None
    previous: str | None = None
    items: list[Gardem] = Field(default_factory=lambda: [])

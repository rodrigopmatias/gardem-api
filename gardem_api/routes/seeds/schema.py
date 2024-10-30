from pydantic import BaseModel, ConfigDict, Field


class SeedEditale(BaseModel):
    name: str


class SeedReadOnly(BaseModel):
    id: int


class Seed(SeedEditale, SeedReadOnly):
    model_config = ConfigDict(from_attributes=True)


class SeedListResult(BaseModel):
    count: int = Field(default=0)
    next: str | None = None
    previous: str | None = None
    items: list[Seed] = Field(default_factory=lambda: [])

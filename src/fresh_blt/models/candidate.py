from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field


class Candidate(BaseModel):
    id: int
    name: str
    withdrawn: bool = Field(False)
    meta: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> Candidate:
        return cls(
            id=data["id"],
            name=data["name"],
            withdrawn=data.get("withdrawn", False),
            meta=data.get("meta", {})
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "withdrawn": self.withdrawn,
            "meta": self.meta,
        }
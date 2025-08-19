from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .election import Election


class Candidate(BaseModel):
    id: int
    name: str
    withdrawn: bool = Field(False)
    meta: dict[str, Any] = Field(default_factory=dict)
    election: Election
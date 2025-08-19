from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .ballot import Ballot
    from .candidate import Candidate


class Election(BaseModel):
    name: str
    ballots: list[Ballot] = Field(default_factory=list)
    candidates: list[Candidate] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)

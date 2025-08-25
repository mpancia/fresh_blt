from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .candidate import Candidate


class Ballot(BaseModel):
    rankings: list[list[Candidate]] = Field(
        description="Ordered list of lists of candidates, where each inner list is a set of equally ranked candidates.",
    )
    weight: int = Field(
        default=1,
        description="Weight of the ballot, used for weighted voting systems.",
    )

    @classmethod
    def from_dict(cls, data: dict) -> Ballot:
        return cls(
            rankings=data["rankings"],
            weight=data["weight"],
        )
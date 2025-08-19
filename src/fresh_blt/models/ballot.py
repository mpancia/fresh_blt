from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .candidate import Candidate
    from .election import Election


class Ballot(BaseModel):
    election: Election = Field(
        description="The election this ballot belongs to.",
    )
    rankings: list[list[Candidate]] = Field(
        description="Ordered list of lists of candidates, where each inner list is a set of equally ranked candidates.",
    )
    weight: int = Field(
        default=1,
        description="Weight of the ballot, used for weighted voting systems.",
    )
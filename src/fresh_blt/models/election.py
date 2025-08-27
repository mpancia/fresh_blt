"""
Election model for .blt format.

Container for election contest with candidates, ballots, and metadata.
Central hub for ranked-choice voting data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .ballot import Ballot
    from .candidate import Candidate


class Election(BaseModel):
    """
    Election contest container with candidates, ballots, and metadata.

    Central data structure for ranked-choice voting contests.
    """

    name: str = Field(
        ...,
        description="Human-readable name or title of the election contest",
        examples=["City Council Election", "Board Member Race 2024"],
        min_length=1,
    )

    ballots: list[Ballot] = Field(
        default_factory=list,
        description="List of all ballots cast in the election with voter rankings and weights",
    )

    candidates: list[Candidate] = Field(
        default_factory=list,
        description="List of all candidates participating in the election, including withdrawn ones",
    )

    meta: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional election metadata for extensibility",
        examples=[{"location": "City Hall", "date": "2024-11-05", "type": "ranked_choice"}],
    )

"""
Ballot model for .blt files.

Represents voter rankings with support for ties and weighted voting.
Handles validation and serialization.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field, field_validator

if TYPE_CHECKING:
    from .candidate import Candidate


class Ballot(BaseModel):
    """
    Voter ballot with ranked preferences and weight.

    Rankings are list-of-lists: outer list is preference order,
    inner lists are tied candidates. Supports weighted voting.
    """

    rankings: list[list[Candidate]] = Field(
        ...,
        description=(
            "Ordered list of lists representing voter preferences. Each inner list "
            "contains candidates ranked equally at that preference level. Empty inner "
            "lists represent exhausted preferences."
        ),
        examples=[
            [[{"id": 1, "name": "Alice"}], [{"id": 2, "name": "Bob"}]],  # Alice > Bob
            [
                [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
                [{"id": 3, "name": "Charlie"}],
            ],  # Alice = Bob > Charlie
        ],
    )

    weight: int = Field(
        default=1,
        gt=0,  # Must be greater than 0
        description=(
            "Weight of the ballot for weighted voting systems. Must be a positive integer."
        ),
        examples=[1, 5, 10, 100],
    )

    @field_validator("rankings")
    @classmethod
    def validate_rankings(cls, v: list[list[Candidate]]) -> list[list[Candidate]]:
        """Check rankings are valid - no duplicate candidates."""
        # Empty rankings are allowed for exhausted preferences
        if not v:
            return v

        # Check for duplicate candidates across all rankings
        seen_candidates = set()
        for preference_level in v:
            for candidate in preference_level:
                if candidate in seen_candidates:
                    raise ValueError(f"Duplicate candidate found in rankings: {candidate}")
                seen_candidates.add(candidate)

        return v

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Ballot:
        """Create Ballot from dict. Requires 'rankings' and 'weight' keys."""
        # Validate required keys are present
        if "rankings" not in data:
            raise ValueError("Missing required key: 'rankings'")
        if "weight" not in data:
            raise ValueError("Missing required key: 'weight'")

        return cls(rankings=data["rankings"], weight=data["weight"])

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .candidate import Candidate


class Ballot(BaseModel):
    rankings: list[list[Candidate]] = Field(
        description="Ordered list of lists of candidates, where each inner list is a set of equally ranked candidates.",
    )
    weight: int = Field(
        default=1,
        gt=0,  # Must be greater than 0
        description="Weight of the ballot, used for weighted voting systems.",
    )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Ballot:
        """
        Create a Ballot instance from a dictionary.

        Args:
            data: Dictionary containing 'rankings' and 'weight' keys

        Returns:
            Ballot instance

        Raises:
            ValueError: If required keys are missing or invalid
            TypeError: If data types are incorrect
        """
        # Validate required keys are present
        if "rankings" not in data:
            raise ValueError("Missing required key: 'rankings'")
        if "weight" not in data:
            raise ValueError("Missing required key: 'weight'")

        # Use Pydantic's built-in validation by creating the instance
        return cls(rankings=data["rankings"], weight=data["weight"])
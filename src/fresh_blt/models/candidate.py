"""
Candidate model for .blt format.

Represents election participants with ID, name, withdrawal status, and metadata.
Handles serialization and provides basic equality/hashing by ID.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Candidate(BaseModel):
    """
    Election candidate with ID, name, withdrawal status, and metadata.

    Use ID for equality/hashing since names can change.
    Supports serialization via from_dict/to_dict.
    """

    id: int = Field(
        ...,
        description="Unique integer identifier for the candidate",
        gt=0,  # Must be positive
        examples=[1, 42, 100],
    )

    name: str = Field(
        ...,
        description="Human-readable full name of the candidate",
        examples=["Alice Johnson", "Bob Smith", "Dr. Charlie Brown"],
        min_length=1,
    )

    withdrawn: bool = Field(
        default=False, description="Whether the candidate has withdrawn from the election"
    )

    meta: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional candidate metadata for extensibility",
        examples=[
            {"party": "Independent", "age": 35, "experience": "5 years"},
            {"withdrawal_reason": "Personal reasons", "withdrawal_date": "2024-10-15"},
        ],
    )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Candidate:
        """Create Candidate from dict. Requires 'id' and 'name' keys."""
        return cls(
            id=data["id"],
            name=data["name"],
            withdrawn=data.get("withdrawn", False),
            meta=data.get("meta", {}),
        )

    def __hash__(self) -> int:
        """Hash by ID for set/dict usage."""
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        """Equal if same ID."""
        if not isinstance(other, Candidate):
            return NotImplemented
        return self.id == other.id

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "withdrawn": self.withdrawn,
            "meta": self.meta,
        }

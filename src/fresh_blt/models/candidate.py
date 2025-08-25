"""
Candidate model for BLT (Ballot Language for Tabulation) format.

This module defines the Candidate model, which represents a participant in an election.
Candidates can be active participants or withdrawn from the race, and can contain
additional metadata for election-specific information.

The Candidate model is designed to be:
- Immutable after creation (using Pydantic's frozen behavior)
- Serializable to/from dictionaries for data interchange
- Extensible through metadata for custom properties

Example:
    ```python
    from fresh_blt.models import Candidate

    # Create a regular candidate
    candidate = Candidate(
        id=1,
        name="Alice Johnson",
        withdrawn=False,
        meta={"party": "Independent", "age": 35}
    )

    # Create a withdrawn candidate
    withdrawn_candidate = Candidate(
        id=2,
        name="Bob Smith",
        withdrawn=True,
        meta={"withdrawal_reason": "Personal reasons"}
    )

    # Serialize and deserialize
    data = candidate.to_dict()
    restored = Candidate.from_dict(data)
    ```
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Candidate(BaseModel):
    """
    Represents a candidate participating in an election contest.

    A Candidate instance contains the basic information about a person or entity
    running in an election, including their unique identifier, name, withdrawal
    status, and extensible metadata for additional properties.

    Attributes:
        id: Unique integer identifier for the candidate. Must be positive and
           unique within an election context. Used for ballot rankings and
           result calculations.

        name: Human-readable full name of the candidate. Should be descriptive
            enough to clearly identify the candidate to election officials and voters.

        withdrawn: Boolean flag indicating whether the candidate has withdrawn
                  from the election. Withdrawn candidates are typically excluded
                  from final results but may still appear on ballots for auditing
                  purposes. Defaults to False.

        meta: Dictionary for storing additional candidate metadata such as
             party affiliation, contact information, biographical details, or
             any custom properties. This provides extensibility for election-
             specific information not covered by core attributes. Defaults to empty dict.

    Class Methods:
        from_dict: Create a Candidate instance from a dictionary representation.
                  Useful for deserializing from JSON, CSV, or other data formats.

    Instance Methods:
        to_dict: Convert the Candidate to a dictionary representation.
                Useful for serializing to JSON, CSV, or other data formats.

    Example:
        ```python
        # Create candidates for an election
        candidates = [
            Candidate(id=1, name="Alice Johnson", meta={"party": "Democrat"}),
            Candidate(id=2, name="Bob Smith", meta={"party": "Republican"}),
            Candidate(id=3, name="Charlie Brown", withdrawn=True,
                     meta={"party": "Independent", "withdrawal_date": "2024-10-15"})
        ]

        # Convert to dictionary for storage
        candidate_data = [c.to_dict() for c in candidates]

        # Restore from dictionary
        restored_candidates = [Candidate.from_dict(data) for data in candidate_data]
        ```

    Note:
        Candidates are typically referenced by their ID in ballot rankings rather
        than by name, ensuring that name changes or corrections don't break
        existing ballot data. The withdrawn status affects tabulation algorithms,
        which must handle withdrawn candidates appropriately (typically by
        transferring votes to next preferences).
    """

    id: int = Field(
        ...,
        description="Unique integer identifier for the candidate",
        gt=0,  # Must be positive
        examples=[1, 42, 100]
    )

    name: str = Field(
        ...,
        description="Human-readable full name of the candidate",
        examples=["Alice Johnson", "Bob Smith", "Dr. Charlie Brown"],
        min_length=1
    )

    withdrawn: bool = Field(
        default=False,
        description="Whether the candidate has withdrawn from the election"
    )

    meta: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional candidate metadata for extensibility",
        examples=[
            {"party": "Independent", "age": 35, "experience": "5 years"},
            {"withdrawal_reason": "Personal reasons", "withdrawal_date": "2024-10-15"}
        ]
    )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Candidate:
        """
        Create a Candidate instance from a dictionary representation.

        This method provides a convenient way to deserialize Candidate data
        from dictionaries, which is useful when loading from JSON files,
        CSV data, or other serialized formats.

        Args:
            data: Dictionary containing candidate data with required keys 'id' and 'name',
                 and optional keys 'withdrawn' and 'meta'. Missing optional keys will
                 use their default values.

        Returns:
            Candidate: A new Candidate instance with the provided data.

        Raises:
            KeyError: If required keys 'id' or 'name' are missing from the dictionary.
            ValidationError: If the data doesn't meet the Candidate model's validation rules.

        Example:
            ```python
            data = {
                "id": 1,
                "name": "Alice Johnson",
                "withdrawn": False,
                "meta": {"party": "Independent"}
            }
            candidate = Candidate.from_dict(data)
            ```

            ```python
            # Minimal data with only required fields
            minimal_data = {"id": 2, "name": "Bob Smith"}
            candidate = Candidate.from_dict(minimal_data)
            # withdrawn defaults to False, meta defaults to empty dict
            ```
        """
        return cls(
            id=data["id"],
            name=data["name"],
            withdrawn=data.get("withdrawn", False),
            meta=data.get("meta", {})
        )

    def __hash__(self) -> int:
        """
        Make Candidate instances hashable for use in sets and dictionaries.

        The hash is based on the candidate's ID since it's unique and immutable.

        Returns:
            int: Hash value based on the candidate's ID
        """
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another Candidate instance.

        Two candidates are considered equal if they have the same ID.

        Args:
            other: Object to compare with

        Returns:
            bool: True if the candidates are equal (same ID), False otherwise
        """
        if not isinstance(other, Candidate):
            return NotImplemented
        return self.id == other.id

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the Candidate instance to a dictionary representation.

        This method provides a convenient way to serialize Candidate data
        to dictionaries, which is useful for saving to JSON files, exporting
        to CSV, or transmitting over APIs.

        Returns:
            dict[str, Any]: Dictionary containing all candidate attributes with keys
                           'id', 'name', 'withdrawn', and 'meta'. All values are
                           directly serializable (strings, integers, booleans, dicts).

        Example:
            ```python
            candidate = Candidate(
                id=1,
                name="Alice Johnson",
                withdrawn=False,
                meta={"party": "Independent"}
            )

            data = candidate.to_dict()
            # Returns: {"id": 1, "name": "Alice Johnson", "withdrawn": False, "meta": {"party": "Independent"}}
            ```

            ```python
            # Useful for JSON serialization
            import json
            candidate_data = candidate.to_dict()
            json_string = json.dumps(candidate_data)
            ```
        """
        return {
            "id": self.id,
            "name": self.name,
            "withdrawn": self.withdrawn,
            "meta": self.meta,
        }
"""
Ballot model for .blt files.

This module defines the Ballot model, which represents a single voter's ranked
preferences in an election. Ballots support both ranked-choice voting (where
voters rank candidates in order of preference) and weighted voting systems.

The Ballot model is designed to handle:
- Ranked preferences with equal rankings (ties)
- Weighted ballots for proportional voting systems
- Serialization to/from dictionary formats
- Validation of ranking structures

Example:
    ```python
    from fresh_blt.models import Ballot, Candidate

    # Create candidates
    alice = Candidate(id=1, name="Alice")
    bob = Candidate(id=2, name="Bob")
    charlie = Candidate(id=3, name="Charlie")

    # Create a ballot with clear ranking: Alice > Bob > Charlie
    ballot1 = Ballot(
        rankings=[[alice], [bob], [charlie]],
        weight=1
    )

    # Create a ballot with tied preferences: Alice = Bob > Charlie
    ballot2 = Ballot(
        rankings=[[alice, bob], [charlie]],
        weight=1
    )

    # Create a weighted ballot (e.g., for delegate representation)
    weighted_ballot = Ballot(
        rankings=[[alice], [bob]],
        weight=5  # Represents 5 votes
    )
    ```
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field, field_validator

if TYPE_CHECKING:
    from .candidate import Candidate


class Ballot(BaseModel):
    """
    Represents a single ballot with voter rankings and weight.

    A Ballot instance captures a voter's ranked preferences in an election,
    supporting both strict rankings and equal rankings (ties), along with
    an optional weight for weighted voting systems.

    The ranking structure uses a list of lists where:
    - The outer list represents preference order (most preferred first)
    - Each inner list contains candidates ranked equally at that level
    - An empty inner list represents an exhausted ballot at that preference level

    Attributes:
        rankings: Ordered list of lists representing voter preferences. Each inner
                 list contains candidates ranked equally at that preference level.
                 The ballot is exhausted when all rankings are used or when an
                 empty list is encountered. This structure supports both strict
                 rankings and equal rankings (ties between candidates).

        weight: Positive integer representing the weight of the ballot in weighted
               voting systems. Must be > 0.

    Class Methods:
        from_dict: Create a Ballot instance from a dictionary representation.
                  Useful for deserializing from JSON, CSV, or other data formats.

    Example:
        ```python
        # Create candidates
        candidates = [
            Candidate(id=1, name="Alice"),
            Candidate(id=2, name="Bob"),
            Candidate(id=3, name="Charlie"),
            Candidate(id=4, name="Diana")
        ]
        alice, bob, charlie, diana = candidates

        # Strict ranking: Alice > Bob > Charlie > Diana
        strict_ballot = Ballot(
            rankings=[[alice], [bob], [charlie], [diana]],
            weight=1
        )

        # With ties: Alice = Bob > Charlie = Diana
        tied_ballot = Ballot(
            rankings=[[alice, bob], [charlie, diana]],
            weight=1
        )

        # Partial ranking: Alice > Bob (no preference for others)
        partial_ballot = Ballot(
            rankings=[[alice], [bob]],
            weight=1
        )

        # Weighted ballot (represents multiple votes)
        delegate_ballot = Ballot(
            rankings=[[alice], [bob]],
            weight=10  # Represents 10 delegate votes
        )
        ```
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
            [[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}], [{"id": 3, "name": "Charlie"}]]  # Alice = Bob > Charlie
        ]
    )

    weight: int = Field(
        default=1,
        gt=0,  # Must be greater than 0
        description=(
            "Weight of the ballot for weighted voting systems. Must be a positive integer."
        ),
        examples=[1, 5, 10, 100]
    )

    @field_validator('rankings')
    @classmethod
    def validate_rankings(cls, v: list[list[Candidate]]) -> list[list[Candidate]]:
        """
        Validate that rankings structure is well-formed.

        Ensures that:
        - Rankings structure is valid (allows empty rankings for exhausted preferences)
        - All candidates in rankings are unique across the entire ballot
        - Structure follows the expected list-of-lists format

        Args:
            v: The rankings value to validate

        Returns:
            The validated rankings

        Raises:
            ValueError: If rankings structure contains duplicate candidates
        """
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
        """
        Create a Ballot instance from a dictionary representation.

        Args:
            data: Dictionary containing ballot data with required key 'rankings'
                 and optional key 'weight'. The 'rankings' value should be a
                 list of lists containing candidate dictionaries or Candidate
                 instances. Missing 'weight' defaults to 1.

        Returns:
            Ballot: A new Ballot instance with the provided data.

        Raises:
            KeyError: If required key 'rankings' is missing from the dictionary.
            ValidationError: If the data doesn't meet the Ballot model's validation rules
                           (e.g., invalid weight, malformed rankings structure).
            ValueError: If rankings contains duplicate candidates or is otherwise invalid.

        Example:
            ```python
            # With candidate dictionaries
            data = {
                "rankings": [
                    [{"id": 1, "name": "Alice"}],
                    [{"id": 2, "name": "Bob"}]
                ],
                "weight": 1
            }
            ballot = Ballot.from_dict(data)

            # With Candidate instances (assuming candidates exist)
            ballot_data = {
                "rankings": [[alice], [bob]],
                "weight": 5
            }
            weighted_ballot = Ballot.from_dict(ballot_data)
            ```

            ```python
            # Minimal data with only required fields
            minimal_data = {
                "rankings": [[{"id": 1, "name": "Alice"}]]
            }
            ballot = Ballot.from_dict(minimal_data)
            # weight defaults to 1
            ```
        """
        # Validate required keys are present
        if "rankings" not in data:
            raise ValueError("Missing required key: 'rankings'")
        if "weight" not in data:
            raise ValueError("Missing required key: 'weight'")

        return cls(rankings=data["rankings"], weight=data["weight"])
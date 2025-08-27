"""
Election model for .blt format.

This module defines the Election model, which represents an election contest
containing candidates, ballots, and associated metadata. The model is designed
to work with ranked-choice voting systems and supports weighted ballots.

The Election model serves as the central container that:
- Defines the election's name and basic properties
- Contains all candidates participating in the election
- Stores all cast ballots with their rankings and weights
- Maintains metadata for additional election-specific information

Example:
    ```python
    from fresh_blt.models import Election, Candidate, Ballot

    # Create candidates
    candidate1 = Candidate(id=1, name="Alice", withdrawn=False)
    candidate2 = Candidate(id=2, name="Bob", withdrawn=False)

    # Create a ballot with rankings (Alice > Bob)
    ballot = Ballot(rankings=[[candidate1], [candidate2]], weight=1)

    # Create election
    election = Election(
        name="City Council Election",
        candidates=[candidate1, candidate2],
        ballots=[ballot],
        meta={"location": "City Hall", "date": "2024-11-05"}
    )
    ```
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .ballot import Ballot
    from .candidate import Candidate


class Election(BaseModel):
    """
    Represents an election contest with candidates, ballots, and metadata.

    An Election instance encapsulates all the information needed to conduct
    and analyze a ranked-choice voting election, including the candidates
    running, the ballots cast by voters, and additional metadata.

    Attributes:
        name: Human-readable name or title of the election contest.
             Should be descriptive enough to uniquely identify the election.

        ballots: List of all ballots cast in the election. Each ballot contains
                the voter's ranked preferences and an optional weight for
                weighted voting systems. Defaults to an empty list.

        candidates: List of all candidates participating in the election,
                   including withdrawn candidates. The order may be significant
                   for certain tabulation methods. Defaults to an empty list.

        meta: Dictionary for storing additional election metadata such as
             location, date, election type, or any custom properties.
             Defaults to an empty dict.

    Relationships:
        - One-to-many with Ballot: An election can have multiple ballots
        - One-to-many with Candidate: An election can have multiple candidates
        - Many-to-many through Ballot: Elections link candidates via ballot rankings

    Example:
        ```python
        # Create a simple election
        election = Election(
            name="Board Member Election",
            candidates=[
                Candidate(id=1, name="Alice"),
                Candidate(id=2, name="Bob"),
                Candidate(id=3, name="Charlie")
            ]
        )

        # Add ballots
        ballot1 = Ballot(rankings=[[alice], [bob]], weight=1)
        ballot2 = Ballot(rankings=[[bob], [alice]], weight=1)
        election.ballots.append(ballot1)
        election.ballots.append(ballot2)
        ```
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

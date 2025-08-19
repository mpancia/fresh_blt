import pytest

from fresh_blt.models.ballot import Ballot
from fresh_blt.models.candidate import Candidate
from fresh_blt.models.election import Election

# Rebuild Pydantic models to resolve forward references
Election.model_rebuild()
Ballot.model_rebuild()
Candidate.model_rebuild()


@pytest.fixture
def sample_election():
    # Create the election object first (candidates/ballots will reference it)
    election = Election(name="Sample Election")

    # Create candidates, referencing the election
    candidates = [
        Candidate(id=1, name="Alice", withdrawn=False, election=election),
        Candidate(id=2, name="Bob", withdrawn=False, election=election),
        Candidate(id=3, name="Carol", withdrawn=True, election=election),
        Candidate(id=4, name="Dave", withdrawn=False, election=election),
    ]
    election.candidates = candidates

    # Create ballots, referencing the election and candidates
    ballots = [
        Ballot(
            election=election,
            rankings=[
                [candidates[0]],  # Alice
                [candidates[1], candidates[3]],  # Bob = Dave
                [candidates[2]],  # Carol
            ],
            weight=2,
        ),
        Ballot(
            election=election,
            rankings=[
                [candidates[1]],  # Bob
                [candidates[0]],  # Alice
                [candidates[3]],  # Dave
            ],
            weight=1,
        ),
    ]
    election.ballots = ballots

    return election

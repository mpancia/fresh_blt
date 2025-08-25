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

    # Create candidates
    candidates = [
        Candidate(id=1, name="Alice", withdrawn=False),
        Candidate(id=2, name="Bob", withdrawn=False),
        Candidate(id=3, name="Carol", withdrawn=True),
        Candidate(id=4, name="Dave", withdrawn=False),
    ]
    election.candidates = candidates

    # Create ballots with candidates
    ballots = [
        Ballot(
            rankings=[
                [candidates[0]],  # Alice
                [candidates[1], candidates[3]],  # Bob = Dave
                [candidates[2]],  # Carol
            ],
            weight=2,
        ),
        Ballot(
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

import pytest
from faker import Faker

from fresh_blt.fixtures import BLTProvider
from fresh_blt.models.ballot import Ballot
from fresh_blt.models.candidate import Candidate
from fresh_blt.models.election import Election

# Rebuild Pydantic models to resolve forward references
Election.model_rebuild()
Ballot.model_rebuild()
Candidate.model_rebuild()


@pytest.fixture
def faker():
    """Faker instance with BLT provider for testing."""
    faker = Faker()
    faker.seed_instance(42)  # Reproducible tests
    faker.add_provider(BLTProvider)
    return faker


@pytest.fixture
def sample_election(faker):
    """Generate a sample election for testing using Faker."""
    return faker.election_object(
        faker.election(
            num_candidates=4,
            num_ballots=2,
            withdrawn_rate=0.25  # One candidate will be withdrawn
        )
    )


@pytest.fixture
def predictable_election(faker):
    """Generate a predictable election for consistent testing."""
    faker.seed_instance(12345)  # Fixed seed for predictable results

    # Create a specific election structure for testing
    election_data = {
        'name': 'Test Election',
        'candidates': [
            {'id': 1, 'name': 'Alice', 'withdrawn': False},
            {'id': 2, 'name': 'Bob', 'withdrawn': False},
            {'id': 3, 'name': 'Carol', 'withdrawn': True},  # Withdrawn candidate
            {'id': 4, 'name': 'Dave', 'withdrawn': False},
        ],
        'ballots': [
            {
                'weight': 2,
                'rankings': [
                    [{'id': 1, 'name': 'Alice'}],  # Alice
                    [{'id': 2, 'name': 'Bob'}, {'id': 4, 'name': 'Dave'}],  # Bob = Dave
                    [{'id': 3, 'name': 'Carol'}],  # Carol
                ]
            },
            {
                'weight': 1,
                'rankings': [
                    [{'id': 2, 'name': 'Bob'}],  # Bob
                    [{'id': 1, 'name': 'Alice'}],  # Alice
                    [{'id': 4, 'name': 'Dave'}],  # Dave
                ]
            }
        ],
        'num_seats': 1
    }

    return faker.election_object(election_data)


@pytest.fixture
def small_election(faker):
    """Generate a small election (3 candidates, 5 ballots)."""
    return faker.election_object(
        faker.election(num_candidates=3, num_ballots=5)
    )


@pytest.fixture
def large_election(faker):
    """Generate a larger election for comprehensive testing."""
    return faker.election_object(
        faker.election(num_candidates=6, num_ballots=20)
    )


@pytest.fixture
def withdrawn_election(faker):
    """Generate an election with withdrawn candidates."""
    return faker.election_object(
        faker.election(num_candidates=5, num_ballots=10, withdrawn_rate=0.4)
    )


@pytest.fixture
def blt_content(faker):
    """Generate BLT file content for testing."""
    return faker.blt_content()


@pytest.fixture
def election_data(faker):
    """Generate raw election data dictionary."""
    return faker.election(num_candidates=4, num_ballots=5)

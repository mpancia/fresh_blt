import tempfile
from pathlib import Path

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
    """Faker instance with .blt provider for testing."""
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
            withdrawn_rate=0.25,  # One candidate will be withdrawn
        )
    )


@pytest.fixture
def predictable_election(faker):
    """Generate a predictable election for consistent testing."""
    faker.seed_instance(12345)  # Fixed seed for predictable results

    # Create a specific election structure for testing
    election_data = {
        "name": "Test Election",
        "candidates": [
            {"id": 1, "name": "Alice", "withdrawn": False},
            {"id": 2, "name": "Bob", "withdrawn": False},
            {"id": 3, "name": "Carol", "withdrawn": True},
            {"id": 4, "name": "Dave", "withdrawn": False},
        ],
        "ballots": [
            {
                "weight": 2,
                "rankings": [
                    [{"id": 1, "name": "Alice"}],
                    [{"id": 2, "name": "Bob"}, {"id": 4, "name": "Dave"}],
                    [{"id": 3, "name": "Carol"}],
                ],
            },
            {
                "weight": 1,
                "rankings": [
                    [{"id": 2, "name": "Bob"}],
                    [{"id": 1, "name": "Alice"}],
                    [{"id": 4, "name": "Dave"}],
                ],
            },
        ],
        "num_seats": 1,
    }

    return faker.election_object(election_data)


@pytest.fixture
def small_election(faker):
    """Generate a small election (3 candidates, 5 ballots)."""
    return faker.election_object(faker.election(num_candidates=3, num_ballots=5))


@pytest.fixture
def large_election(faker):
    """Generate a larger election for comprehensive testing."""
    return faker.election_object(faker.election(num_candidates=6, num_ballots=20))


@pytest.fixture
def withdrawn_election(faker):
    """Generate an election with withdrawn candidates."""
    return faker.election_object(
        faker.election(num_candidates=5, num_ballots=10, withdrawn_rate=0.4)
    )


@pytest.fixture
def blt_content(faker):
    """Generate .blt file content for testing."""
    return faker.blt_content()


@pytest.fixture
def election_data(faker):
    """Generate raw election data dictionary."""
    return faker.election(num_candidates=4, num_ballots=5)


# Temporary .blt file fixtures for CLI testing
@pytest.fixture
def valid_blt_file(faker):
    """Create a temporary valid .blt file with 4 candidates (one withdrawn)."""
    election_data = faker.election(
        num_candidates=4, num_ballots=8, withdrawn_rate=0.25, num_seats=2
    )
    blt_content = faker.blt_content(election_data)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".blt", delete=False) as f:
        f.write(blt_content)
        temp_path = Path(f.name)

    yield temp_path
    temp_path.unlink()


@pytest.fixture
def valid_blt_no_withdrawn_file(faker):
    """Create a temporary valid .blt file with 4 candidates (no withdrawn)."""
    election_data = faker.election(num_candidates=4, num_ballots=6, withdrawn_rate=0.0, num_seats=1)
    blt_content = faker.blt_content(election_data)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".blt", delete=False) as f:
        f.write(blt_content)
        temp_path = Path(f.name)

    yield temp_path
    temp_path.unlink()


@pytest.fixture
def invalid_blt_file():
    """Create a temporary invalid .blt file for error testing."""
    invalid_content = "This is not a valid BLT file\nJust some random text\n123\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".blt", delete=False) as f:
        f.write(invalid_content)
        temp_path = Path(f.name)

    yield temp_path
    temp_path.unlink()  # Cleanup


# Temporary .blt file fixtures for grammar testing
@pytest.fixture
def grammar_blt_content_withdrawn():
    """Create .blt content for grammar testing with withdrawn candidates."""
    blt_content = """4 2
-2
3 1 3 4 0
4 1 3 2 0
2 4 1=3 0
1 2 0
2 2=4=3 1 0
1 3 4 2 0
0
"Adam"
"Basil"
"Charlotte"
"Donald"
"Cool Election"
"""
    return blt_content


@pytest.fixture
def grammar_blt_content_no_withdrawn():
    """Create .blt content for grammar testing without withdrawn candidates."""
    blt_content = """4 2
3 1 3 4 0
4 1 3 2 0
2 4 1=3 0
1 2 0
2 2=4=3 1 0
1 3 4 2 0
0
"Adam"
"Basil"
"Charlotte"
"Donald"
"Cool Election"
"""
    return blt_content


@pytest.fixture
def grammar_blt_content_no_zero_terminators():
    """Create .blt content for grammar testing without zero terminators."""
    blt_content = """4 2
-2
3 1 3 4
4 1 3 2
2 4 1=3
1 2
2 2=4=3 1
1 3 4 2
0
"Adam"
"Basil"
"Charlotte"
"Donald"
"Cool Election"
"""
    return blt_content


@pytest.fixture
def grammar_blt_file_withdrawn(grammar_blt_content_withdrawn):
    """Create temporary .blt file with withdrawn candidates for grammar testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".blt", delete=False) as f:
        f.write(grammar_blt_content_withdrawn)
        temp_path = Path(f.name)

    yield temp_path
    temp_path.unlink()


@pytest.fixture
def grammar_blt_file_no_withdrawn(grammar_blt_content_no_withdrawn):
    """Create temporary .blt file without withdrawn candidates for grammar testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".blt", delete=False) as f:
        f.write(grammar_blt_content_no_withdrawn)
        temp_path = Path(f.name)

    yield temp_path
    temp_path.unlink()


@pytest.fixture
def grammar_blt_file_no_zero_terminators(grammar_blt_content_no_zero_terminators):
    """Create temporary .blt file without zero terminators for grammar testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".blt", delete=False) as f:
        f.write(grammar_blt_content_no_zero_terminators)
        temp_path = Path(f.name)

    yield temp_path
    temp_path.unlink()

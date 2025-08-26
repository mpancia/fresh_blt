"""
Pytest fixtures for BLT testing.

This module provides pytest fixtures that can be used across test files
for generating BLT test data.
"""

import pytest
from faker import Faker

from fresh_blt.fixtures import BLTProvider


@pytest.fixture
def blt_faker():
    """Faker instance with BLT provider."""
    faker = Faker()
    faker.add_provider(BLTProvider)
    return faker


@pytest.fixture
def sample_blt(blt_faker):
    """Generate a sample BLT file content."""
    pass  # Implementation will go here


@pytest.fixture
def sample_election(blt_faker):
    """Generate a sample election object."""
    pass  # Implementation will go here


@pytest.fixture
def small_election(blt_faker):
    """Generate a small election (3-4 candidates, 20-50 ballots)."""
    pass  # Implementation will go here


@pytest.fixture
def large_election(blt_faker):
    """Generate a large election (5-8 candidates, 100-500 ballots)."""
    pass  # Implementation will go here


@pytest.fixture
def close_race(blt_faker):
    """Generate an election with close results."""
    pass  # Implementation will go here


@pytest.fixture
def multi_seat_election(blt_faker):
    """Generate a multi-seat election."""
    pass  # Implementation will go here


# Seeded fixtures for reproducible tests
@pytest.fixture
def blt_faker_seeded():
    """Faker instance with BLT provider and fixed seed."""
    faker = Faker()
    faker.seed_instance(42)  # Fixed seed for reproducible tests
    faker.add_provider(BLTProvider)
    return faker


@pytest.fixture
def reproducible_election(blt_faker_seeded):
    """Generate a reproducible election for consistent testing."""
    pass  # Implementation will go here
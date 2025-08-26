# BLT Fixtures

This module provides Faker providers and generators for creating BLT (Ballot Transmission Language) files for testing and development.

## Overview

The fixtures module contains:

- **`blt_provider.py`**: Main Faker provider for generating BLT content and election data
- **`generators.py`**: High-level generators for common election scenarios

## Quick Start

```python
from faker import Faker
from fresh_blt.fixtures import BLTProvider

# Create faker instance with BLT provider
faker = Faker()
faker.add_provider(BLTProvider)

# Generate BLT content
blt_content = faker.blt_content()

# Generate election object
election = faker.election_object()

# Save to file
faker.blt_file("test_election.blt")
```

## Using Generators

```python
from fresh_blt.fixtures import BLTGenerators

gen = BLTGenerators(seed=42)

# Generate different types of elections
small_blt = gen.small_election()
large_blt = gen.large_election()
close_race = gen.close_race()

# Generate multiple files
files = gen.batch_generate(count=5)
```


## Pytest Integration

```python
# tests/test_blt_generation.py
def test_blt_generation(sample_blt):
    """Test BLT content generation."""
    assert isinstance(sample_blt, str)
    assert len(sample_blt.split('\n')) > 5

def test_election_object(sample_election):
    """Test election object generation."""
    assert sample_election.name
    assert len(sample_election.candidates) >= 3
    assert len(sample_election.ballots) >= 10
```

## Available Methods

### BLTProvider Methods

- `election_name()` - Generate realistic election name
- `candidate()` - Generate single candidate
- `candidates()` - Generate list of candidates
- `ballot()` - Generate single ballot
- `ballots()` - Generate multiple ballots
- `election()` - Generate complete election data
- `blt_content()` - Generate BLT file content
- `blt_file()` - Generate and save BLT file
- `election_object()` - Generate Election model instance

### BLTGenerators Methods

- `small_election()` - Small election (3-4 candidates)
- `large_election()` - Large election (5-8 candidates)
- `close_race()` - Election with close results
- `multi_seat_election()` - Multi-seat election
- `batch_generate()` - Generate multiple files
- `generate_withdrawn_candidates()` - Election with withdrawn candidates


## Installation Requirements

```bash
pip install faker pytest
```

## Configuration

### Seeding for Reproducible Tests

```python
faker = Faker()
faker.seed_instance(42)  # For reproducible results
faker.add_provider(BLTProvider)
```

### Custom Election Parameters

```python
# Generate election with specific parameters
election_data = faker.election(
    num_candidates=6,
    num_ballots=100,
    withdrawn_rate=0.2,
    num_seats=3
)
```

## Examples

See the examples directory for complete usage examples.
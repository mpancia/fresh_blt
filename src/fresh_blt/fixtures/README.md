# .blt Fixtures

This module provides Faker providers and generators for creating .blt files and election data for testing and development.

## Overview

The fixtures module contains:

- **`blt_provider.py`**: Main Faker provider for generating blt content and election data
- **`generators.py`**: High-level generators for common election scenarios

## Quick Start

```python
from faker import Faker
from fresh_blt.fixtures import BLTProvider

# Create faker instance with blt provider
faker = Faker()
faker.add_provider(BLTProvider)

# Generate blt content
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
    """Test .blt content generation."""
    assert isinstance(sample_blt, str)
    assert len(sample_blt.split('\n')) > 5

def test_election_object(sample_election):
    """Test election object generation."""
    assert sample_election.name
    assert len(sample_election.candidates) >= 3
    assert len(sample_election.ballots) >= 10
```
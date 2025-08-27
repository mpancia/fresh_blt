"""
High-level generators for common election scenarios.

This module provides convenient generators for specific types of elections.
"""

from faker import Faker

from .blt_provider import BLTProvider


class BLTGenerators:
    """Collection of generators for specific election scenarios."""

    def __init__(self, faker=None, seed: int | None = None):
        self.faker = faker
        if seed:
            pass  # Set seed if provided

    def small_election(self) -> str:
        """Generate a small 3-4 candidate election."""
        return self.faker.blt_content(self.faker.election(num_candidates=4, num_ballots=25))

    def large_election(self) -> str:
        """Generate a large election with many candidates and ballots."""
        return self.faker.blt_content(self.faker.election(num_candidates=8, num_ballots=150))

    def close_race(self) -> str:
        """Generate an election with close results."""
        return self.faker.blt_content(self.faker.close_election(num_candidates=5, num_ballots=100))

    def multi_seat_election(self, num_seats: int = 3) -> str:
        """Generate a multi-seat election."""
        return self.faker.blt_content(
            self.faker.election(num_candidates=6, num_ballots=80, num_seats=num_seats)
        )

    def batch_generate(self, count: int, pattern: str = "test_election_{}.blt") -> list[str]:
        """Generate multiple .blt files."""
        files = []
        for i in range(count):
            filename = pattern.format(i + 1)
            self.faker.blt_file(filename)
            files.append(filename)
        return files

    def generate_withdrawn_candidates(self, withdrawn_count: int) -> str:
        """Generate election with specific number of withdrawn candidates."""
        num_candidates = max(withdrawn_count + 2, 4)  # At least 2 active
        withdrawn_rate = withdrawn_count / num_candidates

        return self.faker.blt_content(
            self.faker.election(num_candidates=num_candidates, withdrawn_rate=withdrawn_rate)
        )


# Convenience functions
def generate_small_election(seed: int | None = None) -> str:
    """Convenience function for small election generation."""
    faker = Faker()
    if seed:
        faker.seed_instance(seed)
    faker.add_provider(BLTProvider)
    return faker.blt_content(faker.election(num_candidates=4, num_ballots=25))


def generate_test_election(
    num_candidates: int = 4, num_ballots: int = 50, seed: int | None = None
) -> str:
    """Convenience function for test election generation."""
    faker = Faker()
    if seed:
        faker.seed_instance(seed)
    faker.add_provider(BLTProvider)
    return faker.blt_content(faker.election(num_candidates=num_candidates, num_ballots=num_ballots))

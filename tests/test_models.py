"""
Tests for the models module.

This module contains comprehensive tests for the Election, Candidate, and Ballot models,
organized by component using test classes for better maintainability and structure.
"""

import pytest

from fresh_blt.models.ballot import Ballot
from fresh_blt.models.candidate import Candidate


class TestElection:
    """Test cases for Election model functionality."""

    def test_election_creation(self, sample_election):
        """Test that election is created with correct basic attributes."""
        assert sample_election.name == "Sample Election"
        assert len(sample_election.candidates) == 4
        assert len(sample_election.ballots) == 2

    def test_election_candidates(self, sample_election):
        """Test election candidates have correct names and count."""
        names = {c.name for c in sample_election.candidates}
        assert names == {"Alice", "Bob", "Carol", "Dave"}

    def test_election_candidate_uniqueness(self, sample_election):
        """Test that all candidates have unique IDs."""
        ids = [c.id for c in sample_election.candidates]
        assert len(ids) == len(set(ids))


class TestCandidate:
    """Test cases for Candidate model functionality."""

    def test_candidate_attributes(self, sample_election):
        """Test that all candidates have required attributes."""
        for candidate in sample_election.candidates:
            assert hasattr(candidate, 'id')
            assert hasattr(candidate, 'name')
            assert hasattr(candidate, 'withdrawn')
            assert isinstance(candidate.id, int)
            assert isinstance(candidate.name, str)
            assert isinstance(candidate.withdrawn, bool)

    def test_candidate_withdrawn_status(self, sample_election):
        """Test candidate withdrawn status (only Carol should be withdrawn)."""
        carol = next(c for c in sample_election.candidates if c.name == "Carol")
        assert carol.withdrawn is True

        # All other candidates should not be withdrawn
        for candidate in sample_election.candidates:
            if candidate.name != "Carol":
                assert candidate.withdrawn is False

    def test_candidate_creation_from_dict(self):
        """Test Candidate.from_dict method with valid data."""
        data = {
            "id": 1,
            "name": "Test Candidate",
            "withdrawn": False,
            "meta": {"extra": "data"}
        }
        candidate = Candidate.from_dict(data)

        assert candidate.id == 1
        assert candidate.name == "Test Candidate"
        assert candidate.withdrawn is False
        assert candidate.meta == {"extra": "data"}

    def test_candidate_creation_from_dict_with_defaults(self):
        """Test Candidate.from_dict method with minimal data (uses defaults)."""
        data = {"id": 2, "name": "Minimal Candidate"}
        candidate = Candidate.from_dict(data)

        assert candidate.id == 2
        assert candidate.name == "Minimal Candidate"
        assert candidate.withdrawn is False  # Default value
        assert candidate.meta == {}  # Default value


class TestBallot:
    """Test cases for Ballot model functionality."""

    def test_ballot_attributes(self, sample_election):
        """Test that all ballots have required attributes with correct types."""
        for ballot in sample_election.ballots:
            assert hasattr(ballot, 'rankings')
            assert hasattr(ballot, 'weight')
            assert isinstance(ballot.rankings, list)
            assert isinstance(ballot.weight, int)
            assert ballot.weight > 0

    def test_ballot_rankings_structure(self, sample_election):
        """Test ballot rankings structure and content."""
        # Test first ballot: Alice > (Bob=Dave) > Carol, weight=2
        ballot1 = sample_election.ballots[0]
        assert ballot1.weight == 2
        assert len(ballot1.rankings) == 3

        # Check ranking names
        ranking_names = [[c.name for c in rank] for rank in ballot1.rankings]
        assert ranking_names == [["Alice"], ["Bob", "Dave"], ["Carol"]]

        # Test second ballot: Bob > Alice > Dave, weight=1
        ballot2 = sample_election.ballots[1]
        assert ballot2.weight == 1
        assert len(ballot2.rankings) == 3

        ranking_names = [[c.name for c in rank] for rank in ballot2.rankings]
        assert ranking_names == [["Bob"], ["Alice"], ["Dave"]]

    def test_ballot_rankings_sets(self, sample_election):
        """Test ballot rankings using sets for unordered comparison within ranks."""
        ballot = sample_election.ballots[0]
        ranking_sets = [set(c.name for c in rank) for rank in ballot.rankings]
        expected = [{"Alice"}, {"Bob", "Dave"}, {"Carol"}]
        assert ranking_sets == expected

    def test_ballot_candidate_references(self, sample_election):
        """Test that all candidates referenced in ballot rankings exist in election."""
        all_candidate_names = {c.name for c in sample_election.candidates}

        for ballot in sample_election.ballots:
            for rank in ballot.rankings:
                for candidate in rank:
                    assert candidate.name in all_candidate_names

    def test_ballot_creation_from_dict_valid_data(self, sample_election):
        """Test Ballot.from_dict method with valid data."""
        alice = next(c for c in sample_election.candidates if c.name == "Alice")
        bob = next(c for c in sample_election.candidates if c.name == "Bob")

        data = {
            "rankings": [[alice], [bob]],
            "weight": 3
        }
        ballot = Ballot.from_dict(data)

        assert len(ballot.rankings) == 2
        assert ballot.rankings[0][0] == alice
        assert ballot.rankings[1][0] == bob
        assert ballot.weight == 3

    def test_ballot_creation_from_dict_missing_rankings(self):
        """Test Ballot.from_dict method raises error when rankings key is missing."""
        data = {"weight": 1}  # Missing rankings

        with pytest.raises(ValueError, match="Missing required key: 'rankings'"):
            Ballot.from_dict(data)

    def test_ballot_creation_from_dict_missing_weight(self):
        """Test Ballot.from_dict method raises error when weight key is missing."""
        data = {"rankings": []}  # Missing weight

        with pytest.raises(ValueError, match="Missing required key: 'weight'"):
            Ballot.from_dict(data)

    def test_ballot_creation_from_dict_invalid_weight_zero(self):
        """Test Ballot.from_dict method rejects zero weight."""
        data = {"rankings": [], "weight": 0}

        # Pydantic will raise a validation error for weight <= 0
        with pytest.raises(ValueError, match="weight"):
            Ballot.from_dict(data)

    def test_ballot_creation_from_dict_invalid_weight_negative(self):
        """Test Ballot.from_dict method rejects negative weight."""
        data = {"rankings": [], "weight": -1}

        # Pydantic will raise a validation error for weight <= 0
        with pytest.raises(ValueError, match="weight"):
            Ballot.from_dict(data)

    def test_ballot_creation_from_dict_empty_rankings(self):
        """Test Ballot.from_dict method accepts empty rankings."""
        data = {"rankings": [], "weight": 1}
        ballot = Ballot.from_dict(data)

        assert ballot.rankings == []
        assert ballot.weight == 1

    def test_ballot_creation_from_dict_empty_nested_rankings(self):
        """Test Ballot.from_dict method with empty nested rankings."""
        data = {"rankings": [[], []], "weight": 1}
        ballot = Ballot.from_dict(data)

        assert len(ballot.rankings) == 2
        assert ballot.rankings == [[], []]
        assert ballot.weight == 1
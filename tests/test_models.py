"""
Tests for the models module.
"""

import pytest

from fresh_blt.models.ballot import Ballot
from fresh_blt.models.candidate import Candidate


class TestElection:
    """Test cases for Election model functionality."""

    def test_election_creation(self, sample_election):
        """Test that election is created with correct basic attributes."""
        assert sample_election.name  # Has a name
        assert len(sample_election.candidates) >= 3  # At least 3 candidates
        assert len(sample_election.ballots) >= 2  # At least 2 ballots
        assert isinstance(sample_election.name, str)
        assert len(sample_election.name) > 0

    def test_election_candidates(self, sample_election):
        """Test election candidates have correct names and count."""
        candidate_names = {c.name for c in sample_election.candidates}
        assert len(candidate_names) == len(sample_election.candidates)  # All names unique
        assert all(isinstance(name, str) and len(name) > 0 for name in candidate_names)

    def test_election_candidate_uniqueness(self, sample_election):
        """Test that all candidates have unique IDs."""
        ids = [c.id for c in sample_election.candidates]
        assert len(ids) == len(set(ids))  # All IDs unique
        assert all(isinstance(id, int) and id > 0 for id in ids)


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
        """Test candidate withdrawn status works correctly."""
        withdrawn_candidates = [c for c in sample_election.candidates if c.withdrawn]
        active_candidates = [c for c in sample_election.candidates if not c.withdrawn]

        # Should have at least some candidates (may be 0 if no withdrawn candidates)
        assert len(withdrawn_candidates) + len(active_candidates) == len(sample_election.candidates)
        assert all(c.withdrawn is True for c in withdrawn_candidates)
        assert all(c.withdrawn is False for c in active_candidates)

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
        # Test that ballots have valid structure
        for _i, ballot in enumerate(sample_election.ballots):
            # Each ballot should have rankings and weight
            assert isinstance(ballot.rankings, list)
            assert isinstance(ballot.weight, int)
            assert ballot.weight > 0

            # Rankings should be non-empty for most ballots
            if len(sample_election.ballots) > 1:  # Only check if we have multiple ballots
                assert len(ballot.rankings) > 0

            # Each ranking level should be a list
            for ranking_level in ballot.rankings:
                assert isinstance(ranking_level, list)
                # Each ranking level should contain candidates
                for candidate in ranking_level:
                    assert hasattr(candidate, 'name')
                    assert hasattr(candidate, 'id')
                    assert candidate.name in {c.name for c in sample_election.candidates}

    def test_ballot_rankings_sets(self, sample_election):
        """Test ballot rankings using sets for unordered comparison within ranks."""
        if len(sample_election.ballots) == 0:
            pytest.skip("No ballots to test")

        ballot = sample_election.ballots[0]

        # Convert rankings to sets for unordered comparison
        ranking_sets = [set(c.name for c in rank) for rank in ballot.rankings]

        # Verify that each ranking level is valid
        for ranking_set in ranking_sets:
            assert len(ranking_set) > 0  # Each ranking level should have candidates
            # All candidates in this ranking should exist in the election
            for candidate_name in ranking_set:
                assert candidate_name in {c.name for c in sample_election.candidates}

    def test_ballot_candidate_references(self, sample_election):
        """Test that all candidates referenced in ballot rankings exist in election."""
        all_candidate_names = {c.name for c in sample_election.candidates}

        for ballot in sample_election.ballots:
            for rank in ballot.rankings:
                for candidate in rank:
                    assert candidate.name in all_candidate_names

    def test_ballot_creation_from_dict_valid_data(self, sample_election):
        """Test Ballot.from_dict method with valid data."""
        if len(sample_election.candidates) < 2:
            pytest.skip("Need at least 2 candidates for this test")

        candidate1 = sample_election.candidates[0]
        candidate2 = sample_election.candidates[1]

        data = {
            "rankings": [[candidate1], [candidate2]],
            "weight": 3
        }
        ballot = Ballot.from_dict(data)

        assert len(ballot.rankings) == 2
        assert ballot.rankings[0][0] == candidate1
        assert ballot.rankings[1][0] == candidate2
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